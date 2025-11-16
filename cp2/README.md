# 1 -- Setup

To begin, please start by creating a virtual environment with the following steps:
1) `cd cp2`
2) `python3 -m venv cp2_env`
3) `pip3 install -r requirements.txt`

# 2 -- Running the Code

### For the server:
`python3 server.py`
- The server will be running on localhost and a second IP, use that IP and port for the packet capture

### For the packet capture:
`python3 requestTimer.py --ip <ip> --port <port>`

### Results
Inside the "results" folder:
- cmd/: output of requestTimer.py
- wireshark/: Wireshark packet captures

please run this code from the cp2 directory to decompress the packet captures:
```
cd results/
tar -xzvf wireshark_captures.tar.gz
```

Output 1 was run with good wifi and output 2 with poor wifi

# 3 -- Contributions

## Alex

Creation of the Flask server

## Tim

Creation of testing scripts/ packet capture
