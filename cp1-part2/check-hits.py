import argparse
import socket

def main():
  parser = argparse.ArgumentParser(description='')
  parser.add_argument('ip', type=str, help='The ip address of the server')
  parser.add_argument('port', type=int, help='The port number for the server')
  parser.add_argument('num_hits', type=int, help='The last n hits to check (up to 5)')

  args = parser.parse_args()

  if args.num_hits < 0 or args.num_hits > 5:
    args.num_hits = 5

  with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
    s.connect((args.ip, int(args.port)))

    theRequest = f"HITS {args.num_hits}\r\n\r\n"

    s.send(theRequest.encode("utf-8"))

    response = s.recv(1024)

    print(response.decode("utf-8"))



if __name__ == '__main__':
  main()