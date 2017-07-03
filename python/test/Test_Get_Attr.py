#!/usr/bin/python

import logging
log = logging.getLogger(__name__)
import socket
import mock
import unittest
import vlib.SVSocket as SVSocket

"""
  Test that SVSocket detects undefined functions and redirects them
    to the internal wrapped socket
"""
class Test_Get_Attr(unittest.TestCase):
 
  def test_mysteryFunction(self):
    """
    Test that a function that does not exist is handled by the socket class
    """
    # Create a test socket which is actually of type SVSocket
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
      
    # Assert that self.testSocket is indeed of the type SVSocket
    self.assertEqual(serverSocket.__class__, SVSocket.SVSocket)

    # Test that AttributeError occurs, wrap in lambda to delay for assertRaises check 
    self.assertRaises(AttributeError, lambda: serverSocket.mysteryFunction())
      
    serverSocket.close()

  def test_socketFunction(self):
    """
    Test that a function that exists in socket but not in SVSocket is redirected
    """
    # Create a test socket which is actually of type SVSocket
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            
    # Assert that self.testSocket is indeed of the type SVSocket
    self.assertEqual(serverSocket.__class__, SVSocket.SVSocket)
            
    # Call default timeout functions that exist in socket but not SVSocket
    serverSocket.settimeout(1000)
    
    # Test that the setting change occured
    self.assertEqual(serverSocket.gettimeout(), 1000)
                
    serverSocket.close()

if __name__ == '__main__':
  unittest.main()
