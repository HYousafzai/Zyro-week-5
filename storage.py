import hashlib
import os

UPLOAD_DIR = "uploaded_docs"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def calculate_file_hash(file_bytes):
    return hashlib.sha256(file_bytes).hexdigest()

def save_uploaded_file(uploaded_file):
    file_bytes = uploaded_file.read()
    file_hash = calculate_file_hash(file_bytes)
    file_path = os.path.join(UPLOAD_DIR, uploaded_file.name)
    
    with open(file_path, "wb") as f:
        f.write(file_bytes)
        
    return file_path, file_hash, file_bytes