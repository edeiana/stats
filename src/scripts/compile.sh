#!/bin/bash

# Fetch the arguments
catDir="${REPO_PATH}/inst" ;

# Middle-end
pushd ./ ;
dstFile=${catDir}/bin/middle-end-0
if ! test -e ${dstFile} ; then
  cd ${REPO_PATH}/src/middle-end/ME0 ;
  ./compile.sh ;
fi
popd ;

# Back-end
pushd ./ ;
dstFile=${catDir}/bin/back-end-0
if ! test -e ${dstFile} ; then
  cd ${REPO_PATH}/src/back-end/BE0 ;
  ./compile.sh ;
fi
popd ;
