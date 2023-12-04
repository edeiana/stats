import sys
import tempfile

import utils

def readSeedConf(pathToFile):
  seedConf = []
  with open(str(pathToFile), 'r') as f:
    for line in f:
      if (line != ''):
        seedConf.append(line)
    f.close()
  
  return seedConf

def genDictFromList(listArg):
  dictFromList = {}
  for i in range(len(listArg)):
    dictFromList[str(i)] = int(listArg[i])

  return dictFromList

def getSeedConfJson(seedConf):
  seedConfJson = []
  for elem in seedConf:
    elemAsList = elem.split('_')
    if (elemAsList[-1] == '') or (elemAsList[-1] == '\n'):
      elemAsList = elemAsList[:-1]
    seedConfJson.append(genDictFromList(elemAsList))

  return seedConfJson

def genSeedConfFiles(seedConfJson):
  filesList = []
  for elem in seedConfJson:
    newfile, pathToFile = tempfile.mkstemp(suffix = '.json')
    utils.writeJson(pathToFile, elem)
    filesList.append(pathToFile)

  return filesList

def genSeedConfString(filesList):
  opentunerSeedConfFlag = '--seed-configuration='
  seedConfString = ''
  for elem in filesList:
    seedConfString += opentunerSeedConfFlag + elem + ' '

  return seedConfString

def genSeedConf(pathToSeedConf):
  seedConf = readSeedConf(pathToSeedConf)
  seedConfJson = getSeedConfJson(seedConf)
  filesList = genSeedConfFiles(seedConfJson)
  seedConfString = genSeedConfString(filesList)

  return seedConfString


seedConfString = genSeedConf(sys.argv[1])
print(seedConfString)

