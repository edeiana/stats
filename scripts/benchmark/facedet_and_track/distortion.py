import os
import sys
import math
from os import listdir
from os.path import isfile, join

import numpy as np

## Get the poses of an instance of an experiment (i.e., an iteration)
#
#
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

## Compute the output distortion for an iteration of a configuration of an experiment
#
#
def outputDistortion(baselinePoses, poses):
  numOfFrames = len(baselinePoses)
  
  relmseTot = 0.0
  distortion = {}
  distortionList = []
  distanceAcc = 0.0
  for frame in range(0, numOfFrames):
    x1b = baselinePoses[str(frame)][0]
    y1b = baselinePoses[str(frame)][1]
    x2b = baselinePoses[str(frame)][0] + baselinePoses[str(frame)][2]
    y2b = baselinePoses[str(frame)][1] + baselinePoses[str(frame)][3]

    x1 = poses[str(frame)][0]
    y1 = poses[str(frame)][1]
    x2 = poses[str(frame)][0] + poses[str(frame)][2]
    y2 = poses[str(frame)][1] + poses[str(frame)][3]

    d1 = math.sqrt((math.pow((x1b - x1), 2) + math.pow((y1b - y1), 2)))
    d2 = math.sqrt((math.pow((x2b - x2), 2) + math.pow((y2b - y2), 2)))

    d = d1 + d2

    distanceAcc += d

    distortionList.append(d)

    distortion[str(frame)] = d

  peakMax = max(distortionList)

  return peakMax

def getBoxplotData(pathToOutputFiles):
  pathToFixedOutput = '../../data/facetrack/fixedOutput'
  fixedData = getData(pathToFixedOutput)
  dataAll = getData(pathToOutputFiles)
  distortions = []
  for data in dataAll:
    _, distortion, _ = outputDistortion(fixedData[0], data)
    distortions.append(distortion)

  print distortions
  print len(distortions)

  return


def getThreshold(pathToOutputFiles):
  dataAll = getData(pathToOutputFiles)

  distortions = []
  lenDataAll = len(dataAll)
  for i in range(lenDataAll):
    for j in range((i + 1), lenDataAll):
      distortion = outputDistortion(dataAll[i], dataAll[j])
      distortions.append(distortion)

  print distortions

  return

pathToOutputFiles = sys.argv[1]
getThreshold(pathToOutputFiles)

