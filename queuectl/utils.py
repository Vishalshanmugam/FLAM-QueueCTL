import subprocess

def run_command(command):
    try:
        result = subprocess.run(command, shell=True)
        return result.returncode == 0
    except Exception:
        return False

