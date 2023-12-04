import os
import sys
import math
import json
import socket
import numpy as np
from os import listdir
from os.path import isfile, join

class KillException(Exception):
  pass

class SigsegvException(Exception):
  pass

def getNumOfCores(coresList):
  return len(coresList.split(','))

def readJson(pathToFile):
  data = {}
  with open(str(pathToFile)) as f:    
    data = json.load(f)
    f.close()

  return data

def writeJson(pathToFile, jsonData):
  with open(pathToFile, 'w') as f:
    json.dump(jsonData, f)
    f.close()

  return

def getTime(experimentDir):
  median, _, medianIt = computeExecutionTime(experimentDir)

  return median, medianIt

def getTimeAndVariance(experimentDir):
  median, variance, medianIt = computeExecutionTime(experimentDir)

  return median, variance, medianIt

def computeExecutionTime(experiment):
  timeDataAll = getTimeIteration(experiment)

  if (len(timeDataAll) == 0):
    median = float('inf')
    variance = float('inf')
    medianIt = None
    return median, variance, medianIt

  time = [elem[0] for elem in timeDataAll]
  median = np.median(time)
  variance = np.var(time)

  medianIt = getMedianIteration(timeDataAll)

  return median, variance, medianIt

def getTimeIteration(experiment):
  pathToFiles = experiment
  onlyFiles = [f for f in listdir(pathToFiles) if isfile(join(pathToFiles, f)) and f.startswith('time')]
  timeDataAll = []
  for f in onlyFiles:
    it = getIteration(f)
    timeData = readTime(pathToFiles + '/' + f)
    overheadData = readTime(pathToFiles + '/' + f.replace('time', 'overhead'))
    timeDataAll.append((timeData - overheadData, it))

  return timeDataAll

def getMedianIteration(data):
  it = None
  sortedData = sorted(data)
  lenData = len(sortedData)
  if ((lenData % 2) == 0):
    it = sortedData[int(lenData/2)][1]
  else:
    it = sortedData[int(math.floor(lenData/2))][1]

  return it

def getIteration(fileName): # <---
  return int(fileName.split('_')[2])

def errorMsg(message):
  print(message)
  sys.exit(1)

def readFile(pathToFile):
  result = []
  with open(str(pathToFile), 'r') as f:
    line = f.readline()
    ranges = line.split()
    for r in ranges:
      result.append(int(r))
    f.close()
  
  return result

def readReturnCodeFromFile(pathToFile):
  result = None
  try:
    f = open(str(pathToFile), 'r')
    line = f.readline()
    result = int(line)
    f.close()
  except IOError:
    sys.stderr.write('ERROR: file ' + pathToFile + ' does not exist\n')
    return None
  
  return result

def readTime(pathToFile):
  result = None
  try:
    with open(str(pathToFile), 'r') as f:
      line = f.readline()
      result = float(line)
      f.close()
  except IOError:
    return None
  
  return result

def readString(pathToFile):
  with open(str(pathToFile), 'r') as f:
    line = f.readline()
    f.close()
  
  return str(line)

def writeFileAppend(pathToFile, data):
  dataStr=''
  with open(str(pathToFile), 'a') as f:
    for elem in data:
      dataStr += str(elem) + ', '
    f.write(dataStr)
    f.close()

  return

def writeFile(pathToFile, data):
  dataStr=''
  with open(str(pathToFile), 'w') as f:
    for elem in data:
      dataStr += str(elem) + ' '
    f.write(dataStr)
    f.close()

  return

def getList(string, separator):
  return [elem for elem in string.split(separator) if (elem != '')]

def getIndexes(cfg):
  maxIndex = max([int(key) for key in cfg])
  indexes = [0]*(maxIndex + 1)
  for key in cfg:
    indexes[int(key)] = cfg[key]
  
  return indexes

def getIndexesOfLength(cfg, maxIndex):
  indexes = [0]*(maxIndex + 1)
  for key in cfg:
    indexes[int(key)] = cfg[key]
  
  return indexes

def getIndexes2(ranges):
  indexes = []
  for elem in ranges:
    indexes.append(0)

  return indexes

def getIndexesStr(indexes):
  indexesStr = ''
  for elem in indexes:
    indexesStr += str(elem) + '_'

  return indexesStr

## Read the execution time of an iteration
#
#
def readTimeData(pathToFile):
  totSeconds = None
  with open(str(pathToFile), 'r') as f:
    for line in f:
      if (line.startswith('real')):
        lineTmp = line.split()[1]
        totSeconds = float(lineTmp)
        break
    f.close()
  
  return totSeconds

## Write the execution time of an iteration
#
#
def writeTimeData(pathToFile, data):
  with open(str(pathToFile), 'w') as f:
    f.write(str(data))
    f.close()

  return

def createTmpDir():
  cwd = os.getcwd()
  pid = os.getpid()
  tmpDirStr = cwd + '/.tmp' + str(pid)
  if (not os.path.exists(tmpDirStr)):
    os.makedirs(tmpDirStr)
  else:
    errorStr = 'ERROR: directory ' + tmpDirStr + ' already exists'
    errorMsg(errorStr)

  return tmpDirStr

## Computes the Pareto frontier
#
#
def paretoFrontier(x, y):
  myList = sorted([(x[i], y[i]) for i in range(0, len(x))])

  currX = myList[0][0]
  myListMax = [myList[0]]
  j = 0
  for i in range(0, len(x)):
    if (myList[i][0] == currX):
      if (myList[i][1] > myListMax[j][1]):
        myListMax[j] = myList[i]
    else:
      j += 1
      currX = myList[i][0]
      myListMax.append(myList[i])
      if(myList[i][1] > myListMax[j][1]):
        myListMax[j] = myList[i]

  pareto = [myListMax[0]]
  for elem in myListMax[1:]:
    if (elem[1] >= pareto[-1][1]):
      pareto.append(elem)

  xPareto = [pareto[i][0] for i in range(0, len(pareto))]
  yPareto = [pareto[i][1] for i in range(0, len(pareto))]

  return xPareto, yPareto

def getInfoStr(benchmark):
  inputName = os.environ['INPUT_NAME']
  numOfCores = int(os.environ['NUM_OF_CORES'])
  numOfIterations = int(os.environ['MAX_ITERATIONS'])
  htFlag = bool(int(os.environ['HT_FLAG']))
  pwFlag = bool(int(os.environ['PW_FLAG']))

  modeStr = 'REG'
  if (htFlag):
    modeStr = 'HT'
  if (pwFlag):
    modeStr += '/PW'

  indexFile = os.environ['INDEX_FILE']
  indexes = readFile(indexFile)
  indexesStr = getIndexesStr(indexes)

  hostname = socket.gethostname()
  infoStr = os.environ['REPO_PATH'] + '/data/' + benchmark + '/' + hostname + '/' + modeStr + '/' + str(numOfCores) + '/' + inputName + '/' + indexesStr

  return infoStr

