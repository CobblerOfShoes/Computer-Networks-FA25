import scapy.all as scapy
from scapy.layers.inet import IP, TCP
import argparse
import sys

TCP_SYN_FLAG = 2

def main(filename, find_client=True):
    try:
        packets = scapy.rdpcap(filename)
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        sys.exit(1)

    for packet in packets:
        if packet.haslayer(TCP) and packet.haslayer(IP):
            if packet[TCP].flags & TCP_SYN_FLAG and (packet[TCP].dport > 54000 and packet[TCP].dport < 54500):  # SYN flag
                if find_client:
                    print("HI")
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