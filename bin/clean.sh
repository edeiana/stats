#!/bin/bash

function cleanMakefile {
  echo "  Cleaning makefiles under \"$1\"" ;
  pushd ./ ;
  cd $1 ;
  for i in `find ./ -name Makefile` ; do

    # Check the makefile still exists
    if ! test -f $i ; then
      continue ;
    fi
    echo "    Cleaning $i" ;

    # Clean
    pushd ./ ;
    dirOfI="`dirname $i`" ;
    cd "$dirOfI" ;
    make clean ;
    popd ;
  done
  popd ;
}

# Initialize the environment
source ./scripts/init.sh ;

hostname=`uname -n` ;
if test -f ./config/${hostname}.json ; then
  rm ./config/${hostname}.json ;
fi
if test -d ./config ; then
  find ./config -empty -delete
fi

if test -d ${virtualEnvDir} ; then
  deactivate ;
  rm -rf virtualEnv ;
fi

buildDirs=`find ./src -name build` ;
if test "$buildDirs" != "" ; then
  rm -rf $buildDirs ;
fi

otDirs=`find ./ -name opentuner.db` ;
if test "$otDirs" != "" ; then
  rm -rf $otDirs ;
fi

rm -rf tools/opentuner inst `find ./ -iname *.pyc`;

rm -rf tools/papi ;

# Remove opencv and boost
rm -rf tools/sys tools/opencv tools/boost_1_65_1 tools/boost_1_65_1.tar.gz ;

rm -rf parsec-3.0/log/* 

rm -f tmp*

rm -f `find ./ -iname *.pyc` ;

for i in `find ./ -name src` ; do

  # Check if src_top exists
  pushd ./ ;
  cd $i ;
  cd ../ ;
  if ! test -d src_top ; then
    popd ;
    continue ;
  fi

  # Delete src
  rm -rf src ;

  popd ;
done

rm -f scripts/autotunerDesignSpace/*.log

pushd ./ ;
cd parsec-3.0 ;
./bin/parsecmgmt -a clean ;
./bin/parsecmgmt -a fullclean ;
./bin/parsecmgmt -a uninstall ;
./bin/parsecmgmt -a fulluninstall ;
popd ;

# Clean the threadpool
rm -f src/include/threadpool ;
rm -rf tools/threadpool ;
echo "" ;

# Clean directories with makefiles
echo "Cleaning directories with makefiles"
cleanMakefile "src"
cleanMakefile "tools"
