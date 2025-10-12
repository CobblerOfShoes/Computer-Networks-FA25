import sys
import socket
import argparse
import sys
import logging
import os
import subprocess
import signal

from datetime import datetime

MAX_WORKERS = 5
workers: dict[str: dict] = {}

# The following are globals such that the signal handler can do cleanup
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

def update_latest_hits(worker_id, site_id, ad_string, time):
    lines = []
    with open('./worker_states/hits', 'a+') as f:
        f.seek(0)
        lines = f.readlines()
        if len(lines) > 4:
            lines = lines[1:]

    newline = str(worker_id) + " " + str(site_id) + " " + str(ad_string) + " " + str(time)
    lines.append(newline)

    new_list = []
    for line in lines:
        if line.endswith('\n'):
            new_list.append(line)
        else:
            new_list.append(line + '\n')

    with open('./worker_states/hits', 'w') as f:
        f.writelines(new_list)


def alert_worker(message, worker, worker_id):
    worker_sock = worker['socket']

    worker['last_job_time'] = datetime.now().strftime("%Y-%m-%d %H-%M-%S")
    data = message.encode('utf-8')
    worker_sock.send(data)

    response = worker_sock.recv(2048)
    if not response:
        print("Socket Connection Broken")
        sys.exit(1)
    worker['last_response_time'] = datetime.now().strftime("%Y-%m-%d %H-%M-%S")

    with open(f'./worker_states/{worker_id}', 'w') as f:
        f.write(str({worker_id: worker}))

    words = response.decode("utf-8").split()

    update_latest_hits(worker_id, words[5], words[2], worker['last_response_time'])

    response = " ".join(words[3:])

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

          workers.update({id: {'hostname': hostname,
                              'port': port,
                              'is_free': is_free,
                              'socket': worker_sock}})
        except:
            print("ERROR: Incorrect number of arguments")
            return
    else:
        print("Error: More than {MAX_WORKERS} workers registered")
        return

def send_status_info(addr, udp_sock):
    response = ""
    for filename in os.listdir('./worker_states'):
        file_path = os.path.join('./worker_states', filename)
        with open(file_path, 'r', encoding="utf-8") as f:
            response += f.read()

    if not response.strip():
        response = "No data yet"

    udp_sock.sendto(response.encode("utf-8"), (addr))

def send_last_hits(addr, udp_sock, n_hits):
    response = ""
    with open('./worker_states/hits', 'a+') as f:
        f.seek(0)
        response = f.readlines()

    if not response:
        response = "No hits yet"
    else:
        try:
            response = response[-int(n_hits):]
        except IndexError:
            # Keep the response as is
            response = response

    response = "".join(response)

    udp_sock.sendto(response.encode("utf-8"), (addr))

def main():
    signal.signal(signal.SIGINT, signal_handler)

    parser = argparse.ArgumentParser(description='')
    parser.add_argument('port', type=int, help='The port number for the server')

    args = parser.parse_args()

    if args.port < 54000 or args.port > 54150:
        print("ERROR: Please choose a port between 54000 and 54150")
        sys.exit(1)

    #### Set up UDP listening socket
    udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print('Binding UDP listener to port ' + str(args.port))

    # Tell the OS we know what we are doing
    udp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    host_ip = socket.gethostname()

    server_address = ('127.0.0.1', args.port)
    udp_sock.bind(server_address)

    tasks: dict = {}

    while True:
        data, addr = udp_sock.recvfrom(1024)
        text = data.decode('utf-8')
        print(f"received message: {text}")

        # Worker is contacting Orchestrator for the first time
        if 'REGISTER' in text:
            add_worker(addr, text)

        # Send back status info
        if 'STATUS' in text:
            send_status_info(addr, udp_sock)

        # Send back last nth hits
        if 'HITS' in text:
            num_hits = text.split()[1]
            send_last_hits(addr, udp_sock, num_hits)

        if 'PING' in text:
            response = "PONG\r\n\r\n".encode("utf-8")
            udp_sock.sendto(response, (addr))

        # A client has submitted a request
        if 'CHECK' in text:
            available_worker = None
            worker_id = None
            for worker_name, worker in workers.items():
                if worker['is_free'] == True:
                    worker['is_free'] = False
                    available_worker = worker
                    worker_id = worker_name
                    break

            if not available_worker:
                # Wait for an available worker
                child_pid, status = os.waitpid(-1, 0)
                worker_id, available_worker = tasks[child_pid]
                available_worker['is_free'] = True
                del tasks[child_pid]

            pid = os.fork()
            if pid == 0:
                # We are the child
                response = alert_worker(text, available_worker, worker_id)
                udp_sock.sendto(response.encode("utf-8"), (addr))
                sys.exit(0)
            elif pid < 0:
                # Disaster
                sys.exit(pid)
            else:
                # We are the parent
                # Track which worker was assigned to which client
                tasks.update({pid: (worker_id, available_worker)})



if __name__ == '__main__':
    main()