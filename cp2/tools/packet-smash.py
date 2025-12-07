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
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output.")
    parser.add_argument("pcap_dir", help="Path to the pcap directory to smash.")
    args = parser.parse_args()

    packet_files = [filename for filename in os.listdir(args.pcap_dir) if filename.endswith('.pcap')]
    old_size = sum(os.path.getsize(os.path.join(args.pcap_dir, f)) for f in packet_files)
    print(f"Original size of pcaps: {old_size} bytes")
    output_file = os.path.join(args.pcap_dir, "smashed_packets.tar.gz")

    if args.verbose:
        print(f'Trimming packets in directory: {args.pcap_dir}')
    for filename in packet_files:
        full_path = os.path.join(args.pcap_dir, filename)
        pto.trim_packets(full_path, focus_filter.filter_tcp(full_path))

    output_data = scapy.PacketList()

    pto_files = [os.path.join(args.pcap_dir, filename) for filename in os.listdir(args.pcap_dir) if filename.endswith('.pcap') and filename.startswith('pto-')]

    with tarfile.open(output_file, "w:gz") as tar:
        for file_path in pto_files:
            tar.add(file_path, arcname=os.path.basename(file_path))
    new_size = os.path.getsize(output_file)
    print(f"Smashed size of pcaps: {new_size} bytes")
    print(f"Compression Ratio: {(new_size / old_size)*100:.2f}%")

    print(f"Smashed packets written to {output_file}")
    print("Cleaning temporary pto files...")
    for filename in pto_files:
        os.remove(filename)

if __name__ == "__main__":
    main()
