import eventlet
eventlet.monkey_patch()

from flask import Flask, request, Response
from flask_socketio import SocketIO, emit
import subprocess
import os

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Store scraping processes by run_id to allow multiple concurrent scraping
scraping_processes = {}
# Store the eproc scraping process separately
scraping_process_eproc = None

@app.route('/')
def index():
    return "WebSocket server is running!"

@app.route('/favicon.ico')
def favicon():
    return Response(status=204)

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@socketio.on('start_scraping')
def handle_start_scraping(data):
    global scraping_processes
    print("Received start_scraping:", data)
    
    run_id = data.get('run_id')
    if not run_id:
        emit('scraping_output', {'output': '[ERROR] Missing run_id\n'}, broadcast=False)
        return
    
    # Check if scraping is already running for this specific run_id
    if run_id in scraping_processes and scraping_processes[run_id] is not None:
        emit('scraping_output', {'output': f'[ERROR] Scraping is already running for run_id: {run_id}\n'}, broadcast=False)
        return
    
    # Validate required fields (city_input and days_interval are optional)
    required_args = ['startingpage', 'totalpages', 'username', 'state_index', 'run_id']
    missing = [arg for arg in required_args if not data.get(arg)]
    if missing:
        error_msg = f"[ERROR] Missing required fields: {', '.join(missing)}\n"
        print(error_msg)
        emit('scraping_output', {'output': error_msg}, broadcast=False)
        return
    
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    gem_path = os.path.join(backend_dir, "scrapers", "gem.py")
    cmd = [
        "python", "-u", gem_path,
        "--startingpage", str(data['startingpage']),
        "--totalpages", str(data['totalpages']),
        "--username", data['username'],
        "--state_index", str(data['state_index']),
        "--city_input", data.get('city_input', ''),
        "--days_interval", str(data.get('days_interval', 1)),
        "--run_id", data['run_id']
    ]
    print("Running command:", " ".join(cmd))
    
    try:
        scraping_processes[run_id] = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, cwd=backend_dir)
        for line in iter(scraping_processes[run_id].stdout.readline, ''):
            print("OUTPUT:", line.strip())
            emit('scraping_output', {'output': line}, broadcast=False)
            if line.startswith("File written:"):
                full_path = line.split("File written:", 1)[1].strip()
                # Extract just the filename from the full path
                filename = os.path.basename(full_path)
                emit('file_written', {'filename': filename, 'run_id': data['run_id']}, broadcast=False)
            eventlet.sleep(0)  # Yield to eventlet for better real-time streaming
        scraping_processes[run_id].stdout.close()
        scraping_processes[run_id].wait()
        emit('scraping_output', {'output': 'SCRAPING COMPLETED\n'}, broadcast=False)
        scraping_processes[run_id] = None
        # Clean up the completed process from the dictionary
        if run_id in scraping_processes:
            del scraping_processes[run_id]
    except Exception as e:
        print("Error running gem.py:", e)
        emit('scraping_output', {'output': f'Error: {e}\n'}, broadcast=False)
        scraping_processes[run_id] = None
        # Clean up the failed process from the dictionary
        if run_id in scraping_processes:
            del scraping_processes[run_id]

@socketio.on('stop_scraping')
def handle_stop_scraping(data):
    global scraping_processes
    run_id = data.get('run_id')
    if not run_id:
        emit('scraping_output', {'output': '[ERROR] Missing run_id\n'}, broadcast=False)
        return
    
    if run_id in scraping_processes and scraping_processes[run_id] is not None:
        try:
            scraping_processes[run_id].terminate()
            scraping_processes[run_id].wait(timeout=5)
            emit('scraping_output', {'output': f'[INFO] Scraping stopped for run_id: {run_id}\n'}, broadcast=False)
        except subprocess.TimeoutExpired:
            scraping_processes[run_id].kill()
            emit('scraping_output', {'output': f'[INFO] Scraping force killed for run_id: {run_id}\n'}, broadcast=False)
        except Exception as e:
            emit('scraping_output', {'output': f'[ERROR] Error stopping scraping: {e}\n'}, broadcast=False)
        finally:
            scraping_processes[run_id] = None
            # Clean up the stopped process from the dictionary
            if run_id in scraping_processes:
                del scraping_processes[run_id]
    else:
        emit('scraping_output', {'output': f'[INFO] No scraping process found for run_id: {run_id}\n'}, broadcast=False)

@socketio.on('start_eproc_scraping')
def handle_start_eproc_scraping(data):
    global scraping_process_eproc
    print("Received start_eproc_scraping:", data)
    required_args = ['base_url', 'tender_type', 'days_interval', 'start_page', 'run_id']
    missing = [arg for arg in required_args if not data.get(arg)]
    if missing:
        error_msg = f"[ERROR] Missing required fields: {', '.join(missing)}\n"
        print(error_msg)
        emit('eproc_scraping_output', {'output': error_msg}, broadcast=False)
        return
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    eproc_path = os.path.join(backend_dir, "scrapers", "search.py")
    cmd = [
        "python", "-u", eproc_path,
        "--base_url", data['base_url'],
        "--tender_type", data['tender_type'],
        "--days_interval", str(data['days_interval']),
        "--start_page", str(data['start_page'])
    ]
    print("Running command:", " ".join(cmd))
    try:
        scraping_process_eproc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, cwd=backend_dir)
        for line in iter(scraping_process_eproc.stdout.readline, ''):
            print("EPROC OUTPUT:", line.strip())
            emit('eproc_scraping_output', {'output': line}, broadcast=False)
            eventlet.sleep(0)
        scraping_process_eproc.stdout.close()
        scraping_process_eproc.wait()
        emit('eproc_scraping_output', {'output': 'E-PROC SCRAPING COMPLETED\n'}, broadcast=False)
        scraping_process_eproc = None
    except Exception as e:
        print("Error running search.py:", e)
        emit('eproc_scraping_output', {'output': f'Error: {e}\n'}, broadcast=False)
        scraping_process_eproc = None

if __name__ == '__main__':
    socketio.run(app, port=5003, debug=True) 