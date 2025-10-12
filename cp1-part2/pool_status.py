import argparse
import socket

def main():
  parser = argparse.ArgumentParser(description='')
  parser.add_argument('ip', type=int, help='The ip address of the server')
  parser.add_argument('port', type=int, help='The port number for the server')

  args = parser.parse_args()

  with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
    s.connect((args.ip, int(args.port)))

    theRequest = "STATUS\r\n\r\n"

    s.send(theRequest.encode("utf-8"))

    response = s.recv(1024)

    print(response.decode("utf-8"))



if __name__ == '__main__':
  main()