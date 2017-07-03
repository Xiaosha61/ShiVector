import urllib2
# Apply the patch by including this import statement
import vlib.Patch

try:
  response = urllib2.urlopen('http://127.0.0.1:8484')
  print "Client 1 Response:", response

except urllib2.URLError, e:
  print "********** CherryPy URL is incorrect or the server is stopped ***********", e
  raise
