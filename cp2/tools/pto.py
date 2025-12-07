import argparse
from find_tcp_max import header_length
import scapy.all as scapy

import os
import sys

import focus_filter

def trim_packets(filename, packets):
    if not os.path.isfile(filename):
        print(f"ERROR: Could not find file {filename}")
        sys.exit(1)

    new_filename = filename.split('/')
    new_filename = '/'.join(new_filename[:-1]) + '/pto-' + new_filename[-1]

    with scapy.PcapWriter(new_filename, append=True, sync=True) as wr:
        for packet in packets:
            # Prune TCP Only (trim payload)
            if scapy.TCP in packet:
                pkt_len = header_length(packet)
                new_packet = bytes(packet)[:pkt_len]
                # Something about the below lines does not work and I don't know why
                #new_packet = packet.copy()
                #new_packet = new_packet[scapy.TCP].remove_payload()
                wr.write(new_packet)
            # Leave other packet types alone
            else:
                wr.write(packet)

def main():
    parser = argparse.ArgumentParser(description="Prune only the TCP Packets in a pcap to remove payload data.")
    parser.add_argument("pcap_file", help="Path to the pcap file to analyze.")
    args = parser.parse_args()

    trim_packets(args.pcap_file, scapy.PcapReader(args.pcap_file))

    # The following will first filter out relevant packets and then trim them
    # trim_packets(args.pcap_file, focus_filter.filter_tcp(args.pcap_file))

if __name__ == "__main__":
    main()