import subprocess
import argparse
import sys
import time
import signal
import os
import shutil
from pathlib import Path

workers: list[subprocess.Popen] = []

def signal_handler(sig, frame):
    # Clean up processes
    for worker in workers:
        worker.terminate()

    # Clean worker states
    if os.path.exists('./worker_states'):
       shutil.rmtree('./worker_states')

    sys.exit(0)

def main():
  signal.signal(signal.SIGINT, signal_handler)

  parser = argparse.ArgumentParser(description='')
  parser.add_argument('orchestrator_ip', type=str, help='The IP address of the orchestrator')
  parser.add_argument('orchestrator_port', type=int, help='The port number for the orchestrator')
  parser.add_argument('worker_ip', type=str, help='The ip address for the workers')
  parser.add_argument('worker_ports', type=int, help='The port number for the workers')
  parser.add_argument('num_workers', type=int, help='The number of workers to launch')
  parser.add_argument('log_location', type=str, help='The directory to store log files in')

  args = parser.parse_args()

  if (args.num_workers < 0 or args.num_workers > 5):
    print("Number of desired workers is outside the range 1-5, starting 5 workers...")
    args.num_workers = 5

  status_directory = Path('./worker_states')
  status_directory.mkdir(exist_ok=True)

  for i in range(args.num_workers):
    workerID = f"Worker{i}"
    workerPort = str(int(args.worker_ports) + i)
    command = ["./adChecker", workerPort, args.log_location,
               args.worker_ip, args.orchestrator_ip, str(args.orchestrator_port),
               workerID]
    worker = subprocess.Popen(command)
    workers.append(worker)

  # Do nothing until the program is killed, allows for cleanup of workers
  while True:
     time.sleep(10)

if __name__ == "__main__":
  main()