import os
import sys
from os import listdir
from os.path import isfile, join

import numpy as np

sys.path.append('../')

import utils

coordNum = 128

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

def  big_s(x, center):
  len_x = len(x)
  total = 0
  for i in range(len_x):
    total += np.linalg.norm(x[i]-center)    

  return total/len_x

def daviesbouldin(k_list, k_centers):
  """ Davies Bouldin Index
  
  Parameters
  ----------
  k_list : list of np.arrays
      A list containing a numpy array for each cluster |c| = number of clusters
      c[K] is np.array([N, p]) (N : number of samples in cluster K, p : sample dimension)
  k_centers : np.array
      The array of the cluster centers (prototypes) of type np.array([K, p])
  """
  len_k_list = len(k_list)
  big_ss = np.zeros([len_k_list], dtype=np.float64)
  d_eucs = np.zeros([len_k_list, len_k_list], dtype=np.float64)
  for k in range(len_k_list):
    big_ss[k] = big_s(k_list[k], k_centers[k])
  for k in range(len_k_list):
    for l in range(0, len_k_list):
      d_eucs[k, l] = np.linalg.norm(k_centers[k]-k_centers[l])

  db = 0    
  for k in range(len_k_list):
    values = np.zeros([len_k_list-1], dtype=np.float64)
    for l in range(0, k):
      values[l] = (big_ss[k] + big_ss[l])/d_eucs[k, l]
    for l in range(k+1, len_k_list):
      values[l-1] = (big_ss[k] + big_ss[l])/d_eucs[k, l]
    db += np.max(values)

  res = db/len_k_list

  return res

def getPointCenterList(data):
  i = 0
  k_centers = []
  centerMap = {}
  for pointId in data:
    if (int(pointId) == int(data[pointId]['centroid'])):
      k_centers.append(data[pointId]['coord'])
      centerMap[pointId] = i
      i += 1

  k_list = []
  for center in range(len(centerMap)):
    k_list.append([])

  for pointId in data:
    k_list[centerMap[str(data[pointId]['centroid'])]].append(data[pointId]['coord'])

  return np.array(k_list), np.array(k_centers)

def outputDistortionSingle(baselineData, experimentData):
  k_listBaseline, k_centersBaseline = getPointCenterList(baselineData)
  k_listExperiment, k_centersExperiment = getPointCenterList(experimentData)

  indexBaseline = daviesbouldin(k_listBaseline, k_centersBaseline)
  indexExperiment = daviesbouldin(k_listExperiment, k_centersExperiment)

  result = indexExperiment - indexBaseline # good clustering means small Davies-Bouldin index
  if (result < 0): # experiment is better than baseline
    result = 0

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

