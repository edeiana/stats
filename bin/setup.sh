#!/bin/bash -e

# Deactivate virtualenv, just in case, because I'm lazy
deactivate ;

# Initialize the environment
source ./scripts/init.sh ;

# Check whether or not the PARSEC benchmark suite has been merged
if ! test -f parsec-3.0/.parsec_uniquefile ; then
  echo "ERROR: The PARSEC benchmark suite has not been extracted. Please read the \"README\" file and follow the instructions" ;
  return ;
fi

# Check whether or not the correct LLVM compilation framework is available
llvmConfig=`llvm-config --version` ;
llvmVersion="`cat tools/LLVM`" ;
if test "${llvmConfig}" != "$llvmVersion" ; then
  echo "ERROR: LLVM $llvmVersion is not available" ;
  return ;
fi

# Check the user is using a modern gcc
gccVersionAvailable=`gcc --version | grep ^gcc` ;
gccVersion="`cat tools/GCC`" ;
IFS=" " read -ra gccVersionAsVector <<< "${gccVersionAvailable}" ;
if [[ "${gccVersionAsVector[2]}" != "${gccVersion}" ]] ; then
  echo "ERROR: You need to use GCC ${gccVersion}" ;
  return ;
fi

currDir=`pwd` ;

export PATH=${currDir}/inst/bin:${PATH} ;

# Check if user is already in a virtual env
virtualEnvDir="virtualEnv"
if [[ "${VIRTUAL_ENV}" != "" ]] ; then
  if [[ "${VIRTUAL_ENV}" != "${REPO_PATH}/${virtualEnvDir}" ]] ; then
    echo "ERROR: You are already within this virtual environment: ${VIRTUAL_ENV}. Please deactivate it first." ;
    cd ${currDir} ;
    return ;
  fi
fi

# Clean logs
rm -rf parsec-3.0/log/* ;

# Build libraries
cd parsec-3.0 ;
./to_build_lib.sh ;

# Setup the required directories
cd ${currDir} ;
cd scripts ;
catDir=${REPO_PATH}/inst ;
if ! test -d ${catDir} ; then
  mkdir ${catDir} ;
fi
catDirBin=${REPO_PATH}/inst/bin ;
if ! test -d ${catDirBin} ; then
  mkdir ${catDirBin} ;
fi
catDirLib=${REPO_PATH}/inst/lib ;
if ! test -d ${catDirLib} ; then
  mkdir ${catDirLib} ;
fi
toolsDir=${REPO_PATH}/tools ;
if ! test -d ${toolsDir} ; then
  mkdir ${toolsDir} ;
fi
cd ${currDir} ;

# Clone the threadpool
pushd ./ ;
cd ${toolsDir} ;
if ! test -d threadpool ; then
  git clone ssh://peroni.cs.northwestern.edu/project/parallelizing_compiler/repositories/threadpool ;
  cd ../src/include ;
  ln -s ../../tools/threadpool/include threadpool ;
fi
popd ;

# Clone opentuner
pushd ./ ;
cd ${toolsDir} ;
if ! test -d opentuner ; then
  git clone https://github.com/jansel/opentuner.git
fi

# Compile makeOutputTxt for fluidanimate
cd fluidanimate
make clean;
make install;

popd ;

# Compile compilers
cd ${currDir} ;
pushd ./ ;
cd src ;
make ;
if test $? -ne 0 ; then
  echo "ERROR: src/Makefile failed" ;
  return ;
fi
popd ;

# Setup the python virtual environment for opentuner
if ! test -d ${virtualEnvDir} ; then
  mkdir ${virtualEnvDir} ;
  virtualenv -p python2 ${virtualEnvDir} ;
  source ${virtualEnvDir}/bin/activate ;
  pip install --upgrade pip ;
  pip install opentuner ;
  pip install scipy ;
  pip install psutil ;
  pip install numpy ;
  pip install matplotlib ;
  pip install future ;

else
  source ${virtualEnvDir}/bin/activate ;
fi

# Generate json file that contains architecture topology
hostname=`uname -n` ;
# Check if config dir exists, if not create it
configDir="./config" ;
if ! test -d ${configDir} ; then
  mkdir ${configDir} ;
fi
# Check if topology json file has already been generated
if ! test -f ./config/${hostname}.json ; then
  # Check if hwloc is installed
  which hwloc-gather-topology ;
  if test $? -ne 0 ; then
    echo "ERROR: hwloc-gather-topology not found." ;
    return ;
  fi

  python ./scripts/genConfArch.py ./config ;
fi


cd ${toolsDir} ;
sysDir="${toolsDir}/sys" ;
if ! test -d ${sysDir} ; then
  mkdir ${sysDir} ;
fi

# Setup opencv
opencvRepoDir="opencv";
if ! test -d ${opencvRepoDir} ; then
  git clone https://github.com/Itseez/opencv.git ${opencvRepoDir} ;
fi

pushd ./ ;
if ! test -f ${sysDir}/bin/opencv_version ; then
  cd ${opencvRepoDir} ;
  git checkout 3.2.0 ;
  rm -rf build ;
  mkdir build ;
  cd build ;
  cmake3 -D CMAKE_BUILD_TYPE=Release -D WITH_TBB=OFF -D CMAKE_INSTALL_PREFIX=${sysDir} .. ;
  make -j ;
  make install ;
fi
popd ;

export PKG_CONFIG_PATH=${sysDir}/lib/pkgconfig:${PKG_CONFIG_PATH} ;

# Setup boost 1.65.1
if ! test -f "boost_1_65_1.tar.gz" ; then
  wget https://dl.bintray.com/boostorg/release/1.65.1/source/boost_1_65_1.tar.gz
fi

boostDir="${toolsDir}/boost_1_65_1" ;
if ! test -d ${boostDir} ; then
  tar xf boost_1_65_1.tar.gz ;
fi

export BOOST_ROOT=${toolsDir}/boost_1_65_1 ;

export INCLUDE_PATH=${sysDir}/include:${INCLUDE_PATH} ;
export LD_LIBRARY_PATH=${sysDir}/lib:${LD_LIBRARY_PATH} ;

cd ${currDir} ;
