# Contributions:
- Alex Schumann: Updating the worker and making the bonus scripts
- Tim Parisi: Making the orchestrator and the new client

# To run the code:
- Make sure to navigate into the cp1-part2 directory!
- run "$ make all" to compile the file
- In one terminal: run "$ python3 orchestratoy.py"
    - arguments:
        1) Port number to run the server on
- In another terminal: run "$ python3 launch_workers.py"
    - arguments:
        1) ip address of server
        2) port of server
        3) ip address of client
        4) port of client
        5) number of workers to spawn
        6) logging location
    - notes:
        The workers run with sequential port numbers, so please keep the worker starting port higher than the orchestrator starting port
- In a third terminal: choice of scripts
    run "$ python3 client-v2.py"
    - arguments:
        1) url to scan
        2) string to scan for
        3) site identifier
        4) AdID Password
        5) --port=SERVER_PORT_NUMBER
    run "$ python3 check-hits.py"
    - arguments:
        1) ip address of server
        2) port of server
        3) last n-th hits to check
    run "$ python3 pool_status.py"
    - arguments:
        1) ip address of server
        2) port of server

Note:
  From our understanding, the orchestrator is not supposed to call the launch_workers.py script. However, it would be fairly easy to copy the arguments of launch_workers.py to orchestrator.py and have the orchestrator call the script.

# Bonus Features

Alex:
  Heartbeat to have the launch workers script poll children and have the children poll the orchestrator
Tim:
  Password Protection: User must input a password to access previously seen AdID's