#!/bin/bash

conf="`cat ${REPO_PATH}/src/project.txt`" ;

pkg=$1

# uninstall 
cmd="./bin/parsecmgmt -a uninstall -c $conf -p $pkg"
echo $cmd
$cmd
cmd="./bin/parsecmgmt -a clean -c $conf -p $pkg"
echo $cmd
$cmd

# Find the directory of the benchmark
subdirToUse="apps" ;
if ! test -d pkgs/${subdirToUse}/${pkg} ; then
  subdirToUse="kernels" ;
fi
export PKG_SUBDIR=${subdirToUse} ;

# Set the important directories
rootDir=`pwd` ;
srcSrc="${rootDir}/pkgs/${subdirToUse}/${pkg}/src_top" ;
dstSrc="${rootDir}/pkgs/${subdirToUse}/${pkg}/src" ;

# Check if we need to invoke the front-end compiler
if test -d ${srcSrc} ; then

  # Invoke the front end compiler
  echo "----- FRONT-END COMPILER -----" ;
  rm -rf ${dstSrc} ;
  ../src/scripts/frontEnd ${srcSrc} ${dstSrc} ;
fi
if ! test -d ${dstSrc} ; then
  echo "ERROR while generating ${dstSrc}" ;
  echo "  TOP src: ${srcSrc}" ;
  exit 1 ;
fi

# build
export PARSEC_CONF_PKG_TO_BUILD=$pkg
cmd="./bin/parsecmgmt -a build -c $conf -p $pkg"
echo $cmd
$cmd
