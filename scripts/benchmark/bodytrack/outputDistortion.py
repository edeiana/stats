import os
import sys
import math
import socket
from os import listdir
from os.path import isfile, join

import numpy as np

baseline = {'simlarge': os.environ['REPO_PATH'] + '/data/bodytrack/' + str(socket.gethostname()) + '/REG/28/simlarge/28_3_0_0_0_0_0_0_0_0_'}
threshold = {'simlarge': 100.0}

def readOutput(pathToFile):
  try:
    with open(str(pathToFile), 'r') as f:
      data = {}
      for line in f:
        framePoses = line.split()
        data[str(framePoses[0])] = []
        for pose in framePoses[1:]:
          data[str(framePoses[0])].append(float(pose))
      f.close()
  
      return data

  except IOError:
    print 'WARNING: missing data ' + pathToFile
    return None

def getData(experiment):
  outputFiles = [f for f in listdir(experiment) if f.startswith('output')]
  data = []
  for f in outputFiles:
    data.append(readOutput(join(experiment, f)))

  return data

def distortion(baselinePoses, poses):
  numOfFrames = len(baselinePoses)
  numOfBodyParts = len(baselinePoses['0'])
  
  relmseTot = 0.0
  distortion = {}
  distortionList = []
  distortionListPair = []
  for frame in range(0, numOfFrames):
    relmse = 0.0
    mag = 0.0
    for bodyPart in range(0, numOfBodyParts):
      error = (baselinePoses[str(frame)][bodyPart] - poses[str(frame)][bodyPart])
      se = math.pow(error, 2)
      relse = se/math.pow(baselinePoses[str(frame)][bodyPart], 2)
      relmse = relmse + relse
      mag = mag + math.pow(baselinePoses[str(frame)][bodyPart], 2)
    relmse = relmse/numOfBodyParts
    relmseW = relmse/math.sqrt(mag)
    relmseTot = relmseTot + (relmseW)
    distortion[str(frame)] = relmseW
    distortionList.append(relmseW)
    distortionListPair.append((relmseW, frame))

  peak = min(distortionList)

  return peak

def outputDistortion(pathToOutputDir, inputName):
  pathToBaseline = baseline[inputName]
  dataBaseline = getData(pathToBaseline)
  dataExperiment = getData(pathToOutputDir)

  distortions = []
  for db in dataBaseline:
    for de in dataExperiment:
      distortionValue = distortion(db, de)
      distortions.append(distortionValue)

  return max(distortions)

def isDistorted(inputName, distortion):
  isDistorted = False
  if (distortion > threshold[inputName]):
    isDistorted = True

  return isDistorted

def getThreshold(pathToOutputFiles):
  dataAll = getData(pathToOutputFiles)
  distortions = []
  lenDataAll = len(dataAll)
  for i in range(lenDataAll):
    for j in range((i + 1), lenDataAll):
      distortion = distortion(dataAll[i], dataAll[j])
      distortions.append(distortion)

  print(distortions)
  print('THRESHOLD ' + str(min(distortions)))

  return

#pathToOutputFiles = sys.argv[1]
#getThreshold(pathToOutputFiles)
