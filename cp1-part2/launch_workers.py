import subprocess

def launch_workers(num_workers: int, log_location: str,
                   worker_ip: str, orchestrator_ip: str, orchestrator_port):
  if (num_workers < 0 or num_workers > 5):
    print("Number of desired workers is outside the range 1-5, starting 5 workers...")
    num_workers = 5

  workers: list[subprocess.Popen] = []
  for i in range(num_workers):
    workerID = f"Worker{i}"
    workerPort = str(int(orchestrator_port) + (i + 1))
    command = ["./adChecker", workerPort, log_location,
               worker_ip, orchestrator_ip, str(orchestrator_port),
               workerID]
    worker = subprocess.Popen(command)
    workers.append(worker)

  return workers