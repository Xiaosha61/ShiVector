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
  Note: Start Test_Server_TCP before running this test
"""
class Test_Client_TCP(unittest.TestCase):
 
  def test_Send(self):
    """
    Instantiate an instance of SVSocket through the patch and send a message
    to Test_Server_TCP
    """
    # Create a test socket that is actually an instance of SVSocket
    testSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
     
    # Assert that self.testSocket is indeed of the type SVSocket
    self.assertEqual(testSocket.__class__, SVSocket.SVSocket)
    
    # Connect to the server waiting at this test address
    testSocket.connect(("127.0.0.1", 16161))

    # Send a long enough message such that the receive in the server will require multiple loops
    testSocket.send("In June In JuneIn JuneIn JuneIn JuneIn JuneIn JuneIn JuneIn JuneIn JuneIn JuneIn JuneIn JuneIn JuneIn JuneIn JuneIn JuneIn JuneIn JuneIn JuneIn JuneIn JuneIn JuneIn JuneIn JuneIn JuneIn JuneIn JuneIn JuneIn JuneIn JuneIn JuneIn JuneIn JuneIn JuneIn JuneIn JuneIn JuneIn JuneIn JuneIn JuneIn JuneIn JuneIn JuneIn JuneIn JuneIn JuneIn JuneIn JuneIn JuneIn JuneIn JuneIn JuneIn JuneIn JuneIn JuneIn JuneIn JuneIn JuneIn JuneIn JuneIn JuneIn JuneIn JuneIn JuneIn JuneIn JuneIn JuneIn JuneIn JuneIn JuneIn JuneIn JuneIn JuneIn JuneIn JuneIn JuneIn JuneIn JuneIn JuneIn JuneIn JuneIn JuneIn JuneIn JuneIn JuneIn JuneIn JuneIn JuneIn JuneIn JuneIn JuneIn JuneIn JuneIn JuneIn JuneIn JuneIn JuneIn JuneIn JuneIn JuneIn JuneIn JuneIn JuneIn JuneIn JuneIn JuneIn JuneIn JuneIn JuneIn JuneIn JuneIn JuneIn JuneIn JuneIn JuneIn JuneIn JuneIn JuneIn JuneIn JuneIn JuneIn JuneIn JuneIn JuneIn JuneIn JuneIn JuneIn JuneIn JuneIn JuneIn JuneIn JuneIn JuneIn JuneIn JuneIn JuneIn JuneIn JuneIn JuneIn JuneIn JuneIn JuneIn JuneIn JuneIn JuneIn JuneIn JuneIn JuneIn June In JuneIn JuneIn JuneIn JuneIn JuneIn JuneIn JuneIn June")

    testSocket.close()

if __name__ == '__main__':
  unittest.main()
