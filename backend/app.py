from flask import Flask, request, jsonify
from scanners.scan_utils import scan_project
from flask_cors import CORS
import json
import uuid
import threading
import os, tempfile, shutil, subprocess, traceback

from scanners.run_codeql import run_codeql_scan
from scanners.run_gitleaks import run_gitleaks_scan
from scanners.run_syft import generate_sbom
from scanners.run_osv import run_osv_scan
from scanners.run_noir import run_noir_scan 

from database.db import get_connection
import json
from datetime import datetime

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Demo
users = {
    "admin": "admin123",
    "saswath": "vel123"
}

# Store scan results keyed by scan_id
scan_results = {}

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Missing credentials"}), 400

    if users.get(username) == password:
        return jsonify({"success": True, "token": "demo-token"})
    else:
        return jsonify({"error": "Invalid username or password"}), 401


@app.route('/api/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    save_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(save_path)
    print(f"✅ Uploaded file saved to {save_path}")

    return jsonify({"status": "uploaded", "filename": file.filename})


# ---------------------    print("I had encounterd an error\n")Async Scan ---------------------
def async_scan(scan_id, input_type, repo_url):
    try:
        # Store initial scan record
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO scans (scan_id, input_type, target_value, status) VALUES (?, ?, ?, ?)',
            (scan_id, input_type, repo_url, 'running')
        )
        conn.commit()
        conn.close()
        
        scan_results[scan_id] = {"status": "running", "result": None}
        result = scan_project(input_type, repo_url)
        
        # Update scan record with results
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE scans SET status = ?, results = ?, end_time = ? WHERE scan_id = ?',
            ('completed', json.dumps(result), datetime.now().isoformat(), scan_id)
        )
        conn.commit()
        conn.close()
        
        scan_results[scan_id] = {"status": "done", "result": result}
        
    except Exception as ex:
        # Update scan record with error
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE scans SET status = ?, error_message = ?, end_time = ? WHERE scan_id = ?',
            ('error', str(ex), datetime.now().isoformat(), scan_id)
        )
        conn.commit()
        conn.close()
    
        scan_results[scan_id] = {"status": "error", "result": str(ex)}

@app.route("/api/scan", methods=["POST"])
def scan():
    data = request.get_json()
    input_type = data.get("type")
    repo_url = data.get("value")

    # Generate a unique scan ID
    scan_id = str(uuid.uuid4())

    # 🧠 Fix for ZIP uploads — build full path
    if input_type == "upload":
        full_zip_path = os.path.join(UPLOAD_FOLDER, repo_url)
        if not os.path.exists(full_zip_path):
            return jsonify({"error": f"Uploaded file not found: {full_zip_path}"}), 400
        repo_url = full_zip_path  # ✅ Use full path for scan_project

    # Start async scan in background
    thread = threading.Thread(target=async_scan, args=(scan_id, input_type, repo_url))
    thread.start()

    # Return scan ID immediately
    return jsonify({"scan_id": scan_id})

@app.route("/api/scan-result/<scan_id>", methods=["GET"])
def get_scan_result(scan_id):
    result = scan_results.get(scan_id)
    if not result:
        return jsonify({"status": "not_found", "result": None}), 404
    return jsonify(result)


# Add these new endpoints after your existing routes

@app.route('/api/scans/history', methods=['GET'])
def get_scan_history():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT scan_id, input_type, target_value, status, start_time, end_time 
            FROM scans 
            ORDER BY start_time DESC 
            LIMIT 50
        ''')
        
        scans = []
        for row in cursor.fetchall():
            scans.append({
                'scan_id': row[0],
                'input_type': row[1],
                'target_value': row[2],
                'status': row[3],
                'start_time': row[4],
                'end_time': row[5]
            })
        
        conn.close()
        return jsonify(scans)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/scans/<scan_id>', methods=['GET'])
def get_scan_details(scan_id):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM scans WHERE scan_id = ?', (scan_id,))
        row = cursor.fetchone()
        
        if not row:
            return jsonify({'error': 'Scan not found'}), 404
        
        scan_details = {
            'scan_id': row[1],
            'input_type': row[2],
            'target_value': row[3],
            'status': row[4],
            'results': json.loads(row[5]) if row[5] else None,
            'start_time': row[6],
            'end_time': row[7],
            'error_message': row[8]
        }
        
        conn.close()
        return jsonify(scan_details)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5001)
