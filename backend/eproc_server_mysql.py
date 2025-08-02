from flask import Flask, request, jsonify, send_file, Response
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
from database_operations_mysql import EProcurementDBMySQL
# Set environment variables directly for MySQL connection
import os
os.environ['DB_HOST'] = 'localhost'
os.environ['DB_PORT'] = '3307'
os.environ['DB_USER'] = 'root'
os.environ['DB_PASSWORD'] = 'thanuja'
os.environ['DB_NAME'] = 'toolinformation'

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# In-memory buffer to store logs
logs_buffer = []
MAX_LOG_LINES = 1000

# WebSocket event handler to receive logs from the scraper
@socketio.on('log_message')
def handle_log_message(message):
    """Handle log messages from the scraper and broadcast them."""
    log_line = message.get('data', '')
    print(f"[WS-IN] {log_line}") # Print to backend console for debugging
    
    # Check for file written events
    if '[FILE_WRITTEN]' in log_line:
        try:
            # Parse the file_written message: [FILE_WRITTEN] filename session_id
            parts = log_line.split('[FILE_WRITTEN]')[1].strip().split()
            if len(parts) >= 2:
                filename = parts[0]
                file_session_id = parts[1]
                socketio.emit('file_written', {
                    'filename': filename,
                    'session_id': file_session_id,
                    'timestamp': datetime.now().isoformat()
                })
                print(f"[DEBUG] Emitted file_written event for {filename} in session {file_session_id}")
        except Exception as e:
            print(f"[ERROR] Failed to parse FILE_WRITTEN message: {e}")
    
    # Add to buffer
    if len(logs_buffer) > MAX_LOG_LINES:
        logs_buffer.pop(0)
    logs_buffer.append(log_line)
    # Broadcast to all connected clients
    socketio.emit('scraping_log', {'message': log_line})

def emit_log_to_frontend(msg, session_id=None):
    """Function to be used as a callback to send logs to the frontend."""
    if len(logs_buffer) > MAX_LOG_LINES:
        logs_buffer.pop(0)
    logs_buffer.append(msg)
    
    # Emit immediately with session_id if provided
    if session_id:
        socketio.emit('scraping_log', {'message': msg, 'session_id': session_id})
    else:
        socketio.emit('scraping_log', {'message': msg})
    
    # Force immediate delivery
    socketio.sleep(0)

@app.route('/api/logs', methods=['GET'])
def get_logs():
    """HTTP endpoint for the frontend to poll for logs."""
    return jsonify({'logs': logs_buffer})

# Global variables to track scraping status
scraping_processes = {}  # session_id -> process
scraping_active = False
current_session_id = None

# Configuration
OUTPUT_BASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'outputs', 'eproc')
if not os.path.exists(OUTPUT_BASE_DIR):
    os.makedirs(OUTPUT_BASE_DIR)

# Database file for storing merge records
DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'merge_records.json')

def load_merge_records():
    """Load merge records from JSON file"""
    try:
        if os.path.exists(DB_FILE):
            with open(DB_FILE, 'r') as f:
                return json.load(f)
        return []
    except Exception as e:
        print(f"Error loading merge records: {e}")
        return []

def save_merge_records(records):
    """Save merge records to JSON file"""
    try:
        with open(DB_FILE, 'w') as f:
            json.dump(records, f, indent=2)
    except Exception as e:
        print(f"Error saving merge records: {e}")

def store_merge_in_database(merge_record):
    """Store merge record in database"""
    try:
        records = load_merge_records()
        records.append(merge_record)
        save_merge_records(records)
        print(f"Stored merge record in database: {merge_record['session_id']}")
    except Exception as e:
        print(f"Error storing merge record: {e}")

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
        'server': 'eproc_server_mysql.py'
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
        print(f"[DEBUG] Received scraping request: {data}")
        
        # Validate required fields
        required_fields = ['base_url', 'tender_type', 'days_interval', 'start_page']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Generate session ID
        session_id = str(uuid.uuid4())
        
        # Create session directory
        session_dir = os.path.join(OUTPUT_BASE_DIR, session_id)
        if not os.path.exists(session_dir):
            os.makedirs(session_dir)
        
        # Start scraping in background thread
        thread = threading.Thread(target=run_scraping, args=(data, session_id))
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'success': True,
            'message': 'Scraping started successfully',
            'session_id': session_id
        }), 200
        
    except Exception as e:
        print(f"[ERROR] Failed to start scraping: {e}")
        return jsonify({'error': f'Failed to start scraping: {str(e)}'}), 500

