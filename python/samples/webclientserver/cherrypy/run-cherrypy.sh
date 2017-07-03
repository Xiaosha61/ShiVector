#!/bin/bash

# Set python path to a location that includes vlib:
PYTHONPATH=$PYTHONPATH:../../../

# Set environment variable for shivector.conf
export SHIVECTORCONFPATH=$PWD/shivector.conf

# Now run the cherrypy server:
python server.py



