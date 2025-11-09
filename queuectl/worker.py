import multiprocessing
import subprocess
import time
import os
import signal
import json
from . import db

PID_FILE = "worker_pids.json"

def worker_loop(worker_id):
    print(f"Worker ID - {worker_id} started (PID {os.getpid()})")
    while True:
        conn = db.get_connection()
        c = conn.cursor()
        c.execute("SELECT id, command, attempts, max_retries FROM jobs WHERE state='pending' ORDER BY created_at LIMIT 1")
        row = c.fetchone()
        conn.close()

        if not row:
            time.sleep(2)
            continue

        job_id, command, attempts, max_retries = row
        db.update_job_state(job_id, "processing", attempts)
        print(f"[Worker ID - {worker_id}] Processing job: {job_id} -> {command}")

        try:
            result = subprocess.run(command, shell=True)
            if result.returncode == 0:
                db.update_job_state(job_id, "completed")
                print(f"[Worker ID - {worker_id}] Job with ID {job_id} completed")
            else:
                raise Exception("Command failed")
        except Exception:
            attempts += 1
            if attempts >= max_retries:
                db.update_job_state(job_id, "dead", attempts)
                print(f"[Worker ID - {worker_id}] Job with ID - {job_id} moved to DLQ")
            else:
                delay = 2 ** attempts
                print(f"[Worker {worker_id}] Failed! Retrying in {delay} seconds (attempt {attempts})")
                time.sleep(delay)
                db.update_job_state(job_id, "pending", attempts)

        time.sleep(1)

def start(count):
    """Start worker processes in background"""
    procs = []
    for i in range(count):
        p = multiprocessing.Process(target=worker_loop, args=(i,))
        p.start()
        procs.append(p.pid)

    # Save PIDs
    with open(PID_FILE, "w") as f:
        json.dump(procs, f)

    print(f"Started {count} worker(s): {procs}")
    print("Workers are running in background. You can safely close this terminal.")

def stop():
    """Stop all background workers"""
    if not os.path.exists(PID_FILE):
        print("No running workers found.")
        return

    with open(PID_FILE) as f:
        pids = json.load(f)

    for pid in pids:
        try:
            os.kill(pid, signal.SIGTERM)
            print(f"Stopped worker PID number - {pid}")
        except ProcessLookupError:
            print(f" Worker PID {pid} not found")

    os.remove(PID_FILE)
    print("All workers stopped successfully.")
