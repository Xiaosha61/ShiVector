# ShiVector's own logging that is not used for interpositioning and should
# never intermix with the application's logger
import logging
import SVFileHandler
SVLOG = logging.getLogger('shivector_logging')
SVLOG.setLevel(logging.DEBUG)
fh = SVFileHandler.SVFileHandler('shivector.log')
fh.setLevel(logging.DEBUG)
SVLOG.addHandler(fh)

import Patch as Patch
import socket
import SVSocket
# Global instance of Patch accessible in vlib/
PATCH = Patch.Patch()
# Start the patchers on the Socket, stdlib Print, Stream and File Handlers
PATCH.start_all()


# Give access to all classes in vlib to access the current timestamp value
# Since the port is not bound, we don't need to close it.
PRINTSOCKET = SVSocket.SVSocket(socket.AF_INET, socket.SOCK_STREAM)




