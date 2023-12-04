import os
import sys
import socket
import importlib
import numpy as np
import scipy.stats
import shutil
import traceback

import utils

allottedTimeMultiplier = 5

repoPath = os.environ['REPO_PATH']
benchmark = os.environ['BENCHMARK_NAME']
copyOutputModule = None
try:
  copyOutputModule = importlib.import_module('benchmark.' + benchmark + '.copyOutput')
except ImportError:
  print('WARNING: no copy output module')
  copyOutputModule = None

def medianConfidenceInterval(data, confidence = 0.90):
  a = 1.0 * np.array(data)
  n = len(a)
  m, se = np.median(a), scipy.stats.sem(a)
  h = se * scipy.stats.t._ppf((1.0 + confidence) / 2.0, n - 1)

  return m, (m-h, m+h)

def run(pathToOutputDir):
  hostname = socket.gethostname()

  inputName = os.environ['INPUT_NAME']

  repoPath = os.environ['REPO_PATH']

  configPathG = repoPath + '/config/' + hostname + '.json'
  configJsonG = utils.readJson(configPathG)

  numOfCores = int(os.environ['NUM_OF_CORES'])
  htFlag = bool(int(os.environ['HT_FLAG']))
  pwFlag = bool(int(os.environ['PW_FLAG']))

  minNumOfIterations = int(os.environ['MIN_ITERATIONS'])
  maxNumOfIterations = int(os.environ['MAX_ITERATIONS'])
  
  numOfIterationsForCI = max(minNumOfIterations, 3)
  
  benchmarkDir = os.environ['PKG_SUBDIR']

  modeStr = 'REG'
  localCoresList = configJsonG['REG']
  if (htFlag):
    modeStr = 'HT'
    localCoresList = configJsonG['HT']

  if (pwFlag):
    modeStr += '/PW'

  # Information needed only if we are compiling
  infoStr = pathToOutputDir
  if (not os.path.exists(infoStr)):
    os.makedirs(infoStr)

  burnP6Cond = ((not htFlag) and (not pwFlag))

  maxNumOfCores = len(localCoresList)
  halfNumOfCores = maxNumOfCores / 2

  if (numOfCores > maxNumOfCores):
    numOfCores = maxNumOfCores

  separator = ','
  coresListStr = ''
  i = 0
  for c in range(numOfCores):
    coresListStr += (str(localCoresList[c]) + separator)
    i += 1
  coresListStr = coresListStr[:-1] # remove last ','

  localCoresListP6 = []
  if (numOfCores < halfNumOfCores):
    for c in range(numOfCores, halfNumOfCores):
      localCoresListP6.append(localCoresList[c])

  parsecDir = repoPath + '/parsec-3.0'

  # kill zombie burnP6, just in case something went wrong in previous calls of run.py
  os.system('killall burnP6')

  pathToBenchmarkExitCodeFile = repoPath + '/parsec-3.0/pkgs/' + benchmarkDir + '/' + benchmark + '/run/benchmarkExitCode.txt';
  confidenceThreshold = 0.9
  timeList = []
  for it in range(maxNumOfIterations):
    dataStr = '_it_' + str(it) + '_'

    timeStr = infoStr + '/time' + dataStr + '.txt'
    if (os.path.exists(timeStr)):
      print('WARNING: data already generated ' + timeStr)
      continue

    if (burnP6Cond):
      for c in localCoresListP6:
        os.system('taskset -c ' + str(c) + ' burnP6 &')

    currDir = os.getcwd()
    os.chdir(parsecDir)

    # Execute benchmark
    try:
      runRes = os.system('taskset -c ' + coresListStr  + ' ' + repoPath + '/scripts/runBenchmark')
      timeInFile = repoPath + '/parsec-3.0/pkgs/' + benchmarkDir + '/' + benchmark + '/run/benchmark.out';
      tmpFile = repoPath + '/parsec-3.0/pkgs/' + benchmarkDir + '/' + benchmark + '/run/fullTime.out';
      timeOutFile = repoPath + '/parsec-3.0/pkgs/' + benchmarkDir + '/' + benchmark + '/run/time.txt';
      timeOverheadFile = repoPath + '/parsec-3.0/pkgs/' + benchmarkDir + '/' + benchmark + '/run/overhead.txt';
      os.system('tail -n 3 ' + timeInFile + ' | head -n 1 | awk \'{print $2}\' > ' + tmpFile)
      with open(tmpFile, 'r') as timing_file:
        full_time = timing_file.readlines()[0]
        split_full_time = full_time.rstrip().split('m')
        seconds = float(split_full_time[-1].split('s')[0])
        minutes = float(split_full_time[0])
        time = 60*minutes + seconds
        with open(timeOutFile, 'w') as out_file:
          out_file.write(str(time))

      with open(timeOverheadFile, 'w') as ov_file:
        ov_file.write('0.0')
      
    except:
      errorMessage = 'ERROR: run return code ' + str(runRes) + '\n'
      sys.stderr.write(errorMessage)
      traceback.print_exc()
      raise Exception(errorMessage)

    os.chdir(currDir)

    if (burnP6Cond):
      os.system('killall burnP6')

    # Handle return code
    res = utils.readReturnCodeFromFile(pathToBenchmarkExitCodeFile)
    if (res == None): # something bad happened
      utils.errorMsg('ERROR: ' + pathToBenchmarkExitCodeFile + ' does not exist\n')
      
    if (res == 130): # ctrl-c
      errorMessage = 'EXCEPTION: ctrl-c\n'
      sys.stderr.write(errorMessage)
      shutil.rmtree(infoStr)
      raise KeyboardInterrupt(errorMessage)
    elif (res == 143): # program killed
      errorMessage = 'WARNING: program killed\n'
      sys.stderr.write(errorMessage)
      shutil.rmtree(infoStr)
      break # go to next configuration
    elif (res == 139): # program sigsegv
      errorMessage = 'WARNING: program sigsegv\n'
      sys.stderr.write(errorMessage)
      shutil.rmtree(infoStr)
      raise Exception(errorMessage)
    elif (res != 0): # something wrong happened
      errorMessage = 'ERROR: run.py something wrong happened'
      sys.stderr.write(errorMessage)
      shutil.rmtree(infoStr)
      raise Exception(errorMessage)

    timeFrom = parsecDir + '/pkgs/' + benchmarkDir + '/' + benchmark + '/run/time.txt'
    timeTo = infoStr + '/time' + dataStr + '.txt'
    totTime = utils.readTime(timeFrom)
    if(totTime != None):
      utils.writeFile(timeTo, [totTime])
      # set max amount of time for a run
      # must be large enough so that parsecmgmt can finish setting up run dir
      timeToRun = int(10 + allottedTimeMultiplier*totTime)
      try:
        if (timeToRun < os.environ['MAX_RUN_TIME']):
          os.environ['MAX_RUN_TIME'] = str(timeToRun)
      except KeyError:
        os.environ['MAX_RUN_TIME'] = str(timeToRun)
    else:
      totTime = float('inf')

    overheadFrom = parsecDir + '/pkgs/' + benchmarkDir + '/' + benchmark + '/run/overhead.txt'
    overheadTo = infoStr + '/overhead' + dataStr + '.txt'
    totOverhead = utils.readTime(overheadFrom)
    if(totOverhead != None):
      utils.writeFile(overheadTo, [totOverhead])
    else:
      totOverhead = 0.0

    #if (totTime != float('inf')):
    #  if (pwFlag):
    #    powerFrom = parsecDir + '/pkgs/' + benchmarkDir + '/' + benchmark + '/run/power.txt'
    #    powerTo = infoStr + '/power' + dataStr + '.txt'
    #    os.system('cp ' + powerFrom + ' ' + powerTo)

    if (totTime != float('inf')):
      if (copyOutputModule != None):
        copyOutputModule.copyOutput(infoStr, it)

    # if there are at least 3 iterations
    if (it > numOfIterationsForCI):
      # check if time CI is within 10% of the median
      actualTime = totTime - totOverhead
      timeList.append(actualTime)

      median, ci = medianConfidenceInterval(timeList, confidenceThreshold)

      up = 1.0 + (1.0 - confidenceThreshold)
      dw = confidenceThreshold

      medianDw = dw*median
      medianUp = up*median

      ciDw = ci[0]
      ciUp = ci[1]

      if ((medianDw <= ciDw) and (ciUp <= medianUp)):
        break

  return

