import re

def validate_document(doc_type, data):
    failed_fields = []
    
    if doc_type == "Invoice":
        required = ["invoice_number", "date", "company_name", "total_amount"]
        for field in required:
            if not data.get(field):
                failed_fields.append(field)
        
        # Email & numeric checks
        email = data.get("email", "")
        if email and not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            failed_fields.append("email_format")
            
    elif doc_type == "Resume":
        required = ["name", "email", "skills"]
        for field in required:
            if not data.get(field):
                failed_fields.append(field)
        
        email = data.get("email", "")
        if email and not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            failed_fields.append("email_format")
    else:
        failed_fields.append("unknown_doc_type")
        
    return failed_fields