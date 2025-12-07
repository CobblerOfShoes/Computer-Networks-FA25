import scapy.all as scapy
from scapy.layers.inet import TCP, IP
from scapy.layers import l2
import sys
import argparse

def header_length(packet):
    total_length = 0
    if packet.haslayer(TCP):
        tcp_layer = packet[TCP]
        data_offset = tcp_layer.dataofs  # in 32-bit words
        header_length_bytes = data_offset * 4  # convert to bytes
        total_length += header_length_bytes
    if packet.haslayer(IP):
        ip_layer = packet[IP]
        ip_header_length = ip_layer.ihl * 4  # in bytes
        total_length += ip_header_length
    if packet.haslayer(l2.Ether):
        eth_layer = packet[l2.Ether]
        eth_header_length = 14  # Ethernet header is always 14 bytes
        total_length += eth_header_length
    
    return total_length
    
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Find the maximum TCP header length in a pcap file.")
    parser.add_argument("pcap_file", help="Path to the pcap file to analyze.")
    args = parser.parse_args()
    
    packets = scapy.rdpcap(args.pcap_file)
    for packet in packets:
        print(header_length(packet))