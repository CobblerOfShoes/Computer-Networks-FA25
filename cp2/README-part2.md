# 1 -- Setup

To begin, please start by creating a virtual environment with the following steps:
1) `cd cp2`
2) `python3 -m venv cp2_env`
3) `source cp2_env/bin/activate`
4) `pip3 install -r requirements.txt`

# 2 -- Running the Code

### For the boutique tools:
`cd tools`
`python3 find_client.py packets/PACKET_NAME`
- Replace PACKET_NAME with the pcap file that you want to find the client of
- Assumes that the server is in the ip range 127.74.x.x
`python3 find_server.py packets/PACKET_NAME`
- Replace PACKET_NAME with the pcap file that you want to find the server of
- Assumes that the server is in the ip range 127.74.x.x
`python3 find_tcp_max.py packets/PACKET_NAME`
- Replace PACKET_NAME with the pcap file that you want to get the max tcp header length of
- Prints out one max that is the global tcp header max across the pcap
`python3 focus_filter.py packets/PACKET_NAME`
- Replace PACKET_NAME with the pcap file that you want to get the relavant packets of
- Removes any packets not between the client and server
- This script on its on can take upwards of 5 minutes on a 200 MB pcap as we copy nearly every packet
`python3 pto.py packets/PACKET_NAME`
- Replace PACKET_NAME with the pcap file that you want to get the relavant packets of
- Trims out TCP payloads
- On its own, based on the directions we did not set up this script to first filter down the PCAP
- When using pto's trim_packets in another script, you can pass in focus_filters's filter_tcp as the generator to both filter and trim packets
`python3 packet-smash.py PACKET_DIR`
- Replace PACKET_DIR with the directory containing the pcaps to smash
- The .tar.gz will be placed in the PACKET_DIR
- Running this on two pcaps of around 200 MB each took 5 minutes 22 seconds


### For the advanced analytics:
`cd ../analytics`
`python3 requestTimer.py --ip <ip> --port <port>`
- Note that our server is currently configured to run on port 54011

### Results
Inside the "results" folder:
- cmd/: output of requestTimer.py
- info.md: Information about each capture

# 3 -- Contributions

## Alex


## Tim


