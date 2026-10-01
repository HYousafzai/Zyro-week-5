import streamlit as st
import sqlite3
import json
import pandas as pd
from database import init_db, DB_NAME, log_audit
from storage import save_uploaded_file, calculate_file_hash
from workflow import process_workflow_engine, can_transition

st.set_page_config(page_title="AI Document Intelligence & Workflow Platform", layout="wide")
init_db()

st.title("📄 AI Document Intelligence & Workflow Platform")

menu = ["Upload & Process", "Repository & Search", "Human Review Queue", "Batch Processing", "Metrics Dashboard"]
choice = st.sidebar.selectbox("Navigation", menu)

def get_connection():
    return sqlite3.connect(DB_NAME, timeout=10.0)

if choice == "Upload & Process":
    st.header("Upload Document")
    uploaded_file = st.file_uploader("Upload PDF or Image", type=["pdf", "png", "jpg"])
    doc_type = st.selectbox("Select Document Type", ["Invoice", "Resume"])
    
    if uploaded_file and st.button("Process Document"):
        file_path, file_hash, file_bytes = save_uploaded_file(uploaded_file)
        
        conn = get_connection()
        cursor = conn.cursor()
        
        # Check duplicate
        cursor.execute("SELECT id FROM documents WHERE file_hash = ?", (file_hash,))
        existing_doc = cursor.fetchone()
        
        if existing_doc:
            st.warning("⚠️ Duplicate file detected! This document already exists in the repository.")
            conn.close()
        else:
            # Mock extracted data for demonstration
            mock_data = {
                "invoice_number": "INV-1001" if doc_type == "Invoice" else "",
                "date": "2026-10-01" if doc_type == "Invoice" else "",
                "company_name": "Zyroo Corp" if doc_type == "Invoice" else "",
                "total_amount": "500.00" if doc_type == "Invoice" else "",
                "name": "John Doe" if doc_type == "Resume" else "",
                "email": "johndoe@example.com" if doc_type == "Resume" else "",
                "skills": ["Python", "Machine Learning"] if doc_type == "Resume" else []
            }
            confidence = 0.85
            
            cursor.execute("""
                INSERT INTO documents (filename, file_hash, doc_type, confidence, status, extracted_data)
                VALUES (?, ?, ?, ?, 'New', ?)
            """, (uploaded_file.name, file_hash, doc_type, confidence, json.dumps(mock_data)))
            doc_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            # Run workflow engine safely
            success, final_status = process_workflow_engine(doc_id, doc_type, mock_data, confidence)
            st.success(f"Document processed successfully! Status: **{final_status}**")

elif choice == "Repository & Search":
    st.header("Document Repository & Filters")
    
    status_filter = st.selectbox("Filter by Status", ["All", "New", "Processing", "Needs Review", "Approved", "Rejected", "Completed"])
    search_query = st.text_input("Search by filename, type, or company")
    
    conn = get_connection()
    query = "SELECT id, filename, doc_type, status, review_reason, created_at FROM documents WHERE 1=1"
    params = []
    
    if status_filter != "All":
        query += " AND status = ?"
        params.append(status_filter)
    if search_query:
        query += " AND (filename LIKE ? OR doc_type LIKE ?)"
        params.extend([f"%{search_query}%", f"%{search_query}%"])
        
    df = pd.read_sql(query, conn, params=params)
    conn.close()
    
    if df.empty:
        st.info("No documents found in the repository matching your filters.")
    else:
        st.dataframe(df, use_container_width=True)

elif choice == "Human Review Queue":
    st.header("Human Review Queue")
    
    conn = get_connection()
    df_review = pd.read_sql("SELECT id, filename, doc_type, review_reason, extracted_data FROM documents WHERE status = 'Needs Review'", conn)
    conn.close()
    
    if df_review.empty:
        st.info("No documents currently require review. (Tip: Try uploading a document with missing fields to route it here).")
    else:
        for index, row in df_review.iterrows():
            with st.expander(f"File: {row['filename']} ({row['doc_type']})"):
                st.write(f"**Review Reason:** {row['review_reason']}")
                st.json(json.loads(row['extracted_data']))
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Approve", key=f"app_{row['id']}"):
                        conn = get_connection()
                        cursor = conn.cursor()
                        cursor.execute("UPDATE documents SET status = 'Approved' WHERE id = ?", (row['id'],))
                        log_audit(row['id'], "Manual Review", "Needs Review", "Approved", "Approved by reviewer")
                        conn.commit()
                        conn.close()
                        st.success("Document Approved!")
                        st.rerun()
                with col2:
                    reject_reason = st.text_input("Rejection Reason", key=f"rej_reason_{row['id']}")
                    if st.button("Reject", key=f"rej_{row['id']}"):
                        if not reject_reason:
                            st.error("Please provide a rejection reason.")
                        else:
                            conn = get_connection()
                            cursor = conn.cursor()
                            cursor.execute("UPDATE documents SET status = 'Rejected', review_reason = ? WHERE id = ?", (reject_reason, row['id']))
                            log_audit(row['id'], "Manual Review", "Needs Review", "Rejected", reject_reason)
                            conn.commit()
                            conn.close()
                            st.error("Document Rejected!")
                            st.rerun()

elif choice == "Batch Processing":
    st.header("Batch Workflow Processing")
    conn = get_connection()
    df_batch = pd.read_sql("SELECT id, filename, doc_type, status, extracted_data, confidence FROM documents WHERE status = 'New'", conn)
    conn.close()
    
    if df_batch.empty:
        st.info("No new documents available for batch processing.")
    else:
        selected_ids = st.multiselect("Select Document IDs to Batch Process", df_batch['id'].tolist())
        if st.button("Run Batch Workflow"):
            success_count, fail_count = 0, 0
            for doc_id in selected_ids:
                try:
                    row = df_batch[df_batch['id'] == doc_id].iloc[0]
                    process_workflow_engine(doc_id, row['doc_type'], json.loads(row['extracted_data']), row['confidence'])
                    success_count += 1
                except Exception as e:
                    fail_count += 1
            st.success(f"Batch completed! Processed: {success_count}, Failed: {fail_count}")

elif choice == "Metrics Dashboard":
    st.header("Workflow Metrics Dashboard")
    conn = get_connection()
    total_docs_df = pd.read_sql("SELECT COUNT(*) as cnt FROM documents", conn)
    total_docs = total_docs_df['cnt'][0] if not total_docs_df.empty else 0
    status_counts = pd.read_sql("SELECT status, COUNT(*) as count FROM documents GROUP BY status", conn)
    type_counts = pd.read_sql("SELECT doc_type, COUNT(*) as count FROM documents GROUP BY doc_type", conn)
    conn.close()
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Documents", total_docs)
    
    if not status_counts.empty:
        st.subheader("Counts by Status")
        st.bar_chart(status_counts.set_index("status"))
    
    if not type_counts.empty:
        st.subheader("Counts by Document Type")
        st.bar_chart(type_counts.set_index("doc_type"))