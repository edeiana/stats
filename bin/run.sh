#!/bin/bash

# Check the inputs
if test $# -lt 4 ; then
  echo "USAGE: `basename $0` -p BENCHMARK -i INPUT [-o PATH/TO/OUTPUT/DIR, -nc NUM_OF_CORES, -minit MIN_ITERATIONS, -maxit MAX_ITERATIONS, -ht, -pw, -outputdistortion]" ;
  exit 1 ;
fi

# include common functions
source ${REPO_PATH}/scripts/utils.sh ;

# Fetch the arguments
args=$@ ;

htFlag=$(isFlagSet -ht ${args}) ;
pwFlag=$(isFlagSet -pw ${args}) ;
outputDistortionFlag=$(isFlagSet -outputdistortion ${args}) ;

benchmarkName=$(getElem -p ${args}) ;
inputName=$(getElem -i ${args}) ;

# default number of cores: all logical cores available
numOfCores=$(getElem -nc ${args}) ;
if [[ "${numOfCores}" == "" ]] ; then
  numOfCores=`nproc --all` ;
fi

# default number of iterations: 1
minIterations=$(getElem -minit ${args}) ;
if [[ "${minIterations}" == "" ]] ; then
  minIterations="1" ;
fi

maxIterations=$(getElem -maxit ${args}) ;
if [[ "${maxIterations}" == "" ]] ; then
  maxIterations="1" ;
fi

# get system name
machineName=`uname -n` ;

# get mode
modeName="REG" ;
if [[ "${htFlag}" == "1" ]] ; then
  modeName="HT" ;
fi
if [[ "${pwFlag}" == "1" ]] ; then
  modeName="${modeName}/PW" ;
fi

# default output dir: experiment path
experimentConf="${EXPERIMENT_CONF}" ;
outputDir=$(getElem -o ${args}) ;
# if no experiment path, create a tmp dir
if [[ "${outputDir}" == "" ]] ; then
  outputDirPrefix=${REPO_PATH}/data/${benchmarkName}/${machineName}/${modeName}/${numOfCores}/${inputName} ;
  if [[ "${experimentConf}" != "" ]] ; then
    outputDir=${outputDirPrefix}/${experimentConf} ;
  else
    if ! test -d ${outputDirPrefix} ; then
      mkdir -p ${outputDirPrefix} ;
    fi
    outputDir=`mktemp -d -p ${outputDirPrefix}` ;
  fi
fi

# Find the directory of the benchmark
subdirToUse="apps" ;
if ! test -d ${REPO_PATH}/parsec-3.0/pkgs/${subdirToUse}/${benchmarkName} ; then
  subdirToUse="kernels" ;
fi

# Export arguments
export BENCHMARK_NAME=${benchmarkName} ;
export INPUT_NAME=${inputName} ;
export NUM_OF_CORES=${numOfCores} ;
export MIN_ITERATIONS=${minIterations} ;
export MAX_ITERATIONS=${maxIterations} ;
export HT_FLAG=${htFlag} ;
export PW_FLAG=${pwFlag} ;
export OUTPUT_DISTORTION_FLAG=${outputDistortionFlag} ;
export STATS_FLAG="0" ;
export RUN_MODE="1" ;
export PKG_SUBDIR=${subdirToUse} ;

# Run
python ${REPO_PATH}/scripts/profilerExec.py ${outputDir} ;
