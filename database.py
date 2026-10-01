import sqlite3
import pandas as pd

DB_NAME = "document_intelligence.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA journal_mode=WAL;")
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT,
            file_hash TEXT UNIQUE,
            doc_type TEXT,
            confidence REAL,
            status TEXT DEFAULT 'New',
            extracted_data TEXT,
            failed_fields TEXT,
            review_reason TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            document_id INTEGER,
            action TEXT,
            previous_status TEXT,
            new_status TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            reason_or_note TEXT,
            FOREIGN KEY (document_id) REFERENCES documents (id)
        )
    ''')
    conn.commit()
    conn.close()

def log_audit(doc_id, action, prev_status, new_status, reason=""):
    conn = sqlite3.connect(DB_NAME, timeout=10.0)
    conn.execute("PRAGMA journal_mode=WAL;")
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO audit_logs (document_id, action, previous_status, new_status, reason_or_note)
        VALUES (?, ?, ?, ?, ?)
    ''', (doc_id, action, prev_status, new_status, reason))
    conn.commit()
    conn.close()