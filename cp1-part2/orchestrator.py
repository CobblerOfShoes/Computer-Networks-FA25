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
password_dict = {}

# def signal_handler(sig, frame):
#     print("SIGNAL HANDLER")
#     for t in threads:
#         t.join()
#     sys.exit(1)

def main():
    with open('./logs/usedIDs', 'r') as f:
        for line in f.readlines():
            data = line.strip().split(' ')
            password_dict[data[0]] = data[1] #Format: AdID Password

    # signal.signal(signal.SIGINT, signal_handler)

    parser = argparse.ArgumentParser(description='')
    parser.add_argument('port', type=int, help='The port number for the server')
    parser.add_argument('workers', type=int, help='The number of workers to summon')
    parser.add_argument('--verbose', help='Enable verbose output', action="store_true")

    args = parser.parse_args()

    if args.verbose:
        print("PASSWORDS:")
        print(password_dict)

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

    # Thread for sending results to clients
    t = Thread(target=resp_process, args=[udp_sock])
    threads.append(t)
    t.start()
    while True:
        try:
            data, addr = udp_sock.recvfrom(1024)
            text = data.decode('utf-8').split(' ')
            if args.verbose:
                print(f"received message: {text}")

            # Tracks worker registration
            if 'REGISTER' in text:
                print("AH")
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

            # Respond to heartbeat
            if 'PING' in text:
                print("Received heartbeat")
                response = "PONG\r\n\r\n".encode("utf-8")
                udp_sock.sendto(response, (addr))

            if 'CHECK' in text:
                print(text)
                ad_id = text[2]
                password = text[4][:-5]
                #print(f'PASSWORD-FREE STRING: {text[:-1] + [text[-1][-4:]]}')
                data=' '.join(text[:-1] + [text[-1][-4:]]).encode('utf-8')
                if ad_id not in password_dict:
                    print("AdID not registered, adding")
                    with open('./logs/usedIDs', 'a+') as f2:
                        save_str = ad_id + ' ' + password
                        f2.write(save_str + '\n')
                    password_dict[ad_id] = password
                    work_queue.put((data.decode('utf-8'), addr))
                elif ad_id in password_dict and password_dict[ad_id] != password:
                    print("Incorrect password for AdID")
                    resp_queue.put((("ERROR: Incorrect password for AdID " + ad_id).encode('utf-8'), addr))
                    print(resp_queue.qsize())
                else:
                    print('Found password')
                    work_queue.put((data.decode('utf-8'), addr))

        except Exception as e:
            print("CUSTOM EXCEPTION")
            if args.verbose:
                print(f'Exception: {e}', file=sys.stderr)
            raise(e)

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

def alert_worker(message, hostname, port, nickname):
    print(f"Alerting worker {nickname} at {hostname}:{port} with message: {message}")
    worker_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    starttime = datetime.now().strftime("%Y-%m-%d %H-%M-%S")
    print(f"Binding to port {port}")
    port = int(port)
    worker_sock.connect((hostname, port))
    print('Connected! Sending Message...')
    data = message[0].encode('utf-8')
    worker_sock.send(data)
    print("Request Sent, waiting for response...")
    response = worker_sock.recv(2048)
    endtime = datetime.now().strftime("%Y-%m-%d %H-%M-%S")
    worker_sock.close()
    if not response:
        print("Socket Connection Broken")
        sys.exit(1)

    print(response.decode('utf-8'))
    return response

def worker_process(hostname, port, nickname):
    while True:
        try:
            message = work_queue.get()
            response = alert_worker(message, hostname, port, nickname)
            resp_queue.put((response, message[1]))
        finally:
            work_queue.task_done()

def resp_process(udp_sock: socket.socket):
    with udp_sock:
        while True:
            try:
                data = resp_queue.get()
            except ValueError:
                continue
            print(data)
            response, addr = data
            print(f"Connecting to {addr}")
            print(f'Responding |{response.decode("utf-8")}| to {addr}')
            udp_sock.sendto(response, (addr))
            resp_queue.task_done()
            print("Done!")
            

if __name__ == '__main__':
    main()