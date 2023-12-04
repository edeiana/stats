import os
import re
import sys
import socket

import utils

def getArgs():
  args = {}
  numOfArgs = 1

  lenArgv = len(sys.argv)
  if (lenArgv < numOfArgs + 1):
    print('USAGE: ' + sys.argv[0] + ' path/to/conf/dir')
    sys.exit(1)

  args['pathToConfDir'] = sys.argv[1]

  return args

def getTopologyData(args):
  hostname = socket.gethostname()

  pathToConfDir = args['pathToConfDir']
  if (not os.path.exists(pathToConfDir)):
    os.mkdir(pathToConfDir)

  hwlocCmd = 'hwloc-gather-topology ' + pathToConfDir + '/' + hostname
  try:
    res = os.system(hwlocCmd)
  except:
    sys.stderr.write('ERROR: hwloc missing, return code: ' + str(res) + '\n')
    sys.exit(1)
 
  topologyData = {}
  currNuma = None
  pathToTopologyFile = pathToConfDir + '/' + hostname + '.output'
  with open(pathToTopologyFile, 'r') as f:
    for line in f:
      if (re.match('^ *NUMANode', line)):
        currNuma = int(line.split()[1].split('#')[1])
        topologyData[currNuma] = {}
      elif (re.match('^ *Core', line)):
        currPCore = int(line.split()[2].strip('()').split('#')[1])
        topologyData[currNuma][currPCore] = []
      elif (re.match('^ *PU', line)):
        currLCore = int(line.split()[2].strip('()').split('#')[1])
        topologyData[currNuma][currPCore].append(currLCore)

    f.close()

  toRemove1 = pathToConfDir + '/*.output'
  toRemove2 = pathToConfDir + '/*.tar.bz2'
  os.system('rm ' + toRemove1 + ' ' + toRemove2)

  return topologyData

def getLCoresPerPCore(topologyData):
  numaK = list(topologyData.keys())[0]
  pcoreK = list(topologyData[numaK])[0]
  result = len(topologyData[numaK][pcoreK])

  return result

def getREG(topologyData):
  topologyREG = []
  numaKeys = sorted(list(topologyData.keys()))
  numOfLCores = getLCoresPerPCore(topologyData)
  for lcoreK in range(numOfLCores):
    for numaK in numaKeys:
      pcoreKeys = sorted(list(topologyData[numaK].keys()))
      for pcoreK in pcoreKeys:
        topologyREG.append(topologyData[numaK][pcoreK][lcoreK])

  return list(reversed(topologyREG)) # reverse the list to have core 0 as last element

def getHT(topologyData):
  topologyHT = []
  numaKeys = sorted(list(topologyData.keys()))
  numOfLCores = getLCoresPerPCore(topologyData)
  for numaK in numaKeys:
    for lcoreK in range(numOfLCores):
      pcoreKeys = sorted(list(topologyData[numaK].keys()))
      for pcoreK in pcoreKeys:
        topologyHT.append(topologyData[numaK][pcoreK][lcoreK])

  return list(reversed(topologyHT)) # reverse the list to have core 0 as last element

def createJsonFile(args, topologyREG, topologyHT):
  jsonData = {'REG': topologyREG, 'HT': topologyHT}
  pathToConfDir = args['pathToConfDir']
  hostname = socket.gethostname()
  utils.writeJson(pathToConfDir + '/' + hostname + '.json', jsonData)

  return


args = getArgs()
topologyData = getTopologyData(args)
topologyREG = getREG(topologyData)
topologyHT = getHT(topologyData)
createJsonFile(args, topologyREG, topologyHT)

