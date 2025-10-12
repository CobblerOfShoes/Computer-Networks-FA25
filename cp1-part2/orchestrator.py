import sys
import socket
import argparse
import sys
import time
import math
import logging
import os
from threading import Thread, Lock
from datetime import datetime
import queue
import subprocess
import signal
import json

threads = []
work_queue = queue.Queue()
resp_queue = queue.Queue()
lock = Lock()

def signal_handler(sig, frame):
    for t in threads:
        t.close()
        sys.exit(sig)

def main():
    signal.signal(signal.SIGINT, signal_handler)

    parser = argparse.ArgumentParser(description='')
    parser.add_argument('port', type=int, help='The port number for the server')
    parser.add_argument('workers', type=int, help='The number of workers to summon')
    parser.add_argument('--verbose', help='Enable verbose output', action="store_true")

    args = parser.parse_args()

    if args.port < 54000 or args.port > 54150:
        print("ERROR: Please choose a port between 54000 and 54150")
        sys.exit(1)

    udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    if args.verbose:
        print('Binding to port ' + str(args.port))

    udp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    server_address = ('', args.port)
    udp_sock.bind(server_address)
    if args.verbose:
        print('Success!')

    t = Thread(target=resp_process)
    threads.append(t)
    t.start()

    while True:
        try:
            data, addr = udp_sock.recvfrom(1024)
            text = data.decode('utf-8')
            if args.verbose:
                print(f"received message: {text}")
            if 'REGISTER' in text:
                t = Thread(target=worker_process, args=text[1:])
                threads.append(t)
                t.start()
                if args.verbose:
                    print(text[1:])

                # Send back status info

            if 'STATUS' in text:
                send_status_info(addr, udp_sock)

            # Send back last nth hits
            if 'HITS' in text:
                num_hits = text.split()[1]
                send_last_hits(addr, udp_sock, num_hits)

            if 'CHECK' in text:
                work_queue.put((text, addr))
        except Exception as e:
            for t in threads:
                t.close()
            if args.verbose:
                print(f'Exception: {e}', file=sys.stderr)
            sys.exit(1)

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

def send_status_info(addr, udp_sock):
    response = ""
    for filename in os.listdir('./worker_states'):
        file_path = os.path.join('./worker_states', filename)
        with open(file_path, 'r', encoding="utf-8") as f:
            response += f.read()

    if not response.strip():
        response = "No data yet"

    udp_sock.sendto(response.encode("utf-8"), (addr))

def alert_worker(message, hostname, port):
    worker_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    starttime = datetime.now().strftime("%Y-%m-%d %H-%M-%S")
    print(f"Binding to port {port}")
    port = int(port)
    worker_sock.connect((hostname, port))
    print('Connected! Sending Message...')
    data = message.encode('utf-8')
    worker_sock.send(data)
    response = worker_sock.recv(2048)
    endtime = datetime.now().strftime("%Y-%m-%d %H-%M-%S")
    worker_sock.close()
    if not response:
        print("Socket Connection Broken")
        sys.exit(1)

    print(response.decode('utf-8'))
    return response

def worker_process(hostname, port):
    while True:
        try:
            message = work_queue.get()
            response = alert_worker(message, hostname, port)
            resp_queue.put(response)
        finally:
            work_queue.task_done()

def resp_process():
    udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    while True:
        try:
            response, addr = resp_queue.get()
            udp_sock.sendto(response, (addr))
        finally:
            resp_queue.task_done()

if __name__ == '__main__':
    main()