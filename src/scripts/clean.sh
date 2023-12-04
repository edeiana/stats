#!/bin/bash

cd ${REPO_PATH}/src ;

find ./ -iname *.o -delete ;
find ./ -iname *.pyc -delete ;
find ./ -iname *.log -delete ;
find ./ -name compile_commands.json -delete ;
