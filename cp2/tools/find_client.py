import scapy.all as scapy
from scapy.layers.inet import IP, TCP
import argparse
import sys
import os

TCP_SYN_FLAG = 2

def main(filename, find_client=True):
    if not os.path.isfile(filename):
        print(f"ERROR: Could not find file {filename}")
        sys.exit(1)

    for packet in scapy.PcapReader(filename):
        if packet.haslayer(TCP) and packet.haslayer(IP):
            if packet[TCP].flags & TCP_SYN_FLAG and \
               packet[IP].dst.startswith('129.74') and \
               (packet[TCP].dport >= 54000 and packet[TCP].dport <= 54500):  # SYN flag
                if find_client:
                    print(packet[IP].src)
                    return packet[IP].src
                else:
                    print(packet[IP].dst)
                    return packet[IP].dst

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Find client IP addresses from pcap files.")
    parser.add_argument("pcap_file", help="Path to the pcap file to analyze.")
    args = parser.parse_args()

    main(args.pcap_file, find_client=True)