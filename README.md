# 📄 AI Document Intelligence & Workflow Platform

An end-to-end intelligent document processing, validation, and workflow management system built for the Zyroo AI/ML Internship (Week 5). This application automates document classification, tracks state transitions, manages human review queues, and provides a real-time analytics dashboard.

---

##  Key Features

* **Advanced State Machine Workflow:** Governs document lifecycles (`New` ➜ `Processing` ➜ `Needs Review` / `Completed` ➜ `Approved` / `Rejected`) with strict transition checks.
* **Rule-Based Validation Engine:** Automatically inspects invoices and resumes for required schema fields, correct formatting (e.g., email validation), and data integrity.
* **Confidence-Aware Routing:** Automatically routes low-confidence extractions (<0.75) or failed validations directly to the human review queue.
* **Immutable Audit Trail:** Records a complete history of every document action, status change, timestamp, and review note in an independent SQLite audit log.
* **Interactive Human Review Queue:** Allows reviewers to inspect extraction failures, approve documents, or reject submissions with mandatory review notes.
* **Batch Processing & Error Isolation:** Supports multi-document batch runs with robust exception handling so individual file failures never crash the batch.
* **Repository & Search:** Advanced filtering by document status, file type, and keyword search across filenames and metadata.
* **Metrics Dashboard:** Real-time visual metrics tracking total document volume, status distribution, and document type breakdowns using Streamlit charts.
* **Duplicate Protection:** Computes SHA-256 file hashes on upload to instantly detect and block duplicate file submissions.

---

##  Tech Stack

* **Frontend & UI:** Python, Streamlit
* **Database & Storage:** SQLite (configured with WAL mode for concurrency)
* **Data Processing & Analysis:** Pandas, JSON
* **Environment:** Python 3.x

---

##  Project Structure

```text
├── app.py              # Main Streamlit user interface & multi-tab navigation
├── workflow.py         # Rule-based workflow engine & state transition logic
├── validator.py        # Document field validation and regex checks
├── database.py         # SQLite connection manager, schema init, & audit logger
├── storage.py          # File hashing and secure local document storage
└── document_intelligence.db # SQLite database (auto-generated)


 Installation & Setup
## 1 Clone the repository:

Bash
git clone [https://github.com/HYousafzai/document-intelligence-platform.git](https://github.com/HYousafzai/document-intelligence-platform.git)
cd document-intelligence-platform

## 2: Install dependencies:
Ensure you have Python installed, then install the required packages:

Bash
streamlit
pandas

## 3: Run the application:

Bash
streamlit run app.py

Testing & Verification Guide
Happy Path (Completed): Upload a complete, valid invoice or resume. The document will pass validation and automatically transition to Completed.

Validation Failure (Needs Review): Upload a document missing required fields (e.g., missing total amount or candidate email). The engine will automatically route it to the Human Review Queue.

Duplicate Detection: Upload the exact same file twice to verify that the SHA-256 hash check triggers a duplicate warning.

Human Review Action: Navigate to the Human Review Queue, test approving a file, or reject a file with a mandatory rejection note.

Batch Processing: Select multiple pending files in the Batch Processing tab and execute a batch run.

👤 Author
Hania Yousafzai

GitHub: @HYousafzai