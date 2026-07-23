import psutil
import subprocess
import sys

def check_resources():
    mem = psutil.virtual_memory()
    print(f"Available RAM: {mem.available / (1024**3):.2f} GB ({mem.percent}% used)")
    if mem.percent > 85:
        print("WARNING: Low memory condition detected. Deferring to low-resource mode.")
        return False
    return True

def run_pipeline_step(command):
    if check_resources():
        print(f"Executing: {command}")
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
    else:
        print("Task aborted to protect local environment stability.")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        run_pipeline_step(sys.argv[1])