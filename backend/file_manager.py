from flask import Flask, send_file, jsonify
from flask_cors import CORS
import os
import pandas as pd
import zipfile
import io

app = Flask(__name__)
CORS(app)  # Add CORS support to allow requests from the frontend

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUTS_BASE_DIR = os.path.join(BASE_DIR, 'outputs', 'gem')

def get_run_dir(run_id):
    """Constructs the output directory path for a given run_id and ensures it exists."""
    import os
    if not run_id or '..' in run_id or '/' in run_id or '\\' in run_id:
        return None, "Invalid run_id"
    run_dir = os.path.join(OUTPUTS_BASE_DIR, run_id)
    os.makedirs(run_dir, exist_ok=True)  # Always create the directory if missing
    return run_dir, None

@app.route('/')
def home():
    return "Welcome to the File Manager API!"

@app.route('/api/files/<run_id>', methods=['GET'])
def list_files(run_id):
    run_dir, error = get_run_dir(run_id)
    if error:
        return jsonify({"error": error}), 400
    try:
        files = [f for f in os.listdir(run_dir) if f.endswith('.xlsx')]
        return jsonify(files)
    except FileNotFoundError:
        return jsonify([])

@app.route('/api/download/<run_id>/<filename>', methods=['GET'])
def download_file(run_id, filename):
    run_dir, error = get_run_dir(run_id)
    if error:
        return jsonify({"error": error}), 400
    
    file_path = os.path.join(run_dir, filename)
    if not os.path.exists(file_path):
        return "File not found", 404
        
    return send_file(file_path, as_attachment=True)

@app.route('/api/merge-download/<run_id>', methods=['GET'])
def merge_download(run_id):
    run_dir, error = get_run_dir(run_id)
    if error:
        return jsonify({"error": error}), 400

    files = [f for f in os.listdir(run_dir) if f.endswith('.xlsx')]
    if not files:
        return "No files to merge", 404
        
    merged_df = pd.DataFrame()
    for file in files:
        df = pd.read_excel(os.path.join(run_dir, file))
        merged_df = pd.concat([merged_df, df], ignore_index=True)
    
    merged_filename = f'merged_data_{run_id}.xlsx'
    merged_filepath = os.path.join(run_dir, merged_filename)
    with pd.ExcelWriter(merged_filepath, engine='xlsxwriter') as writer:
        merged_df.to_excel(writer, index=False, sheet_name='MergedData')

    with open(merged_filepath, 'rb') as f:
        excel_io = io.BytesIO(f.read())
    excel_io.seek(0)
    
    return send_file(
        excel_io,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=merged_filename
    )

@app.route('/api/delete/<run_id>/<filename>', methods=['DELETE'])
def delete_file_endpoint(run_id, filename):
    run_dir, error = get_run_dir(run_id)
    if error:
        return jsonify({"error": error}), 400

    file_path = os.path.join(run_dir, filename)
    if os.path.exists(file_path):
        os.remove(file_path)
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'error': 'File not found'}), 404

@app.route('/api/download-all/<run_id>', methods=['GET'])
def download_all(run_id):
    run_dir, error = get_run_dir(run_id)
    if error:
        return jsonify({"error": error}), 400
        
    files = [f for f in os.listdir(run_dir) if f.endswith('.xlsx')]
    if not files:
        return "No files to zip", 404

    mem_zip = io.BytesIO()
    with zipfile.ZipFile(mem_zip, 'w') as zf:
        for file in files:
            zf.write(os.path.join(run_dir, file), arcname=file)
    mem_zip.seek(0)
    
    return send_file(
        mem_zip,
        mimetype='application/zip',
        as_attachment=True,
        download_name=f'all_data_{run_id}.zip'
    )
    
@app.route('/favicon.ico')
def favicon():
    return '', 204

if __name__ == '__main__':
    app.run(port=5001, debug=True) 
