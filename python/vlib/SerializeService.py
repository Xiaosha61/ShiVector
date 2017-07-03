#!/usr/bin/python

import binascii
import logging
import operator
import struct
import socket

"""
Service class that provides functions to serialize and deserialize 
a message, and to add a custom vector clock header
"""
class SerializeService():
  # ****************** Class Level variables **********************************************    
  # Padded integers comprise 8 hexits
  INT_LENGTH = 8
  # Clock key length = Unpadded IP + Padded PID = 8 + 8 = 16 
  KEY_LENGTH = 16 
  # Indicate the position of information in the header to be parsed
  # This is used by the UDP parsing only
  MSG_LENGTH_POS = 0
  CLOCK_SIZE_LIST_POS = 1
  CLOCK_SIZE_POS = 8
  KEY_START_POS = 16
  KEY_END_POS = 32 # Key has length 16
  VALUE_END_POS = 40 # Value has length of int
  CLOCK_LAST_PARSED = 40
  CLOCK_TUPLE_SIZE = 24 #KEY + VALUE = 16 + 8 = 24

  # ***************************************************************************************
  def __init__(self):
    """
    Initiate the Service class
    """

  def packInteger(self, decimalInt):
    """
    Convert decimal integer to a hex integer (padded)
    eg. 299 -> +\x01\x00\x00 -> 2b010000
    """
    # Structure of the string is one integer value
    s = struct.Struct('I')
    # Pack the decimal Integer, providing padding x bytes
    packedInt = s.pack(decimalInt)
    hexInt = binascii.hexlify(packedInt)
            
    return hexInt
    
  def packKey(self, decimalIP, decimalPID):
    """
    Convert decimal arguments to a unpadded Hex IP + padded Hex PID
    """
    # Convert to an unpadded hex 
    hexIP = self.convertIP(decimalIP)
    hexPID = self.packInteger(decimalPID)
    key = hexIP + hexPID
      
    from . import SVLOG
    SVLOG.debug("Created key: " + key)
    
    return key

  def convertIP(self, decimalIP):
    """
    Convert decimal formatted IP to an unpadded hex version
    We can then parse this out later as 8 hexits to save space
    eg. 127.0.0.1 -> \x7f\x00\x00\x01 -> 7f000001
    """
    hexIP = binascii.hexlify(socket.inet_aton(decimalIP))
    from . import SVLOG
    SVLOG.debug("Converted IP: "+ decimalIP + " to: " + hexIP)
    return hexIP
    
  def packTotalMessage(self, msg, vstamp):
    """
    Converts the message contents, vector timestamp and length
    of the message into a hexidecimal formatted string
    """        
    hexMsg = self.packMessage(msg)    
    hexHeaderLength = self.packHeaderLength(hexMsg, vstamp.clock)
    hexVStamp = self.packVStamp(vstamp.clock)
    totalHexMsg = hexHeaderLength + hexVStamp + hexMsg
    from . import SVLOG
    SVLOG.debug("Complete hex message is: " + totalHexMsg)

    return totalHexMsg
    
  def packMessage(self, msg):
    """
    Pack the payload message into hexidecimal format
    """
    # Tell the struct how many characters to expect in the string
    s = struct.Struct(str(len(msg)) + 's')
    # Packs the string message into hexidecimal format
    packedMessage = s.pack(msg)
    hexMessage = binascii.hexlify(packedMessage)
    from . import SVLOG
    SVLOG.debug(" Hex Message: " + hexMessage)
  
    return hexMessage
    
  def packHeaderLength(self, hexMsg, clock):
    """ 
    Construct a list of integers for the total length of the message,
    the size of the vector clock, and the elements in the vector clock
    """
    intList = [len(hexMsg), len(clock)]

    # Construct format string for the 2 integers in the header
    s = struct.Struct('I I')
    packedHeader = s.pack(*intList)
    hexHeader = binascii.hexlify(packedHeader)
    from . import SVLOG
    SVLOG.debug(" Hex Length Header: " + hexHeader)
        
    return hexHeader

  def packVStamp(self, clock):
    """
    Pack the dictionary keys and values. The keys are hex
    format and can be sent directly, whereas the dict
    integer values first need to be encoded to send
    """
    byteStringClock = ""
        
    for k, v in clock.iteritems():
      byteStringClock += k      
      byteStringClock += self.packInteger(v)

    return byteStringClock
    
  def unpackInteger(self, hexInt):
    """
    Takes a hex integer of 8 hexits and unpacks it into decimal
    """
    packed_data = binascii.unhexlify(hexInt)
    # Parse out one integer value
    s = struct.Struct('I')
    unpacked_data = s.unpack(packed_data)
      
    # The result is a tuple of one element
    return unpacked_data[0]


  def unpackMessage(self, msg):
    """
    Parses out the string message from the hex format
    """
    packed_data = binascii.unhexlify(msg)      
    # Parse out the entire length of string data
    s = struct.Struct(str(len(packed_data)) + 's')      
    unpacked_data = s.unpack(packed_data)

    # The result is a tuple of one element
    return unpacked_data[0]

  def parseHeader(self, socket):
    """
    Return a list of the header elements in order: (TCP)
    ( Message Length, # of tuples in vector clock dict )
    """
    # The first integer in the message represents the message length
    msgLengthBytes = socket.recv(SerializeService.INT_LENGTH)
    # Check if header is empty and signal a return
    if len(msgLengthBytes) == 0:
      return ()
    try:
      msgLength = self.unpackInteger(msgLengthBytes)
      # The second integer in the message is the number of tuples in the vector clock
      # This is used to parse out the vector clock dict from the header
      vectorSizeBytes = socket.recv(SerializeService.INT_LENGTH)
      vectorSize = self.unpackInteger(vectorSizeBytes)

      return (msgLength, vectorSize)
     
    except TypeError:
      # This is an internal message, and does not have a header, skip the parsing
      return (msgLengthBytes,0)
    
  def parseUDPHeader(self, totalMsg):
    """
    Return a list of the header elements in order: (UDP)
    ( Message Length, # of tuples in vector clock dict )
    """
    # The first integer in the message represents the message length
    msgLengthBytes = totalMsg[:SerializeService.INT_LENGTH]
    msgLength = self.unpackInteger(msgLengthBytes)
    # The second integer in the message is the number of tuples in the vector clock
    # This is used to parse out the vector clock dict from the header
    vectorSizeBytes = totalMsg[SerializeService.CLOCK_SIZE_POS:
                             SerializeService.KEY_START_POS]
    vectorSize = self.unpackInteger(vectorSizeBytes)
      
    return (msgLength, vectorSize)
        
  def parseVectorClock(self, socket, header):
    """
    Extract the vector clock from the socket message (TCP)
    """
    # Loop through units of integers that comprise the message's vector clock dict
    receivedClock = {}
    vectorSize = header[SerializeService.CLOCK_SIZE_LIST_POS]
    for count in range (0, vectorSize):
      # Since we store the key in hex, we don't need to convert it
      byteKey = socket.recv(SerializeService.KEY_LENGTH)
      byteValue = socket.recv(SerializeService.INT_LENGTH)
      value = self.unpackInteger(byteValue)
        
      # Rebuild the vector clock that was passed in the message header
      receivedClock[byteKey] = value
      
    return receivedClock
        
  def parseUDPVectorClock(self, totalMsg, header):
    """
    Extract the vector clock from the total byte string (UDP)
    """      
    # Loop through units of bytes that comprise the message's vector clock dict
    receivedClock = {}
    vectorSize = header[SerializeService.CLOCK_SIZE_LIST_POS]

    # Each tuple has size 24 hexits, step through by units of 2
    for count in range (1, (vectorSize*2)+1, 2):
      # Since we store the key in hex, we don't need to convert it
      byteKey = totalMsg[(SerializeService.KEY_START_POS*count):
                         (SerializeService.KEY_END_POS*count)]
      byteValue = totalMsg[(SerializeService.KEY_END_POS*count):
                           (SerializeService.VALUE_END_POS*count)]
      value = self.unpackInteger(byteValue)
          
      # Rebuild the vector clock that was passed in the message header
      receivedClock[byteKey] = value
      # Indicate where the last tuple was parsed in the message
      SerializeService.CLOCK_LAST_PARSED += ((count-1)*SerializeService.CLOCK_TUPLE_SIZE)
      
    return receivedClock
                
  def parsePayloadMsg(self, header, socket):
    """
    Extract the wrapped message from the socket message (TCP)
    """
    msgLength = header[SerializeService.MSG_LENGTH_POS]
    payloadMsg = ""
    while msgLength > 0:
      data = socket.recv(msgLength)
    
      if not data:
        break
    
      # deserialize the byte data and join it in the return string
      deserializedData = self.unpackMessage(data)
      # join the string data to the return message
      payloadMsg = payloadMsg + deserializedData
      # decrement the amount of string characters we're expecting
      msgLength -= len(deserializedData)

    return payloadMsg

  def parseUDPPayloadMsg(self, totalMsg):
    """
    Extract the wrapped message from the total message (UDP)
        based on where the vector clock stopped
    """
    payloadMsg = self.unpackMessage(totalMsg[SerializeService.CLOCK_LAST_PARSED:])
      
    return payloadMsg

if __name__ == '__main__':
  serializeService = SerializeService()