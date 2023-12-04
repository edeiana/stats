import os
import sys
import numpy as np
from os import listdir
from os.path import isfile, join

def readPower(pathToFile):
  dataAll = []
  with open(str(pathToFile), 'r') as f:
    for line in f:
      dataStr = line.split()
      data = float(dataStr[1])
      dataAll.append(data)
    f.close()
  
  return dataAll

def getPowerData(experiment):
  pathToFiles = experiment
  onlyFiles = [f for f in listdir(pathToFiles) if isfile(join(pathToFiles, f)) and f.startswith('power')]
  powerDataAll = []
  for f in onlyFiles:
    powerData = readPower(pathToFiles + '/' + f)
    if (len(powerData) != 0):
      powerDataAll.append(powerData)

  return powerDataAll

def getMeanEnergy(powerDataAll):
  energyAll = []
  for powerData in powerDataAll:
    energyAll.append(sum(powerData))

  return np.mean(energyAll)


powerDataAll = getPowerData(sys.argv[1])
meanEnergy = getMeanEnergy(powerDataAll)

print meanEnergy

