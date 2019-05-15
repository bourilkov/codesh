#!/bin/bash
#
#   Create a local CODESH Ascii repository in location $1
#
#   Usage: $1 should be an absolute pathname or a pathname
#          relative to the current directory and the user
#          should have write privileges for this directory
#

if [ $# -lt 1 ]
then
   echo "Usage:  "`basename $0`" <repository_location>"
   exit 1
fi

repository=$1
echo "Creating local CODESH ASCII repository in: " $repository
mkdir -p ${repository}
mkdir -p ${repository}/snapshots
mkdir -p ${repository}/asciiRepoValid

if [ ! -e ${repository} ]
then
   echo Creating local CODESH ASCII repository FAILED.
   echo Usage: $1 should be an absolute pathname or a pathname
   echo relative to the current directory and the user
   echo should have write privileges for this directory
   exit 1
fi
