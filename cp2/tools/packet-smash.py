import sys
import argparse
import scapy.all as scapy
import pto
import os
import gzip
    
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Find client IP addresses from pcap files.")
    parser.add_argument("pcap_dir", help="Path to the pcap directory to smash.")
    args = parser.parse_args()
    
    packet_files = [filename for filename in os.listdir(args.pcap_dir) if filename.endswith('.pcap')]
    output_file = os.path.join(args.pcap_dir, "smashed_packets.pcap")

    for filename in packet_files:
        full_path = os.path.join(args.pcap_dir, filename)
        pto.trim_packets(full_path)
        
    output_data = scapy.PacketList()
    
    pto_files = [filename for filename in os.listdir(args.pcap_dir) if filename.endswith('.pcap') and filename.startswith('pto-')]
    for filename in pto_files:
        full_path = os.path.join(args.pcap_dir, filename)
        packets = scapy.rdpcap(full_path)
        output_data.extend(packets)
    
    with open ('smashed_packets.tar.gz', 'wb') as output:
        data = gzip.compress(output_data.encode())
        output.write(data)
    
    print(f"Smashed packets written to 'smashed_packets.tar.gz'")
    print("Cleaning temporary pto files...")
    for filename in pto_files:
        os.remove(os.path.join(args.pcap_dir, filename))
    os.remove('smashed_packets.pcap')
