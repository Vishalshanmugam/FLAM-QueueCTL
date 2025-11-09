import json
from datetime import datetime
from . import db, config

def enqueue(job_json):
    try:
        job = json.loads(job_json)
        cfg = config.load_config()
        job.setdefault("attempts", 0)
        job.setdefault("max_retries", cfg.get("max_retries", 3))
        job.setdefault("state", "pending")
        now = datetime.utcnow().isoformat()
        job.setdefault("created_at", now)
        job.setdefault("updated_at", now)
        db.insert_job(job)
        print(f"Job {job['id']} enqueued.")
    except Exception as e:
        print(f"Failed to enqueue job: {e}")

