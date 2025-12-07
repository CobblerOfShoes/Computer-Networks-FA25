import argparse
import os

import scapy.all as scapy

import dpkt
import socket

def mac_addr_format(mac_bytes):
  return ':'.join('%02x' % b for b in mac_bytes)

def count_tcp_retransmissions(filename):
  with open(filename, 'rb') as f:
    pcap = dpkt.pcap.Reader(f)
    tcp_flow_info = {
      'ack_freq': {}, 'seq_numbers': {},
      'retransmissions': 0, 'seen_seqs': {},
      'server_ip': None, 'access_point': None
    }

    packet_count = 0

    for timestamp, buf in pcap:
      packet_count += 1
      # Parse the packet
      eth = dpkt.ethernet.Ethernet(buf)
      # Ensure the packet is an IP packet
      if not isinstance(eth.data, dpkt.ip.IP):
          continue
      ip = eth.data
      # Ensure the packet is a TCP packet
      if not isinstance(ip.data, dpkt.tcp.TCP):
          continue
      tcp = ip.data

      # Extract relevant information from the packet
      src_ip = socket.inet_ntoa(ip.src)
      dst_ip = socket.inet_ntoa(ip.dst)

      if src_ip.startswith('129.74'):
        server_ip = src_ip
      else:
        server_ip = dst_ip

      if tcp_flow_info['server_ip'] is None:
        tcp_flow_info['server_ip'] = server_ip

      # Update the access point if we are coming from the client
      if (tcp_flow_info['access_point'] is None) and (src_ip != tcp_flow_info['server_ip']):
        tcp_flow_info['access_point'] = mac_addr_format(eth.dst)

      # I think this will be duplicated with the duplicate sequence number checking

      # if (tcp.flags & dpkt.tcp.TH_ACK) and not (tcp.flags & dpkt.tcp.TH_SYN):
      #   ack = tcp.ack
      #   # Track ACKs for triple duplicate detection
      #   if ack not in flow['ack_freq']:
      #     flow['ack_freq'][ack] = 1
      #   else:
      #     flow['ack_freq'][ack] += 1
      #     current_ack_freq = flow['ack_freq'][ack]
      #     if current_ack_freq == 4:  # Triple duplicate ACK detected
      #       flow['retransmissions'] += 1

      # Look for duplicate sequence numbers to detect retransmissions
      if src_ip == tcp_flow_info['server_ip']:
        seq = tcp.seq
        if seq in tcp_flow_info['seen_seqs'] and tcp_flow_info['seen_seqs'][seq] is True:
          # If the sequence number has been seen before, it's a retransmission
          tcp_flow_info['retransmissions'] += 1
          tcp_flow_info['seen_seqs'][seq] = False
        else:
          # Otherwise, mark the sequence number as seen
          tcp_flow_info['seen_seqs'][seq] = True

  return (tcp_flow_info, packet_count)

def main():
  parser = argparse.ArgumentParser(description="Prune only the TCP Packets in a pcap to remove payload data.")
  parser.add_argument("pcap_dir", help="Path to the directory containing pcap files to analyze.")
  args = parser.parse_args()

  pcap_dir = args.pcap_dir

  pcap_filepaths = [os.path.join(pcap_dir, filename) for filename in os.listdir(args.pcap_dir) if filename.endswith('.pcap')]

  aggregated_info = []

  # Get info on each file
  for file in pcap_filepaths:
    tcp_flow_info = count_tcp_retransmissions(file)
    aggregated_info.append(tcp_flow_info)
    print(f"=== Capture Info for File: {file} ===")
    print(f"Number of packets in file: {tcp_flow_info[1]}")
    print(f"Number of TCP Retransmissions found within the file: {tcp_flow_info[0]['retransmissions']}")

  # Get info grouped by server and access point
  info_grouped_by_server = {}
  info_grouped_by_access_point = {}
  for info in aggregated_info:
    server_ip = info[0]['server_ip']
    if server_ip in info_grouped_by_server.keys():
      info_grouped_by_server[server_ip].append(info)
    else:
      info_grouped_by_server[server_ip] = [info]

    access_point = info[0]['access_point']
    if access_point in info_grouped_by_access_point.keys():
      info_grouped_by_access_point[access_point].append(info)
    else:
      info_grouped_by_access_point[access_point] = [info]

  # Display server info
  sorted_server_info = {}
  for server, info_list in info_grouped_by_server.items():
    retransmission_counts = [info[0]['retransmissions'] for info in info_list]
    min_retransmissions = min(retransmission_counts)
    max_retransmissions = max(retransmission_counts)
    mean_retransmissions = sum(retransmission_counts) / len(retransmission_counts)
    median_retransmissions = retransmission_counts[len(retransmission_counts)//2]
    sorted_server_info[server] = {'min': min_retransmissions,
                                  'max': max_retransmissions,
                                  'mean': mean_retransmissions,
                                  'median': median_retransmissions,
                                  'num_requests': len(info_list)}

  for server, info in sorted(sorted_server_info.items(), key=lambda x: x[1]['median']):
    print(f"=== Displaying data for server {server} ===")
    print(f"Mininum retransmission counts: {info['min']}")
    print(f"Maximum retransmission counts: {info['max']}")
    print(f"Mean retransmission counts: {info['mean']}")
    print(f"Median retransmission counts: {info['median']}")
    print(f"Number of requests to this server: {info['num_requests']}")

  # Display access point info
  sorted_access_point_info = {}
  for access_point, info_list in info_grouped_by_access_point.items():
    retransmission_counts = [info[0]['retransmissions'] for info in info_list]
    min_retransmissions = min(retransmission_counts)
    max_retransmissions = max(retransmission_counts)
    mean_retransmissions = sum(retransmission_counts) / len(retransmission_counts)
    median_retransmissions = retransmission_counts[len(retransmission_counts)//2]
    sorted_access_point_info[access_point] = {'min': min_retransmissions,
                                              'max': max_retransmissions,
                                              'mean': mean_retransmissions,
                                              'median': median_retransmissions,
                                              'num_requests': len(info_list)}

  for access_point, info in sorted(sorted_access_point_info.items(), key=lambda x: x[1]['median']):
    print(f"=== Displaying data for access point {access_point} ===")
    print(f"Mininum retransmission counts: {info['min']}")
    print(f"Maximum retransmission counts: {info['max']}")
    print(f"Mean retransmission counts: {info['mean']}")
    print(f"Median retransmission counts: {info['median']}")
    print(f"Number of requests to this access point: {info['num_requests']}")




if __name__ =='__main__':
  main()