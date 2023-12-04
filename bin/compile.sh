#!/bin/bash

# Check the inputs
numOfInputs=$((2*2)) ;
if test $# -lt ${numOfInputs} ; then
  echo "USAGE: `basename $0` -p BENCHMARK -i INPUT [-nc NUM_OF_CORES, -minit MIN_ITERATIONS, -maxit MAX_ITERATIONS, -conf CONF_STRING, -tunertime TIME_IN_SECS, -pw, -ht, -outputdistortion]" ;
  exit 1 ;
fi

# include common functions
source ${REPO_PATH}/scripts/utils.sh ;

# get arguments
args=$@ ;

benchmarkName=$(getElem -p ${args}) ;
inputName=$(getElem -i ${args}) ;
configurationToUse=$(getElem -conf ${args}) ;
seedConf=$(getElem -seedconf ${args}) ;

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

# optional args
tunerTime=$(getElem -tunertime ${args}) ;
if [[ "${tunerTime}" == "" ]] ; then
  tunerTime="3600" ; # 1h, in seconds
fi
 
htFlag=$(isFlagSet -ht ${args}) ;
pwFlag=$(isFlagSet -pw ${args}) ;
outputDistortionFlag=$(isFlagSet -outputdistortion ${args}) ;

# negate statsFlag
statsFlag="0" ;
if [[ "${configurationToUse}" == "" ]] ; then
  statsFlag="1" ;
fi

# export arguments
export BENCHMARK_NAME=${benchmarkName} ;
export INPUT_NAME=${inputName} ;
export NUM_OF_CORES=${numOfCores} ;
export MIN_ITERATIONS=${minIterations} ;
export MAX_ITERATIONS=${maxIterations} ;
export CONFIGURATION_TO_USE=${configurationToUse} ;
export TUNER_TIME=${tunerTime} ;
export HT_FLAG=${htFlag} ;
export PW_FLAG=${pwFlag} ;
export OUTPUT_DISTORTION_FLAG=${outputDistortionFlag} ;
export STATS_FLAG=${statsFlag} ;
export SEED_CONF=${seedConf} ;

# Compile
cd parsec-3.0 ;
./to_build_app.sh ${benchmarkName} ;
cd ../ ;

# Set experiment path environment variable
machineName=`uname -n` ;

modeName="REG" ;
if [[ "${htFlag}" == "1" ]] ; then
  modeName="HT" ;
fi
if [[ "${pwFlag}" == "1" ]] ; then
  modeName="${modeName}/PW" ;
fi

export EXPERIMENT_CONF="" ;
if [[ "${statsFlag}" == "0" ]] ; then
  export EXPERIMENT_CONF=${configurationToUse} ;
fi
