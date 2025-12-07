import sys
import argparse
import scapy.all as scapy
import os
import gzip

import tarfile

import focus_filter
import pto

def main():
    parser = argparse.ArgumentParser(description="Find client IP addresses from pcap files.")
    parser.add_argument("pcap_dir", help="Path to the pcap directory to smash.")
    args = parser.parse_args()

    packet_files = [filename for filename in os.listdir(args.pcap_dir) if filename.endswith('.pcap')]
    output_file = os.path.join(args.pcap_dir, "smashed_packets.tar.gz")

    # # Create a separate output directory
    # output_directory_name = "smashed_packets"
    # try:
    #     os.mkdir(output_directory_name)
    # except Exception as e:
    #     print(f"ERROR: {e}")
    #     sys.exit(1)

    #output_fullpath = os.path.join(args.pcap_dir, output_directory_name)
    for filename in packet_files:
        full_path = os.path.join(args.pcap_dir, filename)
        pto.trim_packets(full_path, focus_filter.filter_tcp(full_path))

    output_data = scapy.PacketList()

    pto_files = [filename for filename in os.listdir(args.pcap_dir) if filename.endswith('.pcap') and filename.startswith('pto-')]
    # for filename in pto_files:
    #     full_path = os.path.join(args.pcap_dir, filename)
    #     packets = scapy.rdpcap(full_path)
    #     output_data.extend(packets)

    # with open (output_file, 'wb') as output:
    #     data = gzip.compress(output_data.encode())
    #     output.write(data)

    with tarfile.open(output_file, "w:gz") as tar:
        for file_path in pto_files:
            tar.add(file_path, arcname=os.path.basename(file_path))

    print(f"Smashed packets written to {output_file}")
    print("Cleaning temporary pto files...")
    for filename in pto_files:
        os.remove(os.path.join(args.pcap_dir, filename))
    #os.remove('smashed_packets.pcap')

if __name__ == "__main__":
    main()
