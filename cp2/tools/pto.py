import argparse
from find_tcp_max import header_length
import scapy.all as scapy

def trim_packets(filename):
    packets = scapy.rdpcap(filename)
    
    for packet in packets:
        pkt_len = header_length(packet)
        new_packet = bytes(packet)[:pkt_len]
        new_filename = filename.split('/')
        new_filename = '/'.join(new_filename[:-1]) + '/pto-' + new_filename[-1]
        scapy.wrpcap(f"{new_filename}", new_packet, append=True)
        

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Find the maximum TCP header length in a pcap file.")
    parser.add_argument("pcap_file", help="Path to the pcap file to analyze.")
    args = parser.parse_args()
    
    trim_packets(args.pcap_file)