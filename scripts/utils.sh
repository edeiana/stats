#!/bin/bash

function contains {
  local result ;
  result=0 ;
  local string ;
  string=$1 ;
  for elem in ${@:2} ; do
    if [[ "${elem}" == "${string}" ]] ; then
      result=1 ;
      break ;
    fi
  done

  echo "${result}" ;
}


## Check if a flag is set or not in a list of arguments
#  (flag, arguments) -> 0 or 1
#
function isFlagSet {
  local flag ;
  flag=$1 ;

  local arguments ;
  arguments=${@:2} ;

  local isSet ;
  isSet=0 ;
  for elem in ${arguments} ; do
    if [[ "${elem}" == "${flag}" ]] ; then
      isSet=1 ;
      break ;
    fi
  done

  echo "${isSet}" ;
}

## Get the element right after a given named argument in a list of arguments
#  (named argument, arguments) -> element or ""
#
function getElem {
  local flag ;
  flag=$1 ;

  local arguments ;
  arguments=${@:2} ;

  local argumentsList ;
  IFS=' ' read -r -a argumentsList <<< "${arguments}" ;

  local result ;
  result="" ;

  local counter ;
  counter=0 ;
  for elem in "${argumentsList[@]}" ; do
    counter=$((counter+1)) ;
    if [[ "${elem}" == "${flag}" ]] ; then
      result="${argumentsList[${counter}]}" ;
      break ;
    fi
  done

  echo "${result}" ;
}
