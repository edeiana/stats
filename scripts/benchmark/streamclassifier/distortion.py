import os
import sys
from os import listdir
from os.path import isfile, join

import numpy as np

sys.path.append('../')

import utils

coordNum = 10

def getLevels(pathToBaselineOutput):
  onlyFilesBaseline = [f for f in listdir(pathToBaselineOutput) if isfile(join(pathToBaselineOutput, f))]
  levels = set()
  for f in onlyFilesBaseline:
    level = int(f.split('_')[0])
    levels.add(level)

  levelsList = list(levels)
  sortedLevels = sorted(levelsList)
  return sortedLevels

def readOutputSingle(pathToFile):
  try:
    with open(str(pathToFile), 'r') as f:
      data = {}
      j = 0
      pointId = None
      for line in f:
        noNewLine = line.strip('\n\r')
        if (j == 0): # id
          pointId = str(noNewLine)
          data[pointId] = {}
        elif (j == 1):
          centroidId = int(noNewLine)
          data[pointId]['centroid'] = centroidId
        elif (j == 3):
          coordAll = str(noNewLine).split(' ')
          coordAll = coordAll[0:(len(coordAll) - 1)]
          coord = [float(elem) for elem in coordAll[0:coordNum]]
          label = int(float(coordAll[-1]))
          data[pointId]['coord'] = coord
          data[pointId]['label'] = label
        j += 1
        if (j == 5):
          j = 0

      f.close()

      return data

  except IOError:
    print('WARNING: missing data ' + pathToFile)
    return None

def readOutput(pathToFiles):
  data = {}
  levels = getLevels(pathToFiles)
  for level in levels:
    data[str(level)] = {}

  onlyFiles = [f for f in listdir(pathToFiles) if isfile(join(pathToFiles, f))]
  for f in onlyFiles:
    level = str(f.split('_')[0])
    chunk = str(f.split('_')[1])
    data[level][chunk] = readOutputSingle(join(pathToFiles, f))

  return data
 
def getData(experiment, medianIt):
  data = readOutput(experiment + '/output_it_' + str(medianIt) + '_')

  return data

def getNum(data):
  result = {}
  for point in data: #for each point
    centroid = str(data[point]['centroid'])
    label = str(data[point]['label'])
    if (centroid not in result):
      result[centroid] = {}
    if (label not in result[centroid]):
      result[centroid][label] = 0
    result[centroid][label] += 1

  return result

def getDen(data):
  resultCentroid = {}
  resultLabel = {}
  for point in data:
    centroid = str(data[point]['centroid'])
    if (centroid not in resultCentroid):
      resultCentroid[centroid] = 0
    resultCentroid[centroid] += 1
    
    label = str(data[point]['label'])
    if (label not in resultLabel):
      resultLabel[label] = 0
    resultLabel[label] += 1

  return resultCentroid, resultLabel

def computeRecall(num, den, numOfPoints):
  recall = 0.0
  for centroid in num:
    for label in num[centroid]:
      recall += (float(num[centroid][label]) * float(num[centroid][label])) / float(den[label])
  recall /= numOfPoints

  return recall

def computePrecision(num, den, numOfPoints):
  precision = 0.0
  for centroid in num:
    for label in num[centroid]:
      precision += (float(num[centroid][label]) * float(num[centroid][label])) / float(den[centroid])
  precision /= numOfPoints

  return precision

def computeFscore(precision, recall, alpha = 0.5):
  result = 1 / (alpha*(1/precision) + (1 - alpha)*(1/recall))

  return result

def outputDistortionSingle(baselineData, experimentData):
  numBaseline = getNum(baselineData)
  pdenBaseline, rdenBaseline = getDen(baselineData)

  numExperiment = getNum(experimentData)
  pdenExperiment, rdenExperiment = getDen(experimentData)

  baselineNumOfPoints = len(baselineData)
  precisionBaseline = computePrecision(numBaseline, pdenBaseline, baselineNumOfPoints)
  recallBaseline = computeRecall(numBaseline, rdenBaseline, baselineNumOfPoints)

  experimentNumOfPoints = len(experimentData)
  precisionExperiment = computePrecision(numExperiment, pdenExperiment, experimentNumOfPoints)
  recallExperiment = computeRecall(numExperiment, rdenExperiment, experimentNumOfPoints)

  fscoreBaseline = computeFscore(precisionBaseline, recallBaseline)
  fscoreExperiment = computeFscore(precisionExperiment, recallExperiment)

  result = fscoreBaseline - fscoreExperiment # fscore is between 0 (bad clustering) and 1 (excellent clustering)
  if (result < 0):
    result = 0
  #result = fscoreExperiment

  return result

def outputDistortion(baselineData, experimentData):
  distortionList = []
  distortionAll = {}
  for level in baselineData:
    for chunk in baselineData[level]:
      if (level not in distortionAll):
        distortionAll[level] = {}
      distortion = outputDistortionSingle(baselineData[level][chunk], experimentData[level][chunk])
      distortionList.append(distortion)
      distortionAll[level][chunk] = distortion

  distortionAverage = np.average(distortionList)
  distortionPeak = max(distortionList)

  return distortionPeak

def getDataLen(experiment):
  outputFiles = [f for f in listdir(experiment) if f.startswith('output')]

  return len(outputFiles)

def getThreshold(pathToOutputFiles):
  jsonTmpPath = './data.json'
  distortions = []
  lenDataAll = getDataLen(pathToOutputFiles)
  for i in range(lenDataAll):
    for j in range((i + 1), lenDataAll):
      datai = getData(pathToOutputFiles, i)
      dataj = getData(pathToOutputFiles, j)
      distortion = outputDistortion(datai, dataj)
      distortions.append(distortion)
      jsonTmp = {pathToOutputFiles: distortions}
      utils.writeJson(jsonTmpPath, jsonTmp)

  print distortions

  return

pathToOutputFiles = sys.argv[1]
getThreshold(pathToOutputFiles)

