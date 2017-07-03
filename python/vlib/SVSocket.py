#!/usr/bin/python

import logging
import SerializeService as SerializeService
import socket
import Patch as Patch
import VectorClock as VectorClock
import struct
import binascii
import os

"""
SVSocket class is reached using the mock patch's class level decorator.
Each call to socket.socket is decorated by SVSocket's functions which
append logging with a vector timestamp.
"""
class SVSocket():
    
  # ****************** Class Level variables **********************************************  
  # Create a single version of vector clock for this class
  __vectorClock = None
  # Maximum length of message to retrieve from UDP
  MSG_MAX_SIZE = 4096
  # ***************************************************************************************
    
  def __init__(self, *args, **kwargs):
    """
    Initialize an instance of the wrapped socket by stopping the patch momentarily.
    Restart the patch so all socket references point to the decorator SVSocket.
    Instantiate class level variables.
    """
    # ****************** Patch Handling*******************************************
    #     Stop the socket.socket patch to SVSocket so that we can create the actual
    #     socket class and avoid recursive call errors, restart once finished.
    # *****************************************************************************
    # Import global constant patch from the init file
    from . import PATCH
    # Undo the patch on logging handlers temporarily
    try:
      PATCH.stop_patchers()
      # ****************** Class Level variables ************************************
      # Now, we can call socket's __init__ which points to the real class
      self.__wrapped_socket = socket.socket(*args, **kwargs)
      self.currentIP = socket.gethostbyname(socket.getfqdn())
      self.serializeService = SerializeService.SerializeService()
      self.currentPID = os.getpid()
      self.initClock()
      # Restart the patching mechanisms
      PATCH.start_all()
      # *****************************************************************************
    except:
      PATCH.stop_patchers()
      raise
          
  def __getattr__(self, attr):
    """
    Catch any undefined functions called on SVSocket through socket
    and call them on the internal wrapped socket
    """      
    try:
      # Retrieve the name of this function from socket
      fnc = getattr(self.__wrapped_socket, attr)
    except AttributeError:
      raise
 
    if callable(fnc):
      # Return the function closure from the socket class
      return lambda *args, **kwargs : fnc(*args, **kwargs)
    else:
      # The attribute is a simple datatype, return it
      return fnc
        
  def initClock(self):
    """
    Prevent vector clock from being overwritten by instantiation
    """
    if SVSocket.__vectorClock is None:
      SVSocket.__vectorClock = VectorClock.VectorClock(self.currentIP, self.currentPID)
    else:
      from . import SVLOG
      SVLOG.info(" Attempt to add a new PID entry to the clock ")
      SVSocket.__vectorClock.addNewTuple(self.currentIP, self.currentPID)

  def getClock(self):
    """
    Return the dict to the outside world
    """
    return SVSocket.__vectorClock.clock

  def connect(self, address):
    """
    Connect the SVSocket using the wrapped socket's connect function
    """
    self.__wrapped_socket.connect(address)
        
  def send(self, msg):
    """
    Appends the incremented vector clock to the message
        (used with TCP connection)
    """
    # Increment the value at this key (IP+PID)
    SVSocket.__vectorClock.increment(self.currentIP, self.currentPID)
    # Pack a TCP message with the vector clock included in the header
    vMsg = self.serializeService.packTotalMessage(msg, SVSocket.__vectorClock)
    from . import SVLOG
    SVLOG.debug("SEND updated vector clock ")

    self.__wrapped_socket.send(vMsg)
          
    return len(vMsg)
          
  def sendall(self, msg):
    """
    Appends the incremented vector clock to the message
    """
    # Increment the value at this key (IP+PID)
    SVSocket.__vectorClock.increment(self.currentIP, self.currentPID)
    # Pack a TCP message with the vector clock included in the header
    vMsg = self.serializeService.packTotalMessage(msg, SVSocket.__vectorClock)
    from . import SVLOG
    SVLOG.debug("SENDALL updated vector clock")
      
    self.__wrapped_socket.sendall(vMsg)

  def sendto(self, msg, address):
    """
    Appends the incremented vector clock to the message
        (used with UDP connection)
    """
    # Increment the value at this key (IP+PID)
    SVSocket.__vectorClock.increment(self.currentIP, self.currentPID)
    # Pack a UDP message with the vector clock included in the header
    vMsg = self.serializeService.packTotalMessage(msg, SVSocket.__vectorClock)
    from . import SVLOG
    SVLOG.debug("SENDTO updated vector clock ")      
      
    self.__wrapped_socket.sendto(vMsg, address)

  def bind(self, address):
    """
    Binds the wrapped socket to the address
    """
    self.__wrapped_socket.bind(address)

  def listen(self, backlog):
    """
    Call the wrapped socket to listen
    """        
    self.__wrapped_socket.listen(backlog)

  def accept(self):
    """
    Accept on the wrapped socket, then return the new socket
    wrapped inside of a new SVSocket
    """
    newSock, addr = self.__wrapped_socket.accept()
      
    # Wrap the newsock inside of an SVSocket so that
    # decoration will behave properly in subsequent calls      
    wrappedNewSock = SVSocket()
    wrappedNewSock.__wrapped_socket = newSock
      
    return (wrappedNewSock, addr)

  def recv(self, bytes):
    """
    Receive from TCP connection, unpack header, increment and merge internal
    vector clock, then return the wrapped payload message
    """
    # Increment the value at this key (IP+PID)
    SVSocket.__vectorClock.increment(self.currentIP, self.currentPID)
    from . import SVLOG
    SVLOG.debug("RECV INCREMENTED vector clock")
      
    # Retrieve the header from the message
    header = self.serializeService.parseHeader(self.__wrapped_socket)
    # Check if the header is empty and return from this message
    # Signal to the application code's loop that the message is complete
    if len(header) == 0:
      return ""
      
    if header[1] == 0:
      payloadMsg = header[0] + self.__wrapped_socket.recv(SVSocket.MSG_MAX_SIZE)
      return payloadMsg
      
    # Retrieve the vector clock based on its size specified in the header
    receivedVectorClock = self.serializeService.parseVectorClock(self.__wrapped_socket, header)

    # Merge the passed in vector clock with the local vector clock
    SVSocket.__vectorClock.merge(receivedVectorClock)
    SVLOG.debug("RECV MERGED the clocks ")
      
    # Parse the wrapped message following the vector clock
    payloadMsg = self.serializeService.parsePayloadMsg(header, self.__wrapped_socket)
                                    
    return payloadMsg
        
  def recvfrom(self, bytes):
    """
    Receive from UDP connection, handle vector timestamp information then
    return the payload message.
    """
    # Increment the value at this key (IP+PID)
    SVSocket.__vectorClock.increment(self.currentIP, self.currentPID)

    # Retrieve the entire message based on a max size
    totalMsg, addr = self.__wrapped_socket.recvfrom(SVSocket.MSG_MAX_SIZE)

    # Parse the header from the total message
    header = self.serializeService.parseUDPHeader(totalMsg)
    
    # Retrieve the vector clock based on its size specified in the header
    receivedVectorClock = self.serializeService.parseUDPVectorClock(totalMsg, header)
              
    # Merge the passed in vector clock with the local vector clock
    SVSocket.__vectorClock.merge(receivedVectorClock)
      
    # Parse the remainder of the complete message, that is the payload message
    payloadMsg = self.serializeService.parseUDPPayloadMsg(totalMsg)

    return (payloadMsg, addr)

  def close(self):
    """
    Close the wrapped socket
    """
    self.__wrapped_socket.close()
        
if __name__ == '__main__':
  s = SVSocket()