#!/usr/bin/env python3
"""
Simple test script for basic Flask functionality
"""

from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'message': 'Simple test server is working'
    })

@app.route('/', methods=['GET'])
def root():
    return jsonify({
        'message': 'E-Procurement Backend Test Server',
        'endpoints': [
            '/api/health'
        ]
    })

if __name__ == '__main__':
    print("🚀 Starting simple test server on port 5021...")
    app.run(host='0.0.0.0', port=5021, debug=True) 