#!/bin/bash -e

conf="`cat ${REPO_PATH}/src/project.txt`" ;

pkg=""

# tools
pkg="$pkg yasm            "  
pkg="$pkg libtool         "  

# libs
pkg="$pkg glib            "  
pkg="$pkg gsl             "  
pkg="$pkg hooks           "  
pkg="$pkg libjpeg         "  
pkg="$pkg libxml2         "  
pkg="$pkg mesa            "  
pkg="$pkg parmacs         "  
pkg="$pkg ssl             "  
pkg="$pkg tbblib          "  
pkg="$pkg uptcpip         "  
pkg="$pkg zlib            "  

# uninstall 
cmd="./bin/parsecmgmt -a uninstall -c gcc -p cmake"
echo $cmd
#$cmd

cmd="./bin/parsecmgmt -a uninstall -c $conf -p $pkg"
echo $cmd
#$cmd

############################################################################
export PARSEC_CONF_COMPILER_TO_USE=gcc
cmd="./bin/parsecmgmt -a build -c $conf -p cmake"
echo $cmd
$cmd
unset PARSEC_CONF_COMPILER_TO_USE



############################################################################
export PARSEC_CONF_PKG_TO_BUILD=$pkg
export PARSEC_CONF_COMPILER_TO_USE=clang
cmd="./bin/parsecmgmt -a build -c $conf -p $pkg"
echo $cmd
$cmd
