import sys
import socket
import argparse
import sys
import time
import math
import logging
import os

parser = argparse.ArgumentParser(description='')
parser.add_argument('port', type=int, help='The port number for the server')

args = parser.parse_args()

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print('Binding to port ' + str(args.port))

server_address = ('', args.port)
sock.bind(server_address)
print('Success!')
sock.listen(5)
while True:
    try:
        print('Listening for connections...')
        connection, client_address = sock.accept()
        print('Accepted! Receiving Data')
        data = connection.recv(1024)
        print('Received! Responding...')
        message = 'Hello World!'.encode('utf-8')
        connection.sendall(message)
        print("Sent! Closing connection")
        connection.close()
    except Exception as e:
        sock.close()
        sys.exit(1)