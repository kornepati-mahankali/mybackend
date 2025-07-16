import eventlet
eventlet.monkey_patch()

from flask import Flask, request, Response
from flask_socketio import SocketIO, emit
import subprocess
import os

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Store the scraping process globally
scraping_process = None
# Store the eproc scraping process separately
scraping_process_eproc = None

@app.route('/')
def index():
    return "WebSocket server is running!"

@app.route('/favicon.ico')
def favicon():
    return Response(status=204)

@app.route('/api/stop-scraping', methods=['POST'])
def stop_scraping():
    global scraping_process
    if scraping_process and scraping_process.poll() is None:
        scraping_process.terminate()
        scraping_process = None
        return {"status": "stopped"}, 200
    return {"status": "no process running"}, 200

@socketio.on('start_scraping')
def handle_start_scraping(data):
    global scraping_process
    print("Received start_scraping:", data)
    # Validate required arguments, but city_input is optional
    required_args = ['startingpage', 'totalpages', 'username', 'state_index', 'run_id']
    missing = [arg for arg in required_args if not data.get(arg)]
    if missing:
        error_msg = f"[ERROR] Missing required fields: {', '.join(missing)}\n"
        print(error_msg)
        emit('scraping_output', {'output': error_msg}, broadcast=False)
        return
    # Set city_input to empty string if not provided
    city_input = data.get('city_input', '')
    days_interval = data.get('days_interval', '')
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    gem_path = os.path.join(backend_dir, "scrapers", "gem.py")
    cmd = [
        "python", "-u", gem_path,  # -u for unbuffered output
        "--startingpage", str(data['startingpage']),
        "--totalpages", str(data['totalpages']),
        "--username", data['username'],
        "--state_index", str(data['state_index']),
        "--city_input", city_input,
        "--days_interval", str(days_interval),
        "--run_id", data['run_id']
    ]
    print("Running command:", " ".join(cmd))
    try:
        scraping_process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, cwd=backend_dir)
        for line in iter(scraping_process.stdout.readline, ''):
            print("OUTPUT:", line.strip())
            emit('scraping_output', {'output': line}, broadcast=False)
            if line.startswith("File written:"):
                filename = line.split("File written:", 1)[1].strip()
                emit('file_written', {'filename': filename, 'run_id': data['run_id']}, broadcast=False)
            eventlet.sleep(0)  # Yield to eventlet for better real-time streaming
        scraping_process.stdout.close()
        scraping_process.wait()
        emit('scraping_output', {'output': 'SCRAPING COMPLETED\n'}, broadcast=False)
        scraping_process = None
    except Exception as e:
        print("Error running gem.py:", e)
        emit('scraping_output', {'output': f'Error: {e}\n'}, broadcast=False)
        scraping_process = None

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