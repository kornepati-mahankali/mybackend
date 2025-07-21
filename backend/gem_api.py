from flask import Flask, request, jsonify
import subprocess
import os

app = Flask(__name__)

@app.route('/api/start-gem-scraping', methods=['POST'])
def start_gem_scraping():
    data = request.json
    required = ['startingpage', 'totalpages', 'username', 'days_interval']
    if not all(k in data for k in required):
        return jsonify({'error': 'Missing required fields'}), 400

    script_path = os.path.join(os.path.dirname(__file__), '..', 'scripts', 'gem_scraper.py')
    cmd = [
        'python', '-u', script_path,
        '--startingpage', str(data['startingpage']),
        '--totalpages', str(data['totalpages']),
        '--username', data['username'],
        '--days_interval', str(data['days_interval'])
    ]
    
    try:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        return jsonify({'status': 'started', 'pid': proc.pid})
    except FileNotFoundError:
        return jsonify({'error': 'The scraper script was not found.'}), 500
    except Exception as e:
        return jsonify({'error': f'An unexpected error occurred: {e}'}), 500

if __name__ == '__main__':
    app.run(port=5022, debug=True) 