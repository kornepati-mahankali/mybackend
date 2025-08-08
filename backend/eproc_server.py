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

# --- BEGIN: Redirect stdout/stderr to WebSocket for live logs ---
class WebSocketLogger:
    def __init__(self, emit_func):
        self.emit_func = emit_func
    def write(self, message):
        if message.strip():
            self.emit_func(message)
    def flush(self):
        pass

logs_buffer = []

def emit_log_to_frontend(msg, session_id=None):
    logs_buffer.append(msg)
    if len(logs_buffer) > 1000:
        logs_buffer.pop(0)
    socketio.emit('scraping_log', {'message': msg, 'session_id': session_id})

# --- END: Redirect stdout/stderr to WebSocket for live logs ---

# Import configuration from a file that might not exist, so handle the import error
try:
    from config import *
except ImportError:
    # Define fallback configurations if config.py is not found
    SERVER_HOST = '0.0.0.0'
    SERVER_PORT = 5021
    DEBUG = True
    OUTPUT_BASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'outputs', 'eproc')

# Global variables
pending_eproc_sessions = {}  # Store active Selenium sessions

# Create output directory if it doesn't exist
if not os.path.exists(OUTPUT_BASE_DIR):
    os.makedirs(OUTPUT_BASE_DIR)

def build_advanced_search_url(base_url):
    """Builds the advanced search URL from a base e-procurement URL."""
    if not base_url:
        return None
    try:
        parsed_url = urlparse(base_url)
        # Ensure scheme is present
        if not parsed_url.scheme:
            base_url = 'https://' + base_url
            parsed_url = urlparse(base_url)
        
        # Set the correct page and service in query parameters
        query_params = parse_qs(parsed_url.query)
        query_params['page'] = ['FrontEndAdvancedSearch']
        query_params['service'] = ['page']
        
        # Create the new URL
        new_query = urlencode(query_params, doseq=True)
        return urlunparse(parsed_url._replace(query=new_query))
    except Exception as e:
        print(f"[ERROR] Could not parse URL: {e}")
        return None

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'active_sessions': len(pending_eproc_sessions)
    })

@app.route('/api/open-edge', methods=['POST'])
def open_edge():
    """Opens Edge with Selenium and returns a session ID"""
    try:
        data = request.get_json()
        base_url = data.get('url', '')
        if not base_url:
            return jsonify({'error': 'URL is required'}), 400
        
        url = build_advanced_search_url(base_url)
        if not url:
            return jsonify({'error': 'Invalid URL provided'}), 400
        
        print(f"[DEBUG] Final Edge URL: {url}")

        # Path to your msedgedriver
        edge_driver_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'scrapers', 'edgedriver_win64', 'msedgedriver.exe')
        print(f"[DEBUG] Checking Edge WebDriver at: {edge_driver_path}")
        print(f"[DEBUG] Edge WebDriver exists: {os.path.exists(edge_driver_path)}")
        if not os.path.exists(edge_driver_path):
            return jsonify({'error': f'Edge WebDriver not found at {edge_driver_path}'}), 500
        
        options = Options()
        # Add any options you need, e.g., options.add_argument('--headless')
        service = Service(executable_path=edge_driver_path)
        
        bot = webdriver.Edge(service=service, options=options)
        print(f"[DEBUG] Navigating Edge to: {url}")
        bot.get(url)
        
        # Generate a unique session ID and store the bot instance
        session_id = str(uuid.uuid4())
        pending_eproc_sessions[session_id] = bot
        print(f"[DEBUG] Edge opened, session_id: {session_id}")

        return jsonify({'message': 'Edge opened successfully', 'session_id': session_id, 'url': url}), 200
        
    except Exception as e:
        print(f"[ERROR] Failed to open Edge: {e}")
        return jsonify({'error': f'Failed to open Edge: {str(e)}'}), 500

@app.route('/api/start-eproc-scraping', methods=['POST'])
def start_eproc_scraping():
    data = request.get_json()
    session_id = data.get('session_id')
    bot = pending_eproc_sessions.get(session_id)
    if not bot:
        return jsonify({'error': 'Session not found'}), 400

    def run_scraper():
        try:
            run_eproc_scraper_with_bot(
                bot=bot,
                tender_type=data.get('tender_type', 'O'),
                days_interval=data.get('days_interval', 7),
                start_page=data.get('start_page', 1),
                captcha=data.get('captcha'),
                log_callback=lambda msg: emit_log_to_frontend(msg, session_id),
                base_url=data.get('base_url'),
                session_id=session_id
            )
            emit_log_to_frontend('[INFO] Scraping finished.', session_id)
        except Exception as e:
            emit_log_to_frontend(f'[ERROR] Exception in scraping thread: {e}', session_id)
        finally:
            bot.quit()
            if session_id in pending_eproc_sessions:
                del pending_eproc_sessions[session_id]

    threading.Thread(target=run_scraper, daemon=True).start()
    return jsonify({'message': 'Scraping started!'}), 200

