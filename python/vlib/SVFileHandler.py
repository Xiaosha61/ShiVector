#!/usr/bin/python
import logging
import SVStreamHandler as SVStreamHandler

"""
    SVFileHandler class is reached using the mock patch's class level decorator.
"""
class SVFileHandler(SVStreamHandler.SVStreamHandler):

  def __init__(self, filename, mode='a', encoding=None, delay=0):
    """
    Instantiate a wrapped logging.FileHandler to pass undefined functions to the
    decorated FileHandler class. Stop the patch momentarily to instantiate.
    """
    try:
      # Import global constant patch from the init file
      from . import PATCH
      # Undo the patch on logging handlers temporarily
      try:
        PATCH.stop_patchers()
        self.__wrapped_file_handler = logging.FileHandler(filename)
        # Restart all of the handler patches
        PATCH.start_all()
        # Instantiate the SV super class
        self.superClass = super(SVFileHandler, self).__init__(self._open())
      except:
        # Stop patching on any error to prevent recursion
        PATCH.stop_patchers()
        raise
    except ImportError:
      # Patch is not yet initialized, so we don't have to stop any patches
      self.__wrapped_file_handler = logging.FileHandler(filename)
      # Instantiate the SV super class
      self.superClass = super(SVFileHandler, self).__init__(self._open())
      pass

  def __getattr__(self, attr):
    """
    Catch undefined functions and pass to the correct handler
    """
      
    try:
      # Retrieve the name of this function from wrapped handler
      fnc = getattr(self.__wrapped_file_handler, attr)
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
    Call superclass SVStreamHandler's emit()
    """
    # Call the super class stream
    SVStreamHandler.SVStreamHandler.emit(self, record)

  def close(self):
    """ Close the wrapped handler and the SVStreamHandler parent """
    super(SVStreamHandler.SVStreamHandler, self).close()

if __name__ == '__main__':
  fh = SVFileHandler()