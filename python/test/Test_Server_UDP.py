#!/usr/bin/python

import logging
log = logging.getLogger(__name__)
import sys
import socket
import unittest
import vlib.SVSocket as SVSocket
import vlib.SVPrint as SVPrint

"""
  Simple test to receive 1 message from Test_Client_UDP.py
    that will patch socket.socket to SVSocket subclass functions
"""
class Test_Server_UDP(unittest.TestCase):
 
  def test_patchReceive(self):
    """
    Wait for 1 message from the client
    """
    # Create a test socket which is actually of type SVSocket
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
      
    # Assert that self.testSocket is indeed of the type SVSocket
    self.assertEqual(serverSocket.__class__, SVSocket.SVSocket)
    
    # Bind the socket to the test address where Test_Client_UDP is waiting
    host = "127.0.0.1"
    port = 12457
    serverSocket.bind((host, port))
    # Receive data from SVSocket which includes the message with vector timestamp
    data, addr = serverSocket.recvfrom(1024)
    log.debug(("\n\n**** Data received from Test_Client_UDP", data))
    serverSocket.close()
      
  def test_printClock(self):
    """
    Test that print is patched. Manually view in the sys log that the clock is printed.
    """
    # Assert that the built in print is indeed of the type SVPrint
    self.assertEqual(sys.stdout, SVPrint.SVPrint)
        
    # Test the print patch with the created serverSocket
    print "1. BUILTIN: Is there a vector clock at the end of this message? "
    print ("2. PRINT function: Is there a vector clock at the end of this message? ")

if __name__ == '__main__':
  unittest.main()