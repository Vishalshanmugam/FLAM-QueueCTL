import sqlite3
import os
from datetime import datetime
from tabulate import tabulate

DB_PATH = os.path.expanduser("~/.queuectl_jobs.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS jobs (
        id TEXT PRIMARY KEY,
        command TEXT,
        state TEXT,
        attempts INTEGER,
        max_retries INTEGER,
        created_at TEXT,
        updated_at TEXT
    )
    """)
    conn.commit()
    conn.close()

def insert_job(job):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        INSERT OR REPLACE INTO jobs (id, command, state, attempts, max_retries, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        job["id"], job["command"], job["state"], job["attempts"],
        job["max_retries"], job["created_at"], job["updated_at"]
    ))
    conn.commit()
    conn.close()

def fetch_jobs(state=None):
    conn = get_connection()
    c = conn.cursor()
    if state:
        c.execute("SELECT * FROM jobs WHERE state = ?", (state,))
    else:
        c.execute("SELECT * FROM jobs")
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def update_job_state(job_id, state, attempts=None):
    conn = get_connection()
    c = conn.cursor()
    updated_at = datetime.utcnow().isoformat()
    if attempts is not None:
        c.execute("UPDATE jobs SET state=?, attempts=?, updated_at=? WHERE id=?", (state, attempts, updated_at, job_id))
    else:
        c.execute("UPDATE jobs SET state=?, updated_at=? WHERE id=?", (state, updated_at, job_id))
    conn.commit()
    conn.close()

def print_status():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT state, COUNT(*) as count FROM jobs GROUP BY state")
    rows = c.fetchall()
    conn.close()
    print(tabulate(rows, headers=["State", "Count"], tablefmt="grid"))

def move_to_dlq(job_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE jobs SET state='dead', updated_at=? WHERE id=?", (datetime.utcnow().isoformat(), job_id))
    conn.commit()
    conn.close()

