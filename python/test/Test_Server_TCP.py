#!/usr/bin/python

import logging
log = logging.getLogger(__name__)
import mock
import sys
import socket
import unittest
import vlib.SVSocket as SVSocket
import vlib.SVPrint as SVPrint
import vlib.Patch as Patch

"""
  Simple test receiving 1 message from Test_Client_TCP.py
  that will patch socket.socket to SVSocket subclass functions
"""
class Test_Server_TCP(unittest.TestCase):
 
  def test_patchReceive(self):
    """
    Wait for 1 message from the client
    """
    # Create a test socket which is actually of type SVSocket
    self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      
    # Assert that self.testSocket is indeed of the type SVSocket
    self.assertEqual(self.serverSocket.__class__, SVSocket.SVSocket)

    # Bind the socket to the test address where Test_Client_TCP is waiting
    host = "127.0.0.1"
    port = 16161
    self.serverSocket.bind((host, port))
      
    self.serverSocket.listen(5)
    # Accept response when the client sends a message
    (newSock, addr) = self.serverSocket.accept()

    try:   
      # Mock the user code which will loop through the recv data
      # This is the actual message length that the server is expecting which
      # does not include the vector timestamp and additional information
      msgLength = 1024
      
      # The SVSocket function called here through the patch ensures that
      # the entire data message is returned with an appended vector timestamp
      while 1:
        data = newSock.recv(msgLength)
        log.debug(("Test_Server_TCP Application code received message: ", data))
        if not data:
         break

      newSock.close()
      self.serverSocket.close()
    except:
      newSock.close()
      self.serverSocket.close()
      raise
          
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
