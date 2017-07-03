"""
    Patch CherryPy's logging mechanisms and socket communications
    without touching the ordinary cherry py code
    
    Print test strings that have appended timestamps in JSON format
"""

# Import CherryPy global namespace
import cherrypy

class server:
    
  """ Request handler class. """

  def exit(self):
    """ Kill the cached thread """
    raise SystemExit(0)
    
  # Make this function callable from the browser
  exit.exposed = True

  def index(self):
    """ Called from the browser, test printing to the console and to the access
          and error logs found in the cherrypy/ directory """
        
    print " Received a request to cherry py "
       
    return "000000000"
    
  # Expose the index method through the web. CherryPy will never
  # publish methods that don't have the exposed attribute set to True.
  index.exposed = True

import os.path
conf = os.path.join(os.path.dirname(__file__), 'cherrypy.conf')

if __name__ == '__main__':
  # Testing the print interpositioning
  print "**************** CherryPy Server Restarted ******************"

  cherrypy.quickstart(server(), config=conf)
  print "**************** CherryPy Server Running ******************"


else:
  # This branch is for the test suite; you can ignore it.
  cherrypy.tree.mount(server(), config=conf)