def run_scraping(data, session_id):
    """Run the scraping process in a separate thread"""
    global scraping_active, current_session_id
    
    try:
        scraping_active = True
        current_session_id = session_id
        
        # Emit status update
        socketio.emit('status_update', {
            'active': True,
            'session_id': session_id,
            'timestamp': datetime.now().isoformat()
        })
        
        # Set environment variables for the scraper
        env = os.environ.copy()
        env['SESSION_ID'] = session_id
        env['OUTPUT_DIR'] = os.path.join(OUTPUT_BASE_DIR, session_id)
        
        # Build command
        script_path = os.path.join(os.path.dirname(__file__), 'scrapers', 'search.py')
        cmd = [
            sys.executable, script_path,
            '--base_url', data['base_url'],
            '--tender_type', data['tender_type'],
            '--days_interval', str(data['days_interval']),
            '--start_page', str(data['start_page'])
        ]
        
        print(f"[DEBUG] Running command: {' '.join(cmd)}")
        
        # Start subprocess
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            env=env,
            cwd=os.path.dirname(__file__)
        )
        
        scraping_processes[session_id] = proc
        
        # Monitor output
        for line in proc.stdout:
            clean_line = line.strip()
            if clean_line:
                print(f"[SCRAPER] {clean_line}")
                
                # Emit to frontend
                socketio.emit('scraping_log', {
                    'message': clean_line,
                    'session_id': session_id
                })
                
                # Check for completion
                if 'SCRAPING_COMPLETE' in clean_line.upper():
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
        return_code = proc.wait()
        
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
        if session_id in scraping_processes:
            del scraping_processes[session_id]

def move_generated_files(session_id):
    """Move generated Excel files to session directory"""
    try:
        session_dir = os.path.join(OUTPUT_BASE_DIR, session_id)
        
        # Look for Excel files in the current directory
        current_dir = os.path.dirname(__file__)
        excel_files = glob.glob(os.path.join(current_dir, '*.xlsx'))
        
        for file_path in excel_files:
            filename = os.path.basename(file_path)
            dest_path = os.path.join(session_dir, filename)
            
            # Move file to session directory
            shutil.move(file_path, dest_path)
            print(f"[DEBUG] Moved {filename} to session directory")
            
            # Emit file written event
            socketio.emit('file_written', {
                'filename': filename,
                'session_id': session_id,
                'timestamp': datetime.now().isoformat()
            })
            
    except Exception as e:
        print(f"[ERROR] Failed to move generated files: {e}")

