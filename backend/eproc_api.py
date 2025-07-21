from flask import Flask, request, jsonify
import subprocess
import os

app = Flask(__name__)

@app.route('/api/start-scraping', methods=['POST'])
def start_scraping():
    data = request.json
    required = ['base_url', 'tender_type', 'days_interval', 'start_page', 'captcha']
    if not all(k in data for k in required):
        return jsonify({'error': 'Missing required fields'}), 400

    script_path = os.path.join(os.path.dirname(__file__), 'scrapers', 'search.py')
    cmd = [
        'python', '-u', script_path,
        '--base_url', data['base_url'],
        '--tender_type', data['tender_type'],
        '--days_interval', str(data['days_interval']),
        '--start_page', str(data['start_page']),
        '--captcha', data['captcha']
    ]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    return jsonify({'status': 'started', 'pid': proc.pid})

if __name__ == '__main__':
    app.run(port=5005, debug=True) 