#!/bin/bash -e

# Set the CLANG compilers to use if unset
if test -z "$CC" ; then
  export CC=clang
  export CXX=clang++
fi

rm -rf build/ ; 
mkdir build ; 
cd build ; 
mkdir -p ${REPO_PATH}/inst ;
cmake3 -DCMAKE_INSTALL_PREFIX="${REPO_PATH}/inst" -DCMAKE_BUILD_TYPE=Debug ../ ; 
make ;
make install ;
cd ../ 
