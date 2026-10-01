import sqlite3
import json
from validator import validate_document
from database import log_audit, DB_NAME

VALID_TRANSITIONS = {
    "New": ["Processing"],
    "Processing": ["Completed", "Needs Review"],
    "Needs Review": ["Approved", "Rejected"],
    "Approved": ["Completed"],
    "Rejected": [],
    "Completed": []
}

def can_transition(current_status, new_status):
    return new_status in VALID_TRANSITIONS.get(current_status, [])

def process_workflow_engine(doc_id, doc_type, extracted_data, confidence=None):
    # 1. Fetch current status
    conn = sqlite3.connect(DB_NAME, timeout=10.0)
    conn.execute("PRAGMA journal_mode=WAL;")
    cursor = conn.cursor()
    cursor.execute("SELECT status FROM documents WHERE id = ?", (doc_id,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return False, "Document not found"
    
    current_status = row[0]
    
    # 2. Move to Processing
    if can_transition(current_status, "Processing"):
        conn = sqlite3.connect(DB_NAME, timeout=10.0)
        conn.execute("PRAGMA journal_mode=WAL;")
        cursor = conn.cursor()
        cursor.execute("UPDATE documents SET status = 'Processing' WHERE id = ?", (doc_id,))
        conn.commit()
        conn.close()
        
        log_audit(doc_id, "Start Processing", current_status, "Processing", "Workflow processing started")
        current_status = "Processing"
    
    # 3. Validate Fields & Confidence threshold (< 0.75 routes to review)
    failed_fields = validate_document(doc_type, extracted_data)
    low_confidence = confidence is not None and confidence < 0.75
    
    if failed_fields or low_confidence:
        target_status = "Needs Review"
        reason = f"Failed validation: {failed_fields}" if failed_fields else "Low model classification confidence"
    else:
        target_status = "Completed"
        reason = "Validation passed successfully"
        
    if can_transition(current_status, target_status):
        conn = sqlite3.connect(DB_NAME, timeout=10.0)
        conn.execute("PRAGMA journal_mode=WAL;")
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE documents 
            SET status = ?, failed_fields = ?, review_reason = ? 
            WHERE id = ?
        """, (target_status, json.dumps(failed_fields), reason, doc_id))
        conn.commit()
        conn.close()
        
        log_audit(doc_id, "Automated Decision", current_status, target_status, reason)
        
    return True, target_status