Pythonic ShiVector
===================

Required Libraries
-------------------

The mock libary is used in ShiVector instrumentation to interpose on the socket, print, and logging built-in libraries.
In Python versions <= 2.7, a backported mock libary can be downloaded at https://pypi.python.org/pypi/mock.

Installation instructions at: [http://www.voidspace.org.uk/downloads/mock-1.0.1.pdf](http://www.voidspace.org.uk/downloads/mock-1.0.1.pdf)


How to instrument a Python application
------------------------------------

**Set environment variables**

Add the environment variables PYTHONPATH and SHIVECTORCONFPATH in a script that runs your application. A sample of this is in test/run-tests.sh.
Append the ShiVector library (vlib) path to your PYTHONPATH. SHIVECTORCONFPATH must point to the shivector.conf settings to 
tell vlib/Patch where the libraries are located for interposition. An example of the shivector.conf file is found in the test directory.

**Initialize the ShiVector library**

To run the Patch class and initialize ShiVector, vlib/__init__.py must run at the root of your application. You can force the vlib/__init__ to run 
by including the line "import vlib.Patch". This will initiate the interposition and append the vector timestamps to your log messages.

In the CherryPy example *vlib/samples/webclientserver/cherrypy*, "import vlib.Patch" in located in 
*/Library/Python/2.7/site-packages/CherryPy-3.2.2-py2.7.egg/cherrypy/__init__.py*. This runs vlib/__init__.py
**before** logging and socket are imported. This way the interpositioning occurs before any objects are created.

**Test interposed libraries**

The path settings in the shivector.conf example in the test directory will work for most applications. However, some embedded references to 
interposed libraries need to be added manually. If a library needs to be manually added, an error will occur like:

*unbound method xxx() must be called with SVStreamHandler/SvFileHandler/SVPrint/SVSocket instance as first argument 
(got StreamHandler/FileHandler/stdout/socket instance instead)*

If this error occurs, search for the library call that causes the error and add it to the corresponding section in shivector.conf.


Issues
----------------------------

If the application uses Python version 3.5+, the mockfix.py file import can be replace by "import mock as mock". More details are located in the bug
at [https://bitbucket.org/bestchai/shivector/issue/35/import-python-35-mock-library-instead-of](https://bitbucket.org/bestchai/shivector/issue/35/import-python-35-mock-library-instead-of)
and at [http://bugs.python.org/issue21239](http://bugs.python.org/issue21239).


Class Hierarchy
------------------

vlib/ directory contains core classes of the Python implementation of **ShiVector**. These interpose on print, logging handlers, and socket standard 
libraries to add vector timestamps to logging messages within Python applications. 

**__init__.py**: Contains global variables VLOG (for ShiVector specific logging), PATCH (controls interpositioning), and PRINTSOCKET (stores 
the host's vector timestamp). By importing vlib/, this file is run in order to start ShiVector logging. 

**mockfix.py**: Patched version of mock.py that fixes issue http://bugs.python.org/issue21239

**Patch.py**: Controls interpositioning that is initiated in __init__.py of vlib. Relies on configuration file shivector.conf for the environment
variable SHIVECTORCONFPATH. 

**SerializeService.py**: Constructs the socket message header and converts text to hexidecimal format using the binascii library. The format of the
message with the header is [[message length, # of vector clock elements, vector clock map], original message]. If no header if supplied, the plain
message passes through without a vector timestamp.

**SVFileHandler.py**: Interposes on the logging FileHander class, and has the parent SVStreamHandler. Intercepts emit() to pass the message to
the SVStreamHandler super class by using a wrapped FileHandler instance.

**SVMixin.py**: Defines pretty print functions used to format the vector timestamp before appending it to the message.

**SVPrint.py**: Interposes on stdout print attribute by intercepting write(). Uses the wrapped sys.stdout to call the standard library after the
timestamp is appended.

**SVSocket.py**: Interposes socket.socket library functions to increment the vector timestamp when sending and receiving messages. Calls the
VectorClock class to increment the host's clock and to merge any incoming vector timestamp information.

**SVStreamHandler.py**: Interposes on the logging StreamHander class, and is called by the subclass SVFileHandler. Intercepts emit() to pass the message to
the wrapped StreamHandler instance.

test/ directory contains simple client and server tests for TCP and UDP protocols. Run these with run-tests.sh.

samples/ directory contains a web client and server example using cherrypy and urllib2. Run this example by starting the CherryPy server in 
samples/webclientserver/cherrypy/**run-cherrypy.sh**. Then, run the urllib2 client in samples/webclientserver/urllibclient/**run-urllib.sh**. 

**shivector.conf**: Example of the paths that need to be modified to patch the correct print, socket, and logging libraries.

**shivector.log**: Generated by the vlib/ classes that is used for debugging the ShiVector libary.