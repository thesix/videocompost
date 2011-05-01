#!/usr/bin/env python

import sys
import os
import fcntl
import pickle
import time
import signal
from BotList import BotList
from vcconfig import *
from Logger import writelog

class VCError (Exception):
  pass

class VCTimeout (VCError):
  def __init__ (self, msg):
    self.msg = msg

class VCInterrupt (VCError):
  def __init__ (self, msg):
    self.msg = msg

# def keepRunning ():
#   # FIXME:  check what we read from runfile
#   if os.path.isfile (runfilename):
#     runfile = open (runfilename, "r")
#     run = int (runfile.read ())
#     runfile.close ()
#     return run
#   return True

def alarmhandler (signum, frame):
  raise VCTimeout ("received signal {0}".format (signum))

def interrupthandler (signum, frame):
  raise VCInterrupt ("received signal {0}".format (signum))

def mainLoop ():
  """
  """
  # cycletime = 21600 # 6 hours, 4 cycles a day
  # cycletime = 3600
  cycletime = 30
  signal.signal (signal.SIGINT, interrupthandler)
  signal.signal (signal.SIGHUP, interrupthandler)
  while True:
    botlist = BotList ()
    numbots = len (botlist.bots)
    writelog ("[composter]: started cycle with {0} seconds per bot".format (cycletime / numbots))
    for b in botlist.getList ():
      try:
        bot = __import__ (b)
        reload (bot)
        pid = os.fork ()
        if pid == 0:
          return bot.runMe ()
        else:
          signal.signal (signal.SIGALRM, alarmhandler)
          signal.alarm (cycletime / numbots)
          try:
            writelog ("[composter]: waiting for {0}[.py] with pid {1}".format (b, pid))
            rv = os.waitpid (pid, 0)
            writelog ("[composter]: {0}[.py] with pid {1} returned {2}".format (b, pid, rv))
          except VCTimeout:
            os.kill (pid, signal.SIGHUP)
            rv = os.waitpid (pid, 0)
            writelog ("[composter]: {0} with pid {1} returned {2} on SIGHUP after timeout".format (b, pid, rv))
      except ImportError:
        writelog ("[composter]: Error importing {0}[.py]".format (b))
      except VCInterrupt:
        os.kill (pid, signal.SIGHUP)
        rv = os.waitpid (pid, 0)
        writelog ("[composter]: {0} with pid {1} returned {2} on SIGHUP after interrupt".format (b, pid, rv))
        return 0
  writelog ("[composter]: Don't know how I got here ...")
  return 0

if __name__ == "__main__":
  sys.exit (mainLoop ())

# vim: tw=0 ts=2 expandtab
# EOF
