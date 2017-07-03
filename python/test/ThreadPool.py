#!/usr/bin/python

# From Python Cookbook, p.506
import logging
log = logging.getLogger(__name__)
import mock
import socket
from concurrent.futures import ThreadPoolExecutor
import unittest
import vlib.Patch as Patch
import sys

    
def echo_client(sock, client_addr):
  '''
  Handle a client connection
  '''
  while True:
      msg = sock.recv(65536)
      print "\nRECV threadpool message " + msg
      log.debug("\n\nMessage is %d" % msg)

      if not msg:
        break
        
      sock.sendall(msg)
    
  log.debug("Client closed connection")
  print "******* End Thread Pool Tests ************ "

  sock.close()

def echo_server(addr):
  pool = ThreadPoolExecutor(128)
  print "******* Starting Thread Pool Tests ************ "
  # Create a test socket which is actually of type SVSocket
  sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
  # Bind the socket to the test address where Test_Multi_Client is waiting
  sock.bind(addr)
  log.debug((" Thread Pool Bound ", addr))
  sock.listen(5)
  log.debug("Listening.......")

  while 1:
        client_sock, client_addr = sock.accept()
        pool.submit(echo_client, client_sock, client_addr)


echo_server(('',12468))

