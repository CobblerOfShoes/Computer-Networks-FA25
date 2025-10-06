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

def alert_worker(message, worker):
    worker_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    logging.log(f'Binding to port {worker['port']}')
    
    worker_sock.connect((worker['hostname'], 80))
    logging.log('Connected! Sending Message...')
    data = message.encode('utf-8')
    worker_sock.send(data)
    
    response = worker_sock(2048)
    if not response:
        logging.error("Socket Connection Broken")
        sys.exit(1)
    
    print(response.decode('utf-8'))
    return response
    
def add_worker(addr, text):
    if len(WORKERS) <= MAX_WORKERS:
        text = text.split(' ')
        WORKERS.append({'hostname': text[1], 
                        'port': text[2], 
                        'identifier': text[3],
                        'is_free': True})
    else:
        logging.error("Error: More than {MAX_WORKERS} workers registered")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('port', type=int, help='The port number for the server')
    parser.add_argument('workers', type=int, help='The number of workers to summon')

    args = parser.parse_args()

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    logging.log('Binding to port ' + str(args.port))

    server_address = ('', args.port)
    sock.bind(server_address)
    logging.log('Success!')

    while True:
        data, addr = sock.recvfrom(1024)
        text = data.decode('utf-8')
        logging.log(f"received message: {text}")
        if 'REGISTER' in text:
            add_worker(addr, text)

        if 'CHECK' in text:
            worker_name = ''
            for worker in WORKERS.values:
                if worker['is_free'] == True:
                    worker['is_free'] == False
                    work_name = worker['name']
                    break
            if not worker_name:
                logging.error("No workers free")
                sys.exit(1)
            pid = os.fork()
            if pid == 0:
                response = alert_worker(text, work_name)
                sock.sendto(response, (addr))
                sys.exit(0)
            elif pid < 0:
                sys.exit(pid)
                
        

if __name__ == '__main__':
    main()