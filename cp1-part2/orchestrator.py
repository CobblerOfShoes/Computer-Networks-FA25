import sys
import socket
import argparse
import sys
import time
import math
import logging
import os
import subprocess
import signal

from launch_workers import launch_workers

MAX_WORKERS = 5
workers = []
worker_processes: list[subprocess.Popen] = []
udp_sock: socket.socket = None
worker_sockets: list[socket.socket] = []

logging.basicConfig(
    format="[{asctime}] {levelname} - {message}",
    style="{",
    datefmt="%Y-%m-%d %H:%M",
)

def signal_handler(sig, frame):
    for worker in worker_processes:
        worker.terminate()
    if (udp_sock is not None):
        udp_sock.close()
    for socket in worker_sockets:
        if socket is not None:
            socket.close()
    while True:
        try:
            os.wait()
        except ChildProcessError:
            # No more child processes
            break
    sys.exit(0)

def alert_worker(message, worker):
    worker_sock = worker['socket']

    data = message.encode('utf-8')
    worker_sock.send(data)

    response = worker_sock.recv(2048)
    if not response:
        print("Socket Connection Broken")
        sys.exit(1)

    print(response.decode('utf-8'))
    return response

def add_worker(addr, text):
    if len(workers) <= MAX_WORKERS:
        text = text.split(' ')
        try:
          hostname = text[1]
          port = text[2]
          id = text[3]
          is_free = True

          worker_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
          worker_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
          print(f"Binding connection to {id} on port {port}")
          worker_sock.connect((hostname, int(port)))

          workers.append({'hostname': hostname,
                          'port': port,
                          'identifier': id,
                          'is_free': is_free,
                          'socket': worker_sock})
        except:
            print("ERROR: Incorrect number of arguments")
            return
    else:
        print("Error: More than {MAX_WORKERS} workers registered")
        return

def main():
    signal.signal(signal.SIGINT, signal_handler)

    parser = argparse.ArgumentParser(description='')
    parser.add_argument('port', type=int, help='The port number for the server')
    parser.add_argument('workers', type=int, help='The number of workers to summon')
    parser.add_argument('log_location', type=str, help='The location to store log files at')

    args = parser.parse_args()

    if args.port < 54000 or args.port > 54150:
        print("ERROR: Please choose a port between 54000 and 54150")
        sys.exit(1)

    #### Set up UDP listening socket
    SOCK = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print('Binding UDP listener to port ' + str(args.port))

    # Tell the OS we know what we are doing
    SOCK.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    host_ip = socket.gethostname()

    server_address = ('127.0.0.1', args.port)
    SOCK.bind(server_address)

    ### Set up the workers
    WORKER_PROCESSES = launch_workers(args.workers, args.log_location,
                                      '127.0.0.1', '127.0.0.1', args.port)

    tasks: dict = {}

    while True:
        data, addr = SOCK.recvfrom(1024)
        text = data.decode('utf-8')
        print(f"received message: {text}")

        # Worker is contacting Orchestrator for the first time
        if 'REGISTER' in text:
            add_worker(addr, text)

        # A client has submitted a request
        if 'CHECK' in text:
            available_worker = None
            for i, worker in enumerate(workers):
                if worker['is_free'] == True:
                    worker['is_free'] = False
                    available_worker = workers[i]
                    break

            if not available_worker:
                # Wait for an available worker
                child_pid, status = os.waitpid(-1, 0)
                available_worker = tasks[child_pid]
                available_worker['is_free'] = True
                del tasks[child_pid]

            pid = os.fork()
            if pid == 0:
                # We are the child
                response = alert_worker(text, available_worker).decode("utf-8")
                words = response.split()
                response = " ".join(words[2:])
                SOCK.sendto(response.encode("utf-8"), (addr))
                sys.exit(0)
            elif pid < 0:
                # Disaster
                sys.exit(pid)
            else:
                # We are the parent
                # Track which worker was assigned to which client
                tasks.update({pid: available_worker})



if __name__ == '__main__':
    main()