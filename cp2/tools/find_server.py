import find_client
import argparse
from find_client import main

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Find client IP addresses from pcap files.")
    parser.add_argument("pcap_file", help="Path to the pcap file to analyze.")
    args = parser.parse_args()

    main(args.pcap_file, find_client=False)