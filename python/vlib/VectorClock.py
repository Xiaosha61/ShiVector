#!/usr/bin/python

import logging
import SerializeService as SerializeService

"""
Manages the vector clock for each instance including incrementing, adding,
and merging 2 host vector clocks to their maximum values.
    
IP and PID keys are stored in hexidecimal format, for example localhost is
converted to 7f000001 and PID is stored in padded hex to a maximum value of 
4194304 for 64 bit machines.
"""
class VectorClock:
    
  def __init__(self, decimalIP, decimalPID):
    """
    Instantiate the VectorClock with the dictionary object.
    There exists one instance of the Vector Clock per host IP that contains
    unique IP+PID keys with vector timestamp values.
    """
    # Convert the IP and PID to a format we can send and receive
    self.serializeService = SerializeService.SerializeService()     
    key = self.serializeService.packKey(decimalIP, decimalPID)
      
    # This will never overwrite an existing clock value since the
    # VectorClock re-instantiation is controlled in SVSocket.initClock()
    self.clock = {key: 0}

  def addNewTuple(self, decimalIP, decimalPID):
    """
    Add a new process ID and IP to the clock. Add <k,v> only if not present, 
    otherwise an error is logged. To modify a value, increment is used.
    """
    from . import SVLOG
    key = self.serializeService.packKey(decimalIP, decimalPID)
    
    # Add <k,v> only if not present, we can only increment a value
    # not rewrite to directly set it to a value
    if self.clock.has_key(key):
        SVLOG.error("Attempted to add a duplicate key as a new PID" + key)
    else:
      self.clock[key] = 1

  def increment(self, decimalIP, decimalPID):
    """
    Increment the timestamp value at the key IP+PID location
    """
    # Detect if a new IPPID is created and add it to the dict
    key = self.serializeService.packKey(decimalIP, decimalPID)
    if self.clock.has_key(key):
      self.clock[key] = self.clock[key] + 1
    else:
      self.clock[key] = 1
          
  def merge(self, clock):
    """
    Merge two vector timestamps together, to the max value of each key entry.
    """
    # Host vector clock dicts contain unique keys (IP+PID)
    # so we must take care to merge in new tuples        
    for k, v in clock.iteritems():
      if self.clock.has_key(k):
        self.clock[k] = max(self.clock[k], clock[k])
      else:
        # Incoming clock has extra values that we simply add to this host dictionary
        self.clock[k] = v

if __name__ == '__main__':
  vectorClock = VectorClock()
