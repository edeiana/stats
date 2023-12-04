#!/usr/bin/env python
import os
import sys
import socket
import importlib
import traceback
import adddeps  # fix sys.path

import opentuner
from opentuner import ConfigurationManipulator
from opentuner import IntegerParameter
from opentuner import LogIntegerParameter
from opentuner import SwitchParameter
from opentuner import MeasurementInterface
from opentuner import Result

repoPath = os.environ['REPO_PATH']
sys.path.append(repoPath + '/scripts')

import utils
import profiler

class autotuneProgram(MeasurementInterface):

  # Fields
  args = None
  finalConfFlag = False
  configurationsFileName = 'configurations.json'
  crashedConfigurationsFileName = 'crashedConfigurations.json'
  outputDistortionModule = None
  configurationsExplored = 0

  def manipulator(self):
    """
    Define the search space by creating a
    ConfigurationManipulator
    """

    # Read the range of each dimension of the design space
    inputFile = os.environ['RANGE_FILE']
    ranges = utils.readFile(inputFile)

    # Describe the design space to opentuner
    param = 0
    manipulator = ConfigurationManipulator()
    for elem in ranges:
      manipulator.add_parameter(IntegerParameter(str(param), 0, str(elem - 1)))
      param += 1

    # Load outputDistortion module if possible
    benchmark = os.environ['BENCHMARK_NAME']
    self.outputDistortionModule = None
    try:
      self.outputDistortionModule = importlib.import_module('benchmark.' + benchmark + '.outputDistortion')
    except ImportError:
      print('WARNING: no output distortion module')
      self.outputDistortionModule = None

    return manipulator


  def run(self, desired_result, input, limit):
    result = None
    """
    Compile and run a given configuration then
    return performance
    """

    # Read the configuration to run
    cfg = desired_result.configuration.data
    if (not cfg): # no ranges
      sys.exit(0)
      return

    # Translate the configuration into a string representation
    cfgStr = self.getCfgStr(cfg)
    print('AUTOTUNER:   Configuration ' + str(self.configurationsExplored) + ' chosen = ' + cfgStr)
    self.configurationsExplored += 1

    configurations, pathToFiles = self.readConfigurations()
    if (cfgStr in configurations):

      # The configuration has been executed. Return the previous results
      result = configurations[cfgStr]

    else:
      crashedFlag = False
      self.myCompile(cfg, 0)

      # Invoke the profiler to test the current configuration
      try:
        sys.stderr.write('EXPLORING CONFIGURATION: ' + cfgStr + '\n')

        # Define the output directory
        pathToOutputDir = self.getInfoStr()
        pathToOutputDir += '/' + cfgStr

        # Run
        result = profiler.profile(pathToOutputDir)
      except KeyboardInterrupt:
        #raise
        result = self.getResultForCrash()
        sys.exit(1)
      except Exception as e:
        sys.stderr.write('ERROR: opentuner - profiler\n')
        sys.stderr.write(str(e) + '\n')
        traceback.print_exc()
        result = self.getResultForCrash()
        self.writeConfigurations(cfgStr, result, os.path.join(pathToFiles, self.crashedConfigurationsFileName))
        crashedFlag = True

      # The configuration run. Compute the output distortion
      outputDistortionFlag = bool(int(os.environ['OUTPUT_DISTORTION_FLAG']))
      isDistorted = False
      if (('outputDistortion' in result) and (outputDistortionFlag)):
        inputName = os.environ['INPUT_NAME']
        isDistorted = self.outputDistortionModule.isDistorted(inputName, result['outputDistortion'])
        if (isDistorted):
          result['experimentTime'] = float('inf')

      # Dump the results
      if ((not crashedFlag) and (not isDistorted)):
        self.writeConfigurations(cfgStr, result, os.path.join(pathToFiles, self.configurationsFileName))

    # Print results (on stderr, otherwise opentuner won't print)
    sys.stderr.write('\n\nConfiguration: ' + cfgStr + ' Results: ' + str(result) + '\n\n')

    return Result(time=result['experimentTime'])


  def save_final_config(self, configuration):
    """called at the end of tuning"""
    self.finalConfFlag = True
    configurations, _ = self.readConfigurations()
    bestConfiguration, bestExecutionTime = self.getBestConfiguration(configurations)
    self.myCompile(bestConfiguration, bestExecutionTime)
    
    return



  def getArgs(self):
    hostname = socket.gethostname()
    args = {}
    args['argsSet'] = os.environ['ARGS_TMP']

    configPath = os.environ['REPO_PATH'] + '/config/' + hostname + '.json'
    configJson = utils.readJson(configPath)
    args['configJson'] = configJson

    benchmark = os.environ['BENCHMARK_NAME']
    args['benchmark'] = benchmark

    numOfCores = int(os.environ['NUM_OF_CORES'])
    numOfIterations = int(os.environ['MAX_ITERATIONS'])
    htFlag = bool(int(os.environ['HT_FLAG']))
    pwFlag = bool(int(os.environ['PW_FLAG']))
    args['configBenchmarkJson'] = {'numOfCores': numOfCores, 'numOfIterations': numOfIterations, 'HT': htFlag, 'PW': pwFlag}

    return args


  def getInfoStr(self):
    inputName = os.environ['INPUT_NAME']

    hostname = socket.gethostname()

    repoPath = os.environ['REPO_PATH']
    benchmarkName = os.environ['BENCHMARK_NAME']

    numOfCores = int(os.environ['NUM_OF_CORES'])
    htFlag = bool(int(os.environ['HT_FLAG']))
    pwFlag = bool(int(os.environ['PW_FLAG']))

    modeStr = 'REG'
    if (htFlag):
      modeStr = 'HT'
    if (pwFlag):
      modeStr += '/PW'

    pathToFiles = repoPath + '/data/' + benchmarkName + '/' + hostname + '/' + modeStr + '/' + str(numOfCores) + '/' + inputName

    return pathToFiles   

  def getCfgStr(self, cfg):
    cfgStr = ''
    indexes = utils.getIndexes(cfg)
    for index in indexes:
      cfgStr += str(index) + '_'

    return cfgStr

  def getResultForCrash(self):
    result = {}
    result['experimentTime'] = float('inf')

    return result

  def writeConfigurations(self, cfgStr, result, pathToConfigurationsFile):
    configurations = {}
    if (os.path.exists(pathToConfigurationsFile)):
      configurations = utils.readJson(pathToConfigurationsFile)
    configurations[cfgStr] = result
    utils.writeJson(pathToConfigurationsFile, configurations)

    return

  def readConfigurations(self):
    pathToFiles = self.getInfoStr()
    configurations = {}
    self.args = self.getArgs()
    configJson = self.args['configBenchmarkJson']
    pathToConfigurationsFile = os.path.join(pathToFiles, self.configurationsFileName)
    if (os.path.exists(pathToConfigurationsFile)):
      configurations = utils.readJson(pathToConfigurationsFile)

    return configurations, pathToFiles

  def getCfgDict(self, cfg):
    cfgAsDict = {}
    i = 0
    for elem in cfg.split('_')[:-1]:
      cfgAsDict[str(i)] = int(elem)
      i += 1

    return cfgAsDict

  def getBestConfiguration(self, configurations):
    if (len(configurations) > 0):
      bestExecutionTime = configurations[configurations.keys()[0]]['experimentTime']
      bestConfiguration = configurations.keys()[0]
      for k in configurations:
        if (configurations[k]['experimentTime'] < bestExecutionTime):
          bestExecutionTime = configurations[k]['experimentTime']
          bestConfiguration = k
      bestConfigurationAsDict = self.getCfgDict(bestConfiguration)
      return bestConfigurationAsDict, bestExecutionTime
    else:
      print('ERROR: no best configuration')
      sys.exit(1)


  def myCompile(self, cfg, executionTime):
    indexes = utils.getIndexes(cfg)

    inputName = os.environ['INPUT_NAME']
    outputFile = os.environ['INDEX_FILE']
    utils.writeFile(outputFile, indexes)

    repoPath = os.environ['REPO_PATH']
    if (self.finalConfFlag):
      args = self.args

      hostname = socket.gethostname()
      benchmarkName = args['benchmark']

      configJson = args['configBenchmarkJson']
      numOfCores = configJson['numOfCores']
      htFlag = configJson['HT']
      pwFlag = configJson['PW']

      modeStr = 'REG'
      if (htFlag):
        modeStr = 'HT'
      if (pwFlag):
        modeStr += '/PW'

      bestConfFile = repoPath + '/data/' + benchmarkName + '/' + hostname + '/' + modeStr + '/' + str(numOfCores) + '/' + inputName + '/bestConfiguration.json'
      bestConf = {'conf': indexes, 'time': executionTime}
      utils.writeJson(bestConfFile, bestConf)

    os.system(repoPath + '/src/scripts/backEnd') # generate the binary of the best configuration found

    return

if __name__ == '__main__':
  argparser = opentuner.default_argparser()
  autotuneProgram.main(argparser.parse_args())
