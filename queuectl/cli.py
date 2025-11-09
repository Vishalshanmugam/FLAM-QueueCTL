import click
from . import db, job, config
from . import worker as worker_module 


@click.group()
def cli():
    """QueueCTL - Background Job Queue System"""
    db.init_db()

# JOB COMMANDS

@cli.command()
@click.argument("job_json")
def enqueue(job_json):
    """Add a new job to the queue"""
    job.enqueue(job_json)

@cli.command()
@click.option("--state", default=None, help="Job state to clear (pending, completed, dead, all)")
def clear(state):
    """Clear jobs from the queue."""
    import sqlite3
    conn = db.get_connection()
    cur = conn.cursor()
    if state is None or state == "all":
        cur.execute("DELETE FROM jobs;")
        print("All jobs cleared.")
    else:
        cur.execute("DELETE FROM jobs WHERE state = ?;", (state,))
        print(f"Cleared all jobs with state '{state}'.")
    conn.commit()
    conn.close()


# WORKER COMMANDS

@cli.group()
def worker():
    """Worker management"""
    pass

@worker.command("start")
@click.option("--count", default=1, help="Number of workers to start")
def start_worker(count):
    """Start background worker processes"""
    from . import worker as worker_module
    worker_module.start(count)

@worker.command("stop")
def stop_worker():
    """Stop running worker processes"""
    from . import worker as worker_module
    worker_module.stop()
 

# STATUS COMMANDS

@cli.command()
def status():
    """Show system status"""
    db.print_status()

@cli.command("list")
@click.option("--state", default=None, help="Filter jobs by state (pending, failed, completed, etc.)")

def list_jobs(state):
    """List jobs by state"""
    rows = db.fetch_jobs(state)
    if not rows:
        print(f"No jobs found for state: {state}")
        return

    print(f"{'ID':<10} {'Command':<20} {'Attempts':<10} {'State':<10}")
    print("-" * 60)
    for job in rows:
        print(f"{job['id']:<10} {job['command']:<20} {job['attempts']:<10} {job['state']:<10}")

# DEAD LETTER QUEUE

@cli.group()
def dlq():
    """Dead Letter Queue"""
    pass


@dlq.command("list")
def dlq_list():
    """List DLQ jobs"""
    rows = db.fetch_jobs("dead")
    for r in rows:
        print(r)


@dlq.command("retry")
@click.argument("job_id")
def dlq_retry(job_id):
    """Retry a DLQ job"""
    db.update_job_state(job_id, "pending", 0)
    print(f"Retried job {job_id} from DLQ.")



# CONFIG COMMANDS

@cli.group(name="config")
def config_cmd():
    """Configuration"""
    pass


@config_cmd.command("set")
@click.argument("key")
@click.argument("value")
def config_set(key, value):
    """Set configuration values"""
    config.set_value(key, value)


if __name__ == "__main__":
    cli()
