from subprocess import Popen, PIPE, STDOUT
from threading import Thread
from pathlib import Path
import os

def run_tool_background(script: str, args: dict, run_id: str, log_file: Path):
    os.makedirs(log_file.parent, exist_ok=True)

    command = ["python", script]
    for k, v in args.items():
        command.append(f"--{k}={v}")
    command.append(f"--run_id={run_id}")
    print("Launching command", command)
    print("Log file path:",log_file)

    def _stream_logs():
        with open(log_file, "w") as f:
            process = Popen(command, stdout=PIPE, stderr=STDOUT, text=True)
            for line in process.stdout:
                f.write(line)
                f.flush()
            for err in process.stderr:
                f.write(err)
                f.flush()

    thread = Thread(target=_stream_logs)
    thread.start()