@app.route('/api/stop-scraping', methods=['POST'])
def stop_scraping():
    """Stop the current scraping process"""
    global scraping_active, current_session_id
    
    try:
        if not scraping_active or not current_session_id:
            return jsonify({'message': 'No active scraping process'}), 200
        
        # Get the process
        proc = scraping_processes.get(current_session_id)
        if proc:
            # Terminate the process
            proc.terminate()
            try:
                proc.wait(timeout=5)  # Wait up to 5 seconds
            except subprocess.TimeoutExpired:
                proc.kill()  # Force kill if it doesn't terminate
        
        scraping_active = False
        session_id = current_session_id
        current_session_id = None
        
        # Emit status update
        socketio.emit('status_update', {
            'active': False,
            'session_id': None,
            'timestamp': datetime.now().isoformat()
        })
        
        socketio.emit('scraping_log', {
            'message': '🛑 Scraping process stopped by user',
            'session_id': session_id
        })
        
        return jsonify({
            'success': True,
            'message': 'Scraping process stopped successfully'
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to stop scraping: {str(e)}'}), 500

@app.route('/api/status', methods=['GET'])
def get_status():
    """Get current scraping status"""
    return jsonify({
        'active': scraping_active,
        'session_id': current_session_id,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/debug/files/<session_id>', methods=['GET'])
def debug_session_files(session_id):
    """Debug endpoint to list files in a session directory"""
    try:
        session_dir = os.path.join(OUTPUT_BASE_DIR, session_id)
        
        if not os.path.exists(session_dir):
            return jsonify({'error': 'Session directory not found'}), 404
        
        files = []
        for filename in os.listdir(session_dir):
            file_path = os.path.join(session_dir, filename)
            if os.path.isfile(file_path):
                files.append({
                    'name': filename,
                    'size': os.path.getsize(file_path),
                    'modified': datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat()
                })
        
        return jsonify({
            'session_id': session_id,
            'files': files,
            'total_files': len(files)
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to list files: {str(e)}'}), 500

@app.route('/api/files/<session_id>', methods=['GET'])
def get_session_files(session_id):
    """Get list of files in a session directory"""
    try:
        session_dir = os.path.join(OUTPUT_BASE_DIR, session_id)
        
        if not os.path.exists(session_dir):
            return jsonify([]), 200
        
        # Get Excel files
        excel_files = glob.glob(os.path.join(session_dir, '*.xlsx'))
        csv_files = glob.glob(os.path.join(session_dir, '*.csv'))
        
        files = []
        
        # Add Excel files
        for file_path in excel_files:
            filename = os.path.basename(file_path)
            files.append(filename)
        
        # Add CSV files
        for file_path in csv_files:
            filename = os.path.basename(file_path)
            files.append(filename)
        
        return jsonify(files), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get files: {str(e)}'}), 500

@app.route('/api/download/<session_id>/<filename>', methods=['GET'])
def download_file(session_id, filename):
    """Download a file from a session"""
    try:
        file_path = os.path.join(OUTPUT_BASE_DIR, session_id, filename)
        
        if not os.path.exists(file_path):
            return jsonify({'error': 'File not found'}), 404
        
        return send_file(file_path, as_attachment=True, download_name=filename)
        
    except Exception as e:
        return jsonify({'error': f'Failed to download file: {str(e)}'}), 500

@app.route('/api/delete-file/<session_id>', methods=['POST'])
def delete_file(session_id):
    """Delete a file from a session"""
    try:
        data = request.get_json()
        filename = data.get('filename')
        
        if not filename:
            return jsonify({'error': 'Filename is required'}), 400
        
        file_path = os.path.join(OUTPUT_BASE_DIR, session_id, filename)
        
        if not os.path.exists(file_path):
            return jsonify({'error': 'File not found'}), 404
        
        os.remove(file_path)
        
        return jsonify({'message': f'File {filename} deleted successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to delete file: {str(e)}'}), 500

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

@app.route('/api/merge-download/<session_id>', methods=['GET'])
def merge_download_session(session_id):
    """Merge all files in a session and download as CSV"""
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
                print(f"Warning: Could not read {file_path}: {e}")
        
        if not all_data:
            return jsonify({'error': 'No valid Excel files found'}), 404
        
        # Merge all dataframes
        merged_df = pd.concat(all_data, ignore_index=True)
        
        # Create response with CSV data
        csv_data = merged_df.to_csv(index=False)
        response = Response(csv_data, mimetype='text/csv')
        response.headers['Content-Disposition'] = f'attachment; filename=merged_data_{session_id}.csv'
        
        return response
        
    except Exception as e:
        return jsonify({'error': f'Failed to merge and download files: {str(e)}'}), 500

@app.route('/api/merge-single/<session_id>/<filename>', methods=['GET'])
def merge_single_file(session_id, filename):
    """Download a single merged file"""
    try:
        file_path = os.path.join(OUTPUT_BASE_DIR, session_id, filename)
        
        if not os.path.exists(file_path):
            return jsonify({'error': 'File not found'}), 404
        
        return send_file(file_path, as_attachment=True, download_name=filename)
        
    except Exception as e:
        return jsonify({'error': f'Failed to download file: {str(e)}'}), 500

@app.route('/api/merge-global', methods=['POST'])
def merge_global_files():
    """Merge all files from all sessions and store in database"""
    try:
        import pandas as pd
        from datetime import datetime
        
        data = request.get_json()
        global_session_id = data.get('session_id')
        files = data.get('files', [])
        
        if not files:
            return jsonify({'error': 'No files specified'}), 400
        
        # Create global merge directory
        global_dir = os.path.join(OUTPUT_BASE_DIR, global_session_id)
        if not os.path.exists(global_dir):
            os.makedirs(global_dir)
        
        # Read and merge all files
        all_data = []
        processed_files = []
        
        for file_info in files:
            session_id = file_info.get('session_id')
            filename = file_info.get('filename')
            file_path = os.path.join(OUTPUT_BASE_DIR, session_id, filename)
            
            if os.path.exists(file_path):
                try:
                    df = pd.read_excel(file_path)
                    # Add source information
                    df['source_session'] = session_id
                    df['source_file'] = filename
                    df['processed_date'] = datetime.now().isoformat()
                    all_data.append(df)
                    processed_files.append(filename)
                except Exception as e:
                    print(f"Error reading {file_path}: {e}")
                    continue
        
        if not all_data:
            return jsonify({'error': 'No valid files found'}), 404
        
        # Concatenate all dataframes
        merged_df = pd.concat(all_data, ignore_index=True)
        
        # Save merged file
        merged_file_path = os.path.join(global_dir, f'global_merged_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv')
        merged_df.to_csv(merged_file_path, index=False)
        
        # Store in MySQL database
        try:
            db = EProcurementDBMySQL()
            db_result = db.store_merged_data(
                df=merged_df,
                merge_session_id=global_session_id,
                source_session_id=files[0].get('session_id') if files else None,
                source_file=','.join(processed_files)
            )
            
            if db_result['success']:
                print(f"✅ MySQL Database storage successful: {db_result['records_inserted']} records inserted")
                socketio.emit('scraping_log', {
                    'message': f'📊 MySQL Database: {db_result["records_inserted"]} records stored successfully'
                })
            else:
                print(f"❌ MySQL Database storage failed: {db_result['error']}")
                socketio.emit('scraping_log', {
                    'message': f'⚠️ MySQL Database storage failed: {db_result["error"]}'
                })
        except Exception as db_error:
            print(f"❌ MySQL Database operation error: {db_error}")
            socketio.emit('scraping_log', {
                'message': f'⚠️ MySQL Database operation error: {str(db_error)}'
            })
        
        # Store merge metadata
        merge_record = {
            'session_id': global_session_id,
            'files_processed': len(processed_files),
            'total_records': len(merged_df),
            'merged_file': merged_file_path,
            'timestamp': datetime.now().isoformat(),
            'source_files': processed_files,
            'db_records_inserted': db_result.get('records_inserted', 0) if 'db_result' in locals() else 0
        }
        
        # Log the merge operation
        print(f"Global merge completed: {merge_record}")
        
        # Store in database
        store_merge_in_database(merge_record)
        
        return jsonify({
            'success': True,
            'message': f'Successfully merged {len(processed_files)} files with {len(merged_df)} total records',
            'data': merge_record
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to merge files globally: {str(e)}'}), 500

@app.route('/api/download-global-merge/<global_session_id>', methods=['GET'])
def download_global_merge(global_session_id):
    """Download the globally merged file"""
    try:
        global_dir = os.path.join(OUTPUT_BASE_DIR, global_session_id)
        if not os.path.exists(global_dir):
            return jsonify({'error': 'Global merge session not found'}), 404
        
        # Find the merged CSV file
        csv_files = glob.glob(os.path.join(global_dir, '*.csv'))
        if not csv_files:
            return jsonify({'error': 'No merged file found'}), 404
        
        # Return the most recent CSV file
        latest_file = max(csv_files, key=os.path.getctime)
        filename = os.path.basename(latest_file)
        
        return send_file(latest_file, as_attachment=True, download_name=filename)
        
    except Exception as e:
        return jsonify({'error': f'Failed to download merged file: {str(e)}'}), 500

@app.route('/api/merge-history', methods=['GET'])
def get_merge_history():
    """Get merge history from database"""
    try:
        records = load_merge_records()
        return jsonify({
            'success': True,
            'records': records,
            'total_records': len(records)
        }), 200
    except Exception as e:
        return jsonify({'error': f'Failed to get merge history: {str(e)}'}), 500

@app.route('/api/eprocurement-data', methods=['GET'])
def get_eprocurement_data():
    """Get e-procurement data from MySQL database"""
    try:
        merge_session_id = request.args.get('merge_session_id')
        limit = int(request.args.get('limit', 100))
        offset = int(request.args.get('offset', 0))
        
        db = EProcurementDBMySQL()
        result = db.get_merged_data(
            merge_session_id=merge_session_id,
            limit=limit,
            offset=offset
        )
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify({'error': result['error']}), 500
            
    except Exception as e:
        return jsonify({'error': f'Failed to get e-procurement data: {str(e)}'}), 500

@app.route('/api/eprocurement-data/<merge_session_id>', methods=['DELETE'])
def delete_eprocurement_data(merge_session_id):
    """Delete e-procurement data by merge session ID"""
    try:
        db = EProcurementDBMySQL()
        result = db.delete_merged_data(merge_session_id)
        
        if result['success']:
            return jsonify({
                'message': f'Successfully deleted {result["deleted_count"]} records',
                'deleted_count': result['deleted_count']
            }), 200
        else:
            return jsonify({'error': result['error']}), 500
            
    except Exception as e:
        return jsonify({'error': f'Failed to delete e-procurement data: {str(e)}'}), 500

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

@socketio.on('frontend_ready')
def handle_frontend_ready(data):
    """Handle frontend ready signal and send any pending logs"""
    session_id = data.get('session_id')
    print(f'Frontend ready for session: {session_id}')
    
    # Send any existing logs to the frontend
    if logs_buffer:
        for log in logs_buffer[-10:]:  # Send last 10 logs
            socketio.emit('scraping_log', {'message': log, 'session_id': session_id})
            socketio.sleep(0)
    
    emit('scraping_log', {'message': '🟢 Frontend ready, logs will appear immediately', 'session_id': session_id})

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
    print("🚀 Starting E-Procurement MySQL backend server on port 5025...")
    print(f"📁 Output directory: {OUTPUT_BASE_DIR}")
    # The 'allow_unsafe_werkzeug=True' argument is necessary to allow the Socket.IO
    # development server to work correctly with the Werkzeug reloader in debug mode.
    socketio.run(app, host='0.0.0.0', port=5025, debug=True, allow_unsafe_werkzeug=True) 