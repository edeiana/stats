import os
import socket
from os import listdir
from os.path import isfile, join

import utils

benchmark = 'facedet_and_track'

## Read pose.txt file and store each line as an array element
#
#
def readDataRaw(pathToFile):
  with open(str(pathToFile), 'r') as f:
    data = []
    for line in f:
      data.append(str(line))
    f.close()

    return data

## Write a pose.txt file
#
#
def writeDataRaw(pathToFile, data):
  with open(str(pathToFile), 'w') as f:
    for line in data:
      f.write(str(line))
    f.close()

  return

def mergeFiles(fromPath, toPath):
  threadFramesFiles = [f for f in listdir(fromPath) if isfile(join(fromPath, f)) and f.startswith('output')]
  dataTmp = []
  for f in threadFramesFiles:
    data = readDataRaw(join(fromPath, f))
    dataTmp.append(data)

  dataToWrite = [item for sublist in dataTmp for item in sublist]
  writeDataRaw(toPath, dataToWrite)

  return

def copyOutput(pathToOutputDir, it):
  parsecDir = os.environ['REPO_PATH'] + '/parsec-3.0'
  dataStr = '_it_' + str(it) + '_'

  outputFrom = parsecDir + '/pkgs/apps/' + benchmark + '/run'
  outputTo = pathToOutputDir + '/output' + dataStr + '.txt'

  mergeFiles(outputFrom, outputTo)

  return

