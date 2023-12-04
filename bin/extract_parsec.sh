#!/bin/bash

function print_usage_and_exit {
  echo "USAGE: $scriptName PARSEC_ARCHIVE_FILE" ;
  exit 1
}

# Check inputs
scriptName=`basename $0` ;
if test $# -lt 1 ; then
  print_usage_and_exit ;
fi

if ! test -f $1 ; then
  print_usage_and_exit ;
fi

# Uncompress the archive
tar --skip-old-files -x -f $1
