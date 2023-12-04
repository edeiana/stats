import sys
import utils

# Process the command line arguments
def getArgs():
  args = {}
  numOfArgs = 1 

  lenArgv = len(sys.argv)
  if (lenArgv < numOfArgs + 1):
    print('USAGE: $ ' + str(sys.argv[0] + ' path/to/configurations.json ...'))
    sys.exit(1)

  args['pathsToConfJson'] = sys.argv[1:]

  return args

def processData(confJson):
  # Get json as list of tuples: (time, conf)
  confJsonAsListNoInf = []
  confJsonAsListInfOnly = []
  for key in confJson:
    executionTime = float(confJson[key]['experimentTime'])
    if (executionTime == float('inf')):
      confJsonAsListInfOnly.append((executionTime, key, confJson[key]['status']))
    else:
      confJsonAsListNoInf.append((executionTime, key))

  minExecutionTime = None
  try:
    minExecutionTime = min(confJsonAsListNoInf)
  except ValueError:
    minExecutionTime = None

  maxExecutionTime = None
  try:
    maxExecutionTime = max(confJsonAsListNoInf)
  except ValueError:
    maxExecutionTime = None

  numOfInfConfKilled = len([elem for elem in confJsonAsListInfOnly if elem[2] == 'killed'])
  numOfInfConfSigsegv = len([elem for elem in confJsonAsListInfOnly if elem[2] == 'sigsegv'])
  numOfInfConfUnknown = len([elem for elem in confJsonAsListInfOnly if elem[2] == 'unknown'])
  numOfConf = len(confJsonAsListNoInf) + len(confJsonAsListInfOnly)

  return minExecutionTime, maxExecutionTime, numOfInfConfKilled, numOfInfConfSigsegv, numOfInfConfUnknown, numOfConf

def mergeData(minExecutionTimeList, maxExecutionTimeList, numOfInfConfKilledList, numOfInfConfSigsegvList, numOfInfConfUnknownList, numOfConfList):
  minExecutionTimeListNoNone = [elem for elem in minExecutionTimeList if elem != None]
  minExecutionTime = None
  try:
    minExecutionTime = max(minExecutionTimeListNoNone)
  except ValueError:
    minExecutionTime = None

  maxExecutionTimeListNoNone = [elem for elem in maxExecutionTimeList if elem != None]
  maxExecutionTime = None
  try:
    maxExecutionTime = max(maxExecutionTimeListNoNone)
  except ValueError:
    maxExecutionTime = None

  numOfInfConfKilled = sum(numOfInfConfKilledList)
  numOfInfConfSigsegv = sum(numOfInfConfSigsegvList)
  numOfInfConfUnknown = sum(numOfInfConfUnknownList)
  numOfConf = sum (numOfConfList)

  return minExecutionTime, maxExecutionTime, numOfInfConfKilled, numOfInfConfSigsegv, numOfInfConfSigsegv, numOfConf


args = getArgs()

minExecutionTimeList = []
maxExecutionTimeList = []
numOfInfConfKilledList = []
numOfInfConfSigsegvList = []
numOfInfConfUnknownList = []
numOfConfList = []
for pathToConfJson in args['pathsToConfJson']:
  confJson = utils.readJson(pathToConfJson)
  minExecutionTime, maxExecutionTime, numOfInfConfKilled, numOfInfConfSigsegv, numOfInfConfUnknown, numOfConf = processData(confJson)
  minExecutionTimeList.append(minExecutionTime)
  maxExecutionTimeList.append(maxExecutionTime)
  numOfInfConfKilledList.append(numOfInfConfKilled)
  numOfInfConfSigsegvList.append(numOfInfConfSigsegv)
  numOfInfConfUnknownList.append(numOfInfConfUnknown)
  numOfConfList.append(numOfConf)

minExecutionTimeResult, maxExecutionTimeResult, numOfInfConfKilledResult, numOfInfConfSigsegvResult, numOfInfConfUnknownResult, numOfConfResult = mergeData(minExecutionTimeList, maxExecutionTimeList, numOfInfConfKilledList, numOfInfConfSigsegvList, numOfInfConfUnknownList, numOfConfList)

resultAsStr = 'Minimum execution time: ' + str(minExecutionTimeResult) + '\n'
resultAsStr += 'Maximum execution time: ' + str(maxExecutionTimeResult) + '\n'
resultAsStr += 'Number of configurations killed: ' + str(numOfInfConfKilledResult) + '\n'
resultAsStr += 'Number of configurations sigsegv: ' + str(numOfInfConfSigsegvResult) + '\n'
resultAsStr += 'Number of configurations unknown: ' + str(numOfInfConfUnknownResult) + '\n'
resultAsStr += 'Total number of configurations: ' + str(numOfConfResult) + '\n'
print(resultAsStr)

