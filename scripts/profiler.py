import os
import sys
import shutil
import importlib

#sys.path.append('../lib')

import utils
import run

def execProfiler(pathToOutputDir):

  # Fetch env variables
  outputDistortionFlag = bool(int(os.environ['OUTPUT_DISTORTION_FLAG']))
  benchmark = os.environ['BENCHMARK_NAME']

  # Try to load benchmark-specific outputDistortion module
  outputDistortionModule = None
  try:
    outputDistortionModule = importlib.import_module('benchmark.' + benchmark + '.outputDistortion')
  except ImportError:
    sys.stderr.write('WARNING: no output distortion module\n')
    outputDistortionModule = None

  result = {}

  try:
    # run benchmark
    run.run(pathToOutputDir)
  except:
    sys.stderr.write('WARNING: profiler, exception raised on run()\n')
    raise

  # Get results: execution time, and output distortion (if possible)
  experimentTime, _ = utils.getTime(pathToOutputDir)
  result['experimentTime'] = experimentTime
  if ((outputDistortionModule != None) and (outputDistortionFlag)):
    inputName = os.environ['INPUT_NAME']
    result['outputDistortion'] = outputDistortionModule.outputDistortion(pathToOutputDir, inputName)

  # remove experiment directory
  #shutil.rmtree(experimentDir)

  return result


def profile(pathToOutputDir):
  result = execProfiler(pathToOutputDir)

  return result

