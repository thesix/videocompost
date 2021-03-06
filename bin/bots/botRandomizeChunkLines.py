import time
import os.path
import pickle
import signal
import random
from Compost import Compost
from VCLogger import writelog
from vcconfig import *

"""
Adapt config to your needs.  Use loadConfig () and saveConfig ()
to store data across runs.
"""
config = {}
config["chunk"] = 0

compost = Compost ()

class BotError (Exception):
  def __init__ (self, msg):
    self.msg = msg

  def __str__ (self):
    return repr (self.msg)

def signalhandler (signum, frame):
  raise BotError ("received signal {0}".format (signum))

def loadConfig ():
  global config
  filename = os.path.join (configdir, "%s.config" % __name__)
  if os.path.isfile (filename):
    infile = open (filename, "r")
    config = pickle.load (infile)
    infile.close ()

def saveConfig ():
  global config
  filename = os.path.join (configdir, "%s.config" % __name__)
  outfile = open (filename, "w")
  pickle.dump (config, outfile)
  outfile.close ()

def runMe ():
  """
  swapping random lines within a frame
  """
  # each image is 320x240 pixels of 4 bytes
  width = 320
  height = 240
  csize = 4
  wsize= width*csize
  size = width*height*csize

  random.seed()
  
  loadConfig ()
  signal.signal (signal.SIGHUP, signalhandler)
  signal.signal (signal.SIGINT, signalhandler)
  writelog ("[{0}]: started".format (__name__))
  try:
    for chunk in range (config["chunk"], len (compost._chunks)):
      # writelog ("{0} working on chunk {1}".format (__name__, chunk))
      compost.mapChunk (chunk)
      for frame in range (0, len (compost._map) / size):
        randlength=random.randint(0, wsize/4)
        line1index = frame*size+(random.randint (0, size-randlength)/4)*4
        line2index = frame*size+(random.randint (0, size-randlength)/4)*4
        line = compost._map[line1index:(line1index+randlength)]
        compost._map[line1index:(line1index+randlength)] = compost._map[line2index:(line2index+randlength)]
        compost._map[line2index:(line2index+randlength)] = line
        compost.addEntropy (randlength)
      
      config["chunk"] = chunk
      saveConfig ()
  except Exception as e:
    writelog ("[{0}]:  Caught exception ({1}).  Exiting".format (__name__, e))
    config["chunk"] = chunk
    saveConfig ()
    return 0

  # print "{0} has done one cyle. resetting config".format (__name__)
  config["chunk"] = 0
  saveConfig ()
  return 0
  
if __name__ == "__main__":
  pass

# vim: tw=0 ts=2 expandtab
# EOF
