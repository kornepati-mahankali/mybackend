from flask import Flask, request, jsonify, send_file
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import subprocess
import threading
import time
import os
import sys
import json
import glob
from datetime import datetime
import shutil
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
import uuid
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from scrapers.search import run_eproc_scraper_with_bot

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

def send_log_to_frontend(message):
    socketio.emit('scraping_log', {'message': message})

# Global variables to track scraping status
scraping_process = None
scraping_active = False
current_session_id = None

# Configuration
OUTPUT_BASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'outputs', 'eproc')
if not os.path.exists(OUTPUT_BASE_DIR):
    os.makedirs(OUTPUT_BASE_DIR)

pending_eproc_sessions = {}

def build_advanced_search_url(base_url):
    parsed = urlparse(base_url)
    qs = parse_qs(parsed.query)
    qs['page'] = ['FrontEndAdvancedSearch']
    qs['service'] = ['page']
    new_query = urlencode(qs, doseq=True)
    return urlunparse(parsed._replace(query=new_query))

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'scraping_active': scraping_active,
        'server': 'eproc_server_fixed.py'
    })

@app.route('/api/test-url', methods=['POST'])
def test_url():
    """Test URL processing endpoint"""
    try:
        data = request.get_json()
        url = data.get('url', '')
        
        if not url:
            return jsonify({'error': 'URL is required'}), 400
        
        # Clean and validate the URL
        url = url.strip()
        
        # If URL doesn't start with http/https, add https://
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        # For E-Procurement sites, ensure we have the correct search page
        # Check if it's an E-Procurement site (contains nicgep/app or similar patterns)
        is_eprocurement_site = any(pattern in url.lower() for pattern in ['nicgep/app', 'eprocurement', 'tenders', '.gov.in'])
        
        original_url = url
        if is_eprocurement_site and "FrontEndAdvancedSearch" not in url:
            # Check if URL already has query parameters
            if '?' in url:
                url += '&page=FrontEndAdvancedSearch&service=page'
            else:
                url += '?page=FrontEndAdvancedSearch&service=page'
        
        return jsonify({
            'original_url': original_url,
            'processed_url': url,
            'is_eprocurement_site': is_eprocurement_site,
            'has_search_params': "FrontEndAdvancedSearch" in url,
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/open-edge', methods=['POST'])
def open_edge():
    try:
        data = request.get_json()
        url = build_advanced_search_url(data.get('url', ''))
        print(f"[DEBUG] Final Edge URL: {url}")

        edge_driver_path = r'D:\lavangam\lavangam\backend\scrapers\edgedriver_win64\msedgedriver.exe'
        if not os.path.exists(edge_driver_path):
            return jsonify({'error': 'Edge WebDriver not found!'}), 500

        options = Options()
        # options.add_argument('--user-data-dir=...')  # Optional: use a persistent profile

        service = Service(executable_path=edge_driver_path)
        bot = webdriver.Edge(service=service, options=options)
        print(f"[DEBUG] Navigating Edge to: {url}")
        bot.get(url)

        session_id = str(uuid.uuid4())
        pending_eproc_sessions[session_id] = bot
        print(f"[DEBUG] Edge opened, session_id: {session_id}")
        return jsonify({'message': 'Edge opened successfully', 'session_id': session_id, 'url': url}), 200
    except Exception as e:
        print(f"[ERROR] Failed to open Edge: {e}")
        return jsonify({'error': f'Failed to open Edge: {e}'}), 500

@app.route('/api/start-eproc-scraping', methods=['POST'])
def start_eproc_scraping():
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        if not session_id:
            return jsonify({'error': 'Session ID is required. Please open Edge first.'}), 400
        bot = pending_eproc_sessions.get(session_id)
        if not bot:
            return jsonify({'error': 'Session not found. Please open Edge first.'}), 400
        print(f"[DEBUG] Using existing Edge session: {session_id}")
        url = build_advanced_search_url(data.get('base_url', ''))
        print(f"[DEBUG] Start scraping with URL: {url}")

        # Call the real scraper!
        run_eproc_scraper_with_bot(
            bot=bot,
            tender_type=data.get('tender_type', ''),
            days_interval=data.get('days_interval', 7),
            start_page=data.get('start_page', 1),
            captcha=data.get('captcha', None),
            log_callback=send_log_to_frontend
        )

        bot.quit()
        del pending_eproc_sessions[session_id]
        return jsonify({'message': 'Scraping completed successfully!'}), 200
    except Exception as e:
        print(f"[ERROR] Failed to start scraping: {e}")
        return jsonify({'error': f'Failed to start scraping: {e}'}), 500

def run_scraping(data, session_id):
    """Run the E-Procurement scraping script"""
    global scraping_process, scraping_active
    
    try:
        # Get the directory where this script is located
        current_dir = os.path.dirname(os.path.abspath(__file__))
        scraper_path = os.path.join(current_dir, 'scrapers', 'search.py')
        
        # Create session-specific output directory
        session_output_dir = os.path.join(OUTPUT_BASE_DIR, session_id)
        if not os.path.exists(session_output_dir):
            os.makedirs(session_output_dir)
        
        # Prepare command line arguments
        cmd = [
            sys.executable,  # Python executable
            scraper_path,
            '--base_url', data['base_url'],
            '--tender_type', data['tender_type'],
            '--days_interval', str(data['days_interval']),
            '--start_page', str(data['start_page']),
            '--captcha', data['captcha']
        ]
        
        socketio.emit('scraping_log', {'message': f'📋 Running command: {" ".join(cmd)}'})
        
        # Start the scraping process
        scraping_process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1,
            cwd=current_dir
        )
        
        # Read output in real-time
        for line in iter(scraping_process.stdout.readline, ''):
            if line:
                # Clean the line and emit as log
                clean_line = line.strip()
                if clean_line:
                    socketio.emit('scraping_log', {'message': clean_line})
                    
                    # Check for completion or error indicators
                    if 'SCRAPING COMPLETED' in clean_line or 'COMPLETED' in clean_line:
                        socketio.emit('scraping_complete', {
                            'success': True,
                            'message': '✅ E-Procurement scraping completed successfully!',
                            'session_id': session_id,
                            'timestamp': datetime.now().isoformat()
                        })
                        break
                    elif 'ERROR' in clean_line.upper() or 'FAILED' in clean_line.upper():
                        socketio.emit('scraping_error', {
                            'error': clean_line,
                            'session_id': session_id,
                            'timestamp': datetime.now().isoformat()
                        })
                        break
        
        # Wait for process to complete
        return_code = scraping_process.wait()
        
        if return_code == 0:
            # Move generated files to session directory
            move_generated_files(session_id)
            
            socketio.emit('scraping_complete', {
                'success': True,
                'message': '✅ E-Procurement scraping completed successfully!',
                'session_id': session_id,
                'timestamp': datetime.now().isoformat()
            })
        else:
            socketio.emit('scraping_error', {
                'error': f'Scraping process exited with code {return_code}',
                'session_id': session_id,
                'timestamp': datetime.now().isoformat()
            })
            
    except Exception as e:
        error_msg = f'Error during scraping: {str(e)}'
        socketio.emit('scraping_error', {
            'error': error_msg,
            'session_id': session_id,
            'timestamp': datetime.now().isoformat()
        })
    finally:
        scraping_active = False
        scraping_process = None

def move_generated_files(session_id):
    """Move generated Excel files to session directory"""
    try:
        # Look for Excel files in the scrapers/OUTPUT directory
        scraper_output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'scrapers', 'OUTPUT')
        session_output_dir = os.path.join(OUTPUT_BASE_DIR, session_id)
        
        if os.path.exists(scraper_output_dir):
            excel_files = glob.glob(os.path.join(scraper_output_dir, '*.xlsx'))
            for file_path in excel_files:
                filename = os.path.basename(file_path)
                new_path = os.path.join(session_output_dir, filename)
                shutil.move(file_path, new_path)
                socketio.emit('scraping_log', {'message': f'📁 Moved file: {filename}'})
        
        # Also check for files in the scrapers directory
        scrapers_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'scrapers')
        excel_files = glob.glob(os.path.join(scrapers_dir, '*.xlsx'))
        for file_path in excel_files:
            filename = os.path.basename(file_path)
            new_path = os.path.join(session_output_dir, filename)
            shutil.move(file_path, new_path)
            socketio.emit('scraping_log', {'message': f'📁 Moved file: {filename}'})
            
    except Exception as e:
        socketio.emit('scraping_log', {'message': f'⚠️ Warning: Could not move files: {str(e)}'})

