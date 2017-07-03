#!/usr/bin/python

# ShiVector's local logging setup
import logging
import SVMixin

"""
  SVStreamHandler class is reached using the mock patch's class level decorator.
"""
class SVStreamHandler(SVMixin.SVMixin, logging.Handler):
    
  def __init__(self, stream=None):
    """
    Instantiate a wrapped logging.StreamHandler to pass undefined functions to the
    decorated StreamHandler class. Stop the patch momentarily to instantiate.
    """
    try:
      # Import the global constant patch from the vlib/init file
      from . import PATCH
      logging.Handler.__init__(self)
      # Undo the patch on all logging handlers temporarily
      try:
        PATCH.stop_patchers()
        self.__wrapped_stream_handler = logging.StreamHandler(stream)
        # Restart all of the logging handler patches
        PATCH.start_all()
      except:
        # Stop patching on any error to prevent recursion
        PATCH.stop_patchers()
        raise
    except ImportError:
      # Patch is not yet initialized, so we don't have to stop any patches
      self.__wrapped_stream_handler = logging.StreamHandler(stream)
      pass
    
  def __getattr__(self, attr):
    """
    Catch undefined functions and pass to the correct handler
    """
    try:
      # Retrieve the name of this function from wrapped handler
      fnc = getattr(self.__wrapped_stream_handler, attr)
    except AttributeError:
      raise
        
    if callable(fnc):
      # If the attribute is a function, create a closure
      return lambda *args, **kwargs : fnc(*args, **kwargs)
    else:
      # The attribute is a simple datatype, return it
      return fnc
          
  def emit(self, record):
    """
    Override emit() which eventually calls write()
    """
    try:
      from . import PRINTSOCKET
      if record.msg !='\n' and record.msg !='\r':
        # Only attach the timestamp with actual messages
        record.msg = record.msg + self.prettyprintjson(PRINTSOCKET.getClock())
    except ImportError, e:
      # This occurs the first time the patch has run, there is no clock yet
      pass
            
    self.__wrapped_stream_handler.emit(record)
        
        
  def close(self):
    """ Close the stream  """
    self.__wrapped_stream_handler.close()

if __name__ == '__main__':
  sh = SVStreamHandler()