import os
import sys
import socket
from os import listdir
from os.path import isfile, join

sys.path.append('../')

import utils

benchmark = 'bodytrack'

## Read pose.txt file and store each line as an array element
#
#
def readPosesDataRaw(pathToFile):
  with open(str(pathToFile), 'r') as f:
    data = []
    for line in f:
      data.append(str(line))
    f.close()

    return data

## Write a pose.txt file
#
#
def writePosesDataRaw(pathToFile, data):
  with open(str(pathToFile), 'w') as f:
    for line in data:
      f.write(str(line))
    f.close()

  return

## Merge the poses.txt files of a run
#
#
def mergeFiles(fromPath, toPath):
  threadFramesFiles = [f for f in listdir(fromPath) if isfile(join(fromPath, f)) and f.startswith('poses_')]
  posesDataTmp = []
  for f in threadFramesFiles:
    data = readPosesDataRaw(join(fromPath, f))
    posesDataTmp.append(data)

  posesData = [item for sublist in posesDataTmp for item in sublist]
  writePosesDataRaw(toPath, posesData)

  return

def copyOutput(pathToOutputDir, it):
  parsecDir = os.environ['REPO_PATH'] + '/parsec-3.0'
  itStr = '_it_' + str(it) + '_'

  outputFrom = parsecDir + '/pkgs/apps/' + benchmark + '/run'
  outputTo = pathToOutputDir + '/output' + itStr + '.txt'
  mergeFiles(outputFrom, outputTo)

  return

