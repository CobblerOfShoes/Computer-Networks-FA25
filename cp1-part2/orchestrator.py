import sys
import socket
import argparse
import sys
import time
import math
import logging
import os
from threading import Thread, Lock
import queue

threads = []
work_queue = queue.Queue()
resp_queue = queue.Queue()
lock = Lock()



def main():
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('port', type=int, help='The port number for the server')
    parser.add_argument('workers', type=int, help='The number of workers to summon')
    parser.add_argument('--verbose', help='Enable verbose output', action="store_true")

    args = parser.parse_args()

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    if args.verbose:
        print('Binding to port ' + str(args.port))

    server_address = ('', args.port)
    sock.bind(server_address)
    if args.verbose: 
        print('Success!')

    t = Thread(target=resp_process)
    threads.append(t)
    t.start()

    while True:
        try:
            data, addr = sock.recvfrom(1024)
            text = data.decode('utf-8')
            if args.verbose: 
                print(f"received message: {text}")
            if 'REGISTER' in text:
                t = Thread(target=worker_process, args=text[1:])
                threads.append(t)
                t.start()
                if args.verbose: 
                    print(text[1:])
            if 'CHECK' in text:
                work_queue.put((text, addr))
        except Exception as e:
            for t in threads:
                t.close()
            if args.verbose: 
                print(f'Exception: {e}', file=sys.stderr)
            sys.exit(1)

def alert_worker(message, hostname, port):
    worker_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print(f"Binding to port {port}")
    port = int(port)
    worker_sock.connect((hostname, port))
    print('Connected! Sending Message...')
    data = message.encode('utf-8')
    worker_sock.send(data)
    
    response = worker_sock.recv(2048)
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
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    while True:
        try:
            response, addr = resp_queue.get()
            sock.sendto(response, (addr))
        finally:
            resp_queue.task_done()

if __name__ == '__main__':
    main()