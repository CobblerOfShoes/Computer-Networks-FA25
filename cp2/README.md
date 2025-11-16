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
- info.md: Information about each capture

# 3 -- Contributions

## Alex

Creation of the Flask server

## Tim

Creation of testing scripts/ packet capture
