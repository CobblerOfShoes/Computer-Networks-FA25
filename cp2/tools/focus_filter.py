import scapy.all as scapy
from scapy.layers.inet import IP, TCP
import argparse
import sys
import find_client
import os

def main(filename, file_out):
    if not os.path.isfile(filename):
        print(f"ERROR: Could not find file {filename}")
        sys.exit(1)

    client_ip = find_client.main(filename, find_client=True)
    print(f"Client IP Address: {client_ip}")
    server_ip = find_client.main(filename, find_client=False)
    print(f"Server IP Address: {server_ip}")
    print("Filtering out all extra packets...")

    # Filter out packets not between client and server
    for packet in scapy.PcapReader(filename):
        if packet.haslayer(IP):
            if (packet[IP].src == client_ip and packet[IP].dst == server_ip) or (packet[IP].src == server_ip and packet[IP].dst == client_ip):
                scapy.wrpcap(file_out, packet, append=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Find client IP addresses from pcap files.")
    parser.add_argument("pcap_file", help="Path to the pcap file to analyze.")
    parser.add_argument("file_out", help="Path to the output pcap file.")
    args = parser.parse_args()

    main(args.pcap_file, args.file_out)