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
  Test sending a message through UDP which will call the SVSocket subclass functions through the patch
  Note: Start Test_Server_UDP before running this test
"""
class Test_Client_UDP(unittest.TestCase):
 
  def test_Send(self):
    """
    Instantiate an instance of SVSocket through the patch and send a message
    to Test_Server_UDP
    """    
    # Create a test socket that is actually an instance of SVSocket     
    testSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
     
    # Assert that self.testSocket is indeed of the type SVSocket
    self.assertEqual(testSocket.__class__, SVSocket.SVSocket)

    # Connect to the server waiting at this test address and send a message
    testSocket.sendto("When I speak about computer programming as an art, I am thinking primarily of it as an art form, in an aesthetic sense. The chief goal of my work as educator and author is to help people learn how to write beautiful programs. It is for this reason I was especially pleased to learn recently [32] that my books actually appear in the Fine Arts Library at Cornell University. (However, the three volumes apparently sit there neatly on the shelf, without being used, so I'm afraid the librarians may have made a mistake by interpreting my title literally.)  My feeling is that when we prepare a program, it can be like composing poetry or music; as Andrei Ershov has said [9], programming can give us both intellectual and emotional satisfaction, because it is a real achievement to master complexity and to establish a system of consistent rules.", ("127.0.0.1", 12457))

    testSocket.close()

if __name__ == '__main__':
  unittest.main()