@app.route('/api/stop-scraping', methods=['POST'])
def stop_scraping():
    """This endpoint is now a placeholder as scraping runs in the main thread"""
    return jsonify({'message': 'Scraping runs in the main thread and cannot be stopped externally.'}), 400

@app.route('/api/status', methods=['GET'])
def get_status():
    """Get current scraping status"""
    return jsonify({
        'active': False, # No longer managing scraping_active
        'process_running': False, # No longer managing scraping_process
        'session_id': None, # No longer managing current_session_id
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/logs', methods=['GET'])
def get_logs():
    return jsonify({'logs': logs_buffer})

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

@app.route('/api/delete-file/<session_id>', methods=['POST'])
def delete_file(session_id):
    """Delete a specific file from a session"""
    try:
        data = request.get_json() or {}
        filename = data.get('filename')
        
        if not filename:
            return jsonify({'error': 'Filename is required'}), 400
        
        session_dir = os.path.join(OUTPUT_BASE_DIR, session_id)
        file_path = os.path.join(session_dir, filename)
        
        if not os.path.exists(file_path):
            return jsonify({'error': 'File not found'}), 404
        
        os.remove(file_path)
        socketio.emit('scraping_log', {'message': f'🗑️ Deleted file: {filename}'})
        
        return jsonify({'message': f'File {filename} deleted successfully'}), 200
            
    except Exception as e:
        return jsonify({'error': f'Failed to delete file: {str(e)}'}), 500

@app.route('/api/merge-download/<session_id>', methods=['GET'])
def merge_download_files(session_id):
    """Merge all files in a session and download as CSV"""
    try:
        session_dir = os.path.join(OUTPUT_BASE_DIR, session_id)
        if not os.path.exists(session_dir):
            return jsonify({'error': 'Session not found'}), 404
        
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
        
        # Save merged file as CSV
        merged_filename = f'merged_data_{session_id}.csv'
        merged_path = os.path.join(session_dir, merged_filename)
        merged_df.to_csv(merged_path, index=False)
        
        socketio.emit('scraping_log', {'message': f'📊 Merged {len(excel_files)} files into {merged_filename}'})
        
        # Return the CSV file for download
        return send_file(
            merged_path,
            mimetype='text/csv',
            as_attachment=True,
            download_name=merged_filename
        )
            
    except Exception as e:
        return jsonify({'error': f'Failed to merge and download files: {str(e)}'}), 500

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print(f'Client connected: {request.sid}')
    emit('scraping_log', {'message': '🟢 Connected to E-Procurement backend'})
    emit('status_update', {
        'active': False, # No longer managing scraping_active
        'session_id': None, # No longer managing current_session_id
        'timestamp': datetime.now().isoformat()
    })

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print(f'Client disconnected: {request.sid}')

if __name__ == '__main__':
    # Validate configuration if config.py exists
    try:
        config_errors = validate_config()
        if config_errors:
            print("❌ Configuration errors found:")
            for error in config_errors:
                print(f"  - {error}")
            exit(1)
    except NameError:
        print("✅ Proceeding with default or environment variable configurations.")
    
    print("🚀 Starting E-Procurement backend server...")
    print(f"📡 Server will be available at: http://{SERVER_HOST}:{SERVER_PORT}")
    print(f"📁 Output directory: {OUTPUT_BASE_DIR}")
    print(f"🔧 Debug mode: {DEBUG}")
    
    # Use a new variable for the WebSocket logger to avoid conflicts
    ws_logger = WebSocketLogger(emit_log_to_frontend)
    sys.stdout = ws_logger
    sys.stderr = ws_logger
    
    # Use allow_unsafe_werkzeug=True to work with Flask's reloader in debug mode.
    # This is suitable for development.
    socketio.run(app, host=SERVER_HOST, port=SERVER_PORT, debug=DEBUG, allow_unsafe_werkzeug=True) 