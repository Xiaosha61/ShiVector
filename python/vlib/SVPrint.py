#!/usr/bin/python

import logging
log = logging.getLogger(__name__)
import sys
import socket
import SVMixin as SVMixin
"""
SVPrint class is reached using the mock patch's class level decorator.
"""
class SVPrint(SVMixin.SVMixin):
  __wrapped_sys_stdout = None
    
  def __init__(self):
    """ Initialize the instance """
    
  @staticmethod
  def wrap():
    """
    Handle creating a sys.stdout so that the print call is non-recursive
    """
    # Import global constant patch from the init file
    from . import PATCH
    # Undo the patch on print handlers temporarily

    try:
      PATCH.stop_patchers()
      # Set a variable to sys.stdout which points to the real class
      SVPrint.__wrapped_sys_stdout = sys.stdout
      # Restart the patching mechanisms
      PATCH.start_all()
    except:
      PATCH.stop_patchers()
      raise

  @staticmethod
  def write(msg):
    """
    Append the vector clock at the end of the message
    """
    if msg != "":
      try:
        if SVPrint.__wrapped_sys_stdout == None:
          SVPrint.wrap()
        from . import PRINTSOCKET
        # Don't print out the clock if msg is only a new line or tab character
        if msg =='\n' or msg =='\r':
          SVPrint.__wrapped_sys_stdout.write(msg)
        else:
          SVPrint.__wrapped_sys_stdout.write((msg + SVMixin.SVMixin.prettyprintjson(PRINTSOCKET.getClock())))

      except ImportError, e:
        # This occurs the first time the patch has run, there is no clock yet
        SVPrint.__wrapped_sys_stdout.write(msg)

if __name__ == '__main__':
  PRINT = SVPrint()