#!/bin/sh
#  Initialize PYTHONPATH for CODESH in sh/bash
#   To use CODESH just source this script in the
#   directory where you checked out the CODESH code,
#   then change to your working directory

if [ "x$PATH" == x ]
then
 export PATH=`pwd`
else
 export PATH=`pwd`:${PATH}
fi

if [ "x$PYTHONPATH" == x ]
then
 export PYTHONPATH=`pwd`
else
 export PYTHONPATH=`pwd`:${PYTHONPATH}
fi
