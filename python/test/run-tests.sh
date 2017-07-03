#!/bin/bash

# Set python path to a location that includes vlib:
PYTHONPATH=$PYTHONPATH:../
# Set the location to find the shivector.conf
export SHIVECTORCONFPATH=$PWD/shivector.conf

# Run the Multi-threading server intially because it takes a few seconds to start up
python ThreadPool.py &

# Run the TCP Tests
python Test_Server_TCP.py &
python Test_Client_TCP.py

# Run the UDP Tests
python Test_Server_UDP.py &
python Test_Client_UDP.py

# Run the Multi-threading Client Tests
# The ThreadPool server (class) has 4 instances in the clock because it receives from 3
# unique IP+PID clients, whereas the multi_clients are aware of only their own instances
# eg. localProcessId{"c0a8014259380100": 27,"c0a801425e380100": 9,"c0a801425f380100": 9,"c0a8014260380100": 9}
python Test_Multi_Client_TCP.py
python Test_Multi_Client_TCP.py
python Test_Multi_Client_TCP.py

exit 1
