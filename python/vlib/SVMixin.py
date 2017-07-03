#!/usr/bin/python
import json

class SVMixin(object):
  """ Generic reusable functions for ShiVector classes """

  __JSON_ID = "\nlocalProcessId"
    
  def __init__(self):
    """ Initialize """

  @staticmethod
  def prettyprintjson(dict):
    """ Returns the JSon representation of a timestamp dictionary """
    buildStr = SVMixin.__JSON_ID
    buildStr += json.dumps(dict, sort_keys=True, separators=(',', ': '))

    return buildStr

if __name__ == '__main__':
  MIXIN = SVMixin()