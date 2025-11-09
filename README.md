# QueueCTL 
CLI-based Background Job Queue System

## Features
- Enqueue jobs and process them with multiple workers
- Retry failed jobs using exponential backoff
- Move permanently failed jobs to DLQ
- Persistent SQLite-based job storage
- Configurable retry and backoff parameters
- Graceful shutdown support

---

## Setup
```bash
git clone https://github.com/<your-username>/queuectl.git
cd queuectl
python -m venv venv
source venv/bin/activate  # windows: venv\Scripts\activate
pip install -r requirements.txt
pip install -e .