@app.route('/api/stop-scraping', methods=['POST'])
def stop_scraping():
    """Stop the current scraping process"""
    global scraping_process, scraping_active
    
    try:
        if scraping_process and scraping_active:
            scraping_process.terminate()
            scraping_active = False
            socketio.emit('scraping_log', {'message': '🛑 Scraping stopped by user'})
            return jsonify({'message': 'Scraping stopped successfully'}), 200
        else:
            return jsonify({'message': 'No active scraping process'}), 200
            
    except Exception as e:
        return jsonify({'error': f'Failed to stop scraping: {str(e)}'}), 500

@app.route('/api/status', methods=['GET'])
def get_status():
    """Get current scraping status"""
    return jsonify({
        'active': scraping_active,
        'process_running': scraping_process is not None,
        'session_id': current_session_id,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/files/<session_id>', methods=['GET'])
def get_session_files(session_id):
    """Get list of files for a specific session"""
    try:
        session_dir = os.path.join(OUTPUT_BASE_DIR, session_id)
        if not os.path.exists(session_dir):
            return jsonify({'files': []}), 200
        
        files = []
        for file_path in glob.glob(os.path.join(session_dir, '*.xlsx')):
            filename = os.path.basename(file_path)
            file_size = os.path.getsize(file_path)
            files.append({
                'name': filename,
                'size': file_size,
                'path': file_path
            })
        
        return jsonify({'files': files}), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get files: {str(e)}'}), 500

@app.route('/api/download/<session_id>/<filename>', methods=['GET'])
def download_file(session_id, filename):
    """Download a specific file from a session"""
    try:
        file_path = os.path.join(OUTPUT_BASE_DIR, session_id, filename)
        if not os.path.exists(file_path):
            return jsonify({'error': 'File not found'}), 404
        
        return send_file(file_path, as_attachment=True, download_name=filename)
        
    except Exception as e:
        return jsonify({'error': f'Failed to download file: {str(e)}'}), 500

@app.route('/api/merge/<session_id>', methods=['POST'])
def merge_session_files(session_id):
    """Merge all Excel files in a session into one file"""
    try:
        import pandas as pd
        
        session_dir = os.path.join(OUTPUT_BASE_DIR, session_id)
        if not os.path.exists(session_dir):
            return jsonify({'error': 'Session directory not found'}), 404
        
        excel_files = glob.glob(os.path.join(session_dir, '*.xlsx'))
        if not excel_files:
            return jsonify({'error': 'No Excel files found in session'}), 404
        
        # Read and merge all Excel files
        all_data = []
        for file_path in excel_files:
            try:
                df = pd.read_excel(file_path)
                all_data.append(df)
            except Exception as e:
                socketio.emit('scraping_log', {'message': f'⚠️ Warning: Could not read {os.path.basename(file_path)}: {str(e)}'})
        
        if not all_data:
            return jsonify({'error': 'No valid Excel files found'}), 404
        
        # Merge all dataframes
        merged_df = pd.concat(all_data, ignore_index=True)
        
        # Save merged file
        merged_filename = f'merged_data_{session_id}.xlsx'
        merged_path = os.path.join(session_dir, merged_filename)
        merged_df.to_excel(merged_path, index=False)
        
        socketio.emit('scraping_log', {'message': f'📊 Merged {len(excel_files)} files into {merged_filename}'})
        
        return jsonify({
            'message': 'Files merged successfully',
            'merged_file': merged_filename,
            'total_files': len(excel_files),
            'total_rows': len(merged_df)
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to merge files: {str(e)}'}), 500

@app.route('/api/sessions', methods=['GET'])
def list_sessions():
    """List all scraping sessions"""
    try:
        sessions = []
        if os.path.exists(OUTPUT_BASE_DIR):
            for session_dir in os.listdir(OUTPUT_BASE_DIR):
                session_path = os.path.join(OUTPUT_BASE_DIR, session_dir)
                if os.path.isdir(session_path):
                    files = glob.glob(os.path.join(session_path, '*.xlsx'))
                    sessions.append({
                        'session_id': session_dir,
                        'file_count': len(files),
                        'created': datetime.fromtimestamp(os.path.getctime(session_path)).isoformat()
                    })
        
        return jsonify({'sessions': sessions}), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to list sessions: {str(e)}'}), 500

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print(f'Client connected: {request.sid}')
    emit('scraping_log', {'message': '🟢 Connected to E-Procurement backend'})
    emit('status_update', {
        'active': scraping_active,
        'session_id': current_session_id,
        'timestamp': datetime.now().isoformat()
    })

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print(f'Client disconnected: {request.sid}')

if __name__ == '__main__':
    print("🚀 Starting E-Procurement backend server on port 5021...")
    print(f"📁 Output directory: {OUTPUT_BASE_DIR}")
    socketio.run(app, host='0.0.0.0', port=5021, debug=True) 