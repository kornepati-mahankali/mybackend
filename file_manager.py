from flask import Flask, send_file, jsonify, request
import os
import pandas as pd
import zipfile
import io

app = Flask(__name__)

# Adjust this path to your output directory
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'outputs', 'gem', 'test-run-001')

@app.route('/api/files', methods=['GET'])
def list_files():
    files = [f for f in os.listdir(OUTPUT_DIR) if f.endswith('.xlsx')]
    return jsonify(files)

@app.route('/api/download/<filename>', methods=['GET'])
def download_csv(filename):
    file_path = os.path.join(OUTPUT_DIR, filename)
    if not os.path.exists(file_path):
        return "File not found", 404
    df = pd.read_excel(file_path)
    csv_io = io.StringIO()
    df.to_csv(csv_io, index=False)
    csv_io.seek(0)
    return send_file(
        io.BytesIO(csv_io.getvalue().encode()),
        mimetype='text/csv',
        as_attachment=True,
        download_name=filename.replace('.xlsx', '.csv')
    )

@app.route('/api/merge-download', methods=['GET'])
def merge_download():
    files = [f for f in os.listdir(OUTPUT_DIR) if f.endswith('.xlsx')]
    merged_df = pd.DataFrame()
    for file in files:
        df = pd.read_excel(os.path.join(OUTPUT_DIR, file))
        merged_df = pd.concat([merged_df, df], ignore_index=True)
    csv_io = io.StringIO()
    merged_df.to_csv(csv_io, index=False)
    csv_io.seek(0)
    return send_file(
        io.BytesIO(csv_io.getvalue().encode()),
        mimetype='text/csv',
        as_attachment=True,
        download_name='merged_data.csv'
    )

@app.route('/api/delete/<filename>', methods=['DELETE'])
def delete_file(filename):
    file_path = os.path.join(OUTPUT_DIR, filename)
    if os.path.exists(file_path):
        os.remove(file_path)
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'error': 'File not found'}), 404

@app.route('/api/download-all', methods=['GET'])
def download_all():
    files = [f for f in os.listdir(OUTPUT_DIR) if f.endswith('.xlsx')]
    mem_zip = io.BytesIO()
    with zipfile.ZipFile(mem_zip, 'w') as zf:
        for file in files:
            df = pd.read_excel(os.path.join(OUTPUT_DIR, file))
            csv_io = io.StringIO()
            df.to_csv(csv_io, index=False)
            zf.writestr(file.replace('.xlsx', '.csv'), csv_io.getvalue())
    mem_zip.seek(0)
    return send_file(
        mem_zip,
        mimetype='application/zip',
        as_attachment=True,
        download_name='all_data.zip'
    )

if __name__ == '__main__':
    app.run(port=5001, debug=True)