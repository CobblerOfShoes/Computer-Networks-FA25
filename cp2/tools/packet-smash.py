import sys
import argparse
import scapy.all as scapy
import os
import gzip

import tarfile

import focus_filter
import pto

def main():
    parser = argparse.ArgumentParser(description="Filter pcaps, trim TCP packets, and then bundle the outputs.")
    parser.add_argument("pcap_dir", help="Path to the pcap directory to smash.")
    args = parser.parse_args()

    packet_files = [filename for filename in os.listdir(args.pcap_dir) if filename.endswith('.pcap')]
    output_file = os.path.join(args.pcap_dir, "smashed_packets.tar.gz")

    for filename in packet_files:
        full_path = os.path.join(args.pcap_dir, filename)
        pto.trim_packets(full_path, focus_filter.filter_tcp(full_path))

    output_data = scapy.PacketList()

    pto_files = [os.path.join(args.pcap_dir, filename) for filename in os.listdir(args.pcap_dir) if filename.endswith('.pcap') and filename.startswith('pto-')]

    with tarfile.open(output_file, "w:gz") as tar:
        for file_path in pto_files:
            tar.add(file_path, arcname=os.path.basename(file_path))

    print(f"Smashed packets written to {output_file}")
    print("Cleaning temporary pto files...")
    for filename in pto_files:
        os.remove(filename)

if __name__ == "__main__":
    main()
