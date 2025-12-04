# backend/database/db.py
import sqlite3 
import os
import json
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), 'scans.db')

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create scans table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS scans (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        scan_id TEXT UNIQUE NOT NULL,
        input_type TEXT NOT NULL,
        target_value TEXT NOT NULL,
        status TEXT NOT NULL,
        results TEXT,
        start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        end_time TIMESTAMP,
        error_message TEXT
    )
    ''')
    
    # Create findings table for better querying
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS findings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        scan_id TEXT NOT NULL,
        tool TEXT NOT NULL,
        severity TEXT,
        package_name TEXT,
        vulnerability_id TEXT,
        file_path TEXT,
        description TEXT,
        FOREIGN KEY (scan_id) REFERENCES scans (scan_id)
    )
    ''')
    
    conn.commit()
    conn.close()

def get_connection():
    return sqlite3.connect(DB_PATH)

# Initialize database when module is imported
init_db()