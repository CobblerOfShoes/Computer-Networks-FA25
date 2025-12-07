import argparse
from find_tcp_max import header_length
import scapy.all as scapy

import os
import sys

def trim_packets(filename):
    if not os.path.isfile(filename):
        print(f"ERROR: Could not find file {filename}")
        sys.exit(1)

    for packet in scapy.PcapReader(filename):
        # Prune TCP Only (trim payload)
        if scapy.TCP in packet:
          pkt_len = header_length(packet)
          new_packet = bytes(packet)[:pkt_len]
          new_filename = filename.split('/')
          new_filename = '/'.join(new_filename[:-1]) + '/pto-' + new_filename[-1]
          scapy.wrpcap(f"{new_filename}", new_packet, append=True)
        # Leave other packet types alone
        else:
          scapy.wrpcap(f"{new_filename}", packet, append=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Find the maximum TCP header length in a pcap file.")
    parser.add_argument("pcap_file", help="Path to the pcap file to analyze.")
    args = parser.parse_args()

    trim_packets(args.pcap_file)