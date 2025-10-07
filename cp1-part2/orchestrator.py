import sys
import socket
import argparse
import sys
import time
import math
import logging
import os

MAX_WORKERS = 5
WORKERS = []

logging.basicConfig(
    format="[{asctime}] {levelname} - {message}",
    style="{",
    datefmt="%Y-%m-%d %H:%M",
)

def alert_worker(message, worker):
    worker_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print(f"Binding to port {worker['port']}")
    worker['port'] = int(worker['port'])
    worker_sock.connect((worker['hostname'], worker['port']))
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
    
def add_worker(addr, text):
    if len(WORKERS) <= MAX_WORKERS:
        text = text.split(' ')
        try:
            WORKERS.append({'hostname': text[1], 
                            'port': text[2], 
                            'identifier': text[3],
                            'is_free': True})
        except:
            print("ERROR: Incorrect number of arguments")
            return
    else:
        print("Error: More than {MAX_WORKERS} workers registered")
        return

def main():
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('port', type=int, help='The port number for the server')
    parser.add_argument('workers', type=int, help='The number of workers to summon')

    args = parser.parse_args()

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print('Binding to port ' + str(args.port))

    server_address = ('', args.port)
    sock.bind(server_address)
    print('Success!')

    while True:
        data, addr = sock.recvfrom(1024)
        text = data.decode('utf-8')
        print(f"received message: {text}")
        if 'REGISTER' in text:
            add_worker(addr, text)
            print(WORKERS)

        if 'CHECK' in text:
            worker_name = ''
            for i, worker in enumerate(WORKERS):
                if worker['is_free'] == True:
                    worker['is_free'] = False
                    worker_name = WORKERS[i]
                    break
            if not worker_name:
                print("No workers free")
                continue
            pid = os.fork()
            if pid == 0:
                response = alert_worker(text, worker_name)
                sock.sendto(response, (addr))
                sys.exit(0)
            elif pid < 0:
                sys.exit(pid)
                
        

if __name__ == '__main__':
    main()