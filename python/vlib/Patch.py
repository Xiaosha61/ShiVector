#!/usr/bin/python

# TODO Check version, mock is fixed in 3.5+
# Patched version with fixed stop() http://bugs.python.org/issue21239
import mockfix as mock
from ConfigParser import SafeConfigParser
import ConfigParser
import os

class Patch(object):
    """ Run the global wide patches on socket, stdout, and logging handlers """
        
    __SOCKET_PATHS = list()
    __PRINT_PATHS = list()
    __LOG_PATHS = list()
    
    def __init__(self):
        # Set the environment variable to the shivector configuration file
      try:
        dir = os.environ["SHIVECTORCONFPATH"]
      except KeyError:
        # ShiVector's local logging setup
        from . import SVLOG
        SVLOG.error("SHIVECTORCONFPATH is not set in shivector.conf")
        raise
            
      parser = SafeConfigParser()
      parser.read(dir)
    
      # No exception is raised if file is not found, but sections will be empty
      if len(parser.sections()) == 0:
        raise Exception("shivector.conf not found or is empty")

      # Read and set the paths to patch
      try:          
        for k, v in parser.items('socketpaths'):
          Patch.__SOCKET_PATHS.append(v)

        for k, v in parser.items('printpaths'):
          Patch.__PRINT_PATHS.append(v)
                  
        for k, v in parser.items('logpaths'):
          Patch.__LOG_PATHS.append(v)
        
      except ConfigParser.NoSectionError, e:
        SVLOG.error("Section missing in shivector.conf " + e)
        raise

    def start_all(self):
      """ Start all of the patches """
      self.start_sockets()
      self.start_prints()
      self.start_handlers()

    def start_sockets(self):
      """ Patch the built-in socket library to custom SVSocket """
      from . import SVLOG
      import SVSocket as SVSocket
      try:
        for path in Patch.__SOCKET_PATHS:
          Patch.__PATCHER = mock.patch(path, SVSocket.SVSocket)
          Patch.__PATCHER.start()
          SVLOG.debug(path + " is patched to SVSocket")

      except ImportError, e:
        SVLOG.error("Not yet instantiated " + str(e))
        # Pass through in the case where the path is uninitialized
        pass
            
    def start_prints(self):
      """ Patch the built-in print file to custom SVPrint """
      from . import SVLOG
      import SVPrint as SVPrint
      try:
        for path in Patch.__PRINT_PATHS:
          Patch.__PATCHER = mock.patch(path, SVPrint.SVPrint)
          Patch.__PATCHER.start()
          SVLOG.debug(path + " is patched to SVPrint")
      except ImportError, e:
        SVLOG.error("Not yet instantiated " + str(e))
        pass

    def start_handlers(self):
      """
      Patch each type of handler located in the conf file to the custom SVStreamHandler
      and SVFileHandler. The path is the location of logging.Logger objects
      """
      # Perform this check because importing StreamHandler breaks if the application
      # doesn't utilize logging
      if len(Patch.__LOG_PATHS) > 0:
        import SVStreamHandler as SVStreamHandler
        import SVFileHandler as SVFileHandler
        from . import SVLOG
          
        for path in Patch.__LOG_PATHS:
          try:
            Patch.__PATCHER = mock.patch(path+'.StreamHandler', SVStreamHandler.SVStreamHandler)
            Patch.__PATCHER.start()
            SVLOG.debug(path +'.StreamHandler' + " is patched to SVStreamHandler")
            Patch.__PATCHER = mock.patch(path+'.FileHandler', SVFileHandler.SVFileHandler)
            Patch.__PATCHER.start()
            SVLOG.debug(path +'.FileHandler'+ " is patched to SVFileHandler")
          except ImportError, e:
            SVLOG.error("Not yet instantiated " + str(e))
            # Pass through in the case where the path is uninitialized
            pass

    def stop_patchers(self):
      """
      Stop all of the patches in the singler PATCHER object. 
      """
      from . import SVLOG
      SVLOG.debug("Stopped all handlers on PATCHER")
      mock.patch.stopall()

if __name__ == '__main__':
  PATCH = Patch()