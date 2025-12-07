import scapy.all as scapy
from scapy.layers.inet import TCP, IP, Ether
from scapy.layers import l2
import sys
import argparse

def header_length(packet):
    total_length = 0

    eth = packet.getlayer(Ether)
    if eth:
        total_length += len(bytes(eth)) - len(bytes(eth.payload))

    ip = packet.getlayer(IP) or packet.getlayer(IP)
    if ip:
        total_length += len(bytes(ip)) - len(bytes(ip.payload))

    l4 = packet.getlayer(TCP)
    if l4:
        total_length += len(bytes(l4)) - len(bytes(l4.payload))

    return total_length

def main():
    parser = argparse.ArgumentParser(description="Find the maximum TCP header length in a pcap file.")
    parser.add_argument("pcap_file", help="Path to the pcap file to analyze.")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output.")
    args = parser.parse_args()

    pcap_filename = args.pcap_file

    max_tcp_header_length = 0

    for packet in scapy.PcapReader(pcap_filename):
      curr_header_length = header_length(packet)
      if curr_header_length > max_tcp_header_length:
          max_tcp_header_length = curr_header_length

    if args.verbose:
        print(f"Maximum TCP header length in {pcap_filename}: {max_tcp_header_length} bytes")

if __name__ == "__main__":
    main()