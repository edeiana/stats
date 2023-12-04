import os
import sys
import socket

sys.path.append('../')

import utils

benchmark = 'streamcluster'

def copyOutput(pathToOutputDir, it):
  parsecDir = os.environ['REPO_PATH'] + '/parsec-3.0'
  dataStr = '_it_' + str(it) + '_'

  outputFrom = parsecDir + '/pkgs/kernels/' + benchmark + '/run/*_.txt'
  outputTo = pathToOutputDir + '/output' + dataStr
  if (not os.path.exists(outputTo)):
    os.mkdir(outputTo)
  os.system('cp ' + outputFrom + ' ' + outputTo)

  return

