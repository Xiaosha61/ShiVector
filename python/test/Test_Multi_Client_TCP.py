#!/usr/bin/python

import logging
log = logging.getLogger(__name__)
import sys
import socket
import mock
import unittest
import vlib.SVSocket as SVSocket
import vlib.Patch as Patch

"""
  Test sending a message which will call the SVSocket subclass functions through the patch
  Note: Start threadpool.ThreadPool before running this test
"""
class Test_Multi_Client_TCP(unittest.TestCase):
 
  def test_Send(self):
    """
    Instantiate multiple instances of SVSocket through the patch and send a message
    to the ThreadPool server
    """
    # Loop 10 times and send out 10 client requests      
    for x in range(0, 9):
        # Create a test socket that is actually an instance of SVSocket
        self.testSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
     
        # Assert that self.testSocket is of the type SVSocket
        self.assertEqual(self.testSocket.__class__, SVSocket.SVSocket)
      
        # Connect to the ThreadPool
        self.testSocket.connect(("127.0.0.1", 12468))
        # Send a numbered message
        self.testSocket.send("MESSAGE %d " % (x))
        print "Test_Multi_Client_TCP SEND "

        self.testSocket.close()

if __name__ == '__main__':
  unittest.main()
