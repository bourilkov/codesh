#!/bin/bash
#
#   Create a local CODESH SVN repository in location $1
#   $1 should be specified as ABSOLUTE path
#   You need write permission for $1
#
#   Author  D.Bourilkov 26-Nov-2007
#
#   Usage: go to a clean working directory where
#   you have write permissions and run this script;
#   the working directory should be different from $1
#

if [ $# -lt 1 ]
then
   echo "Usage:  "`basename $0`" <repository_location> as ABSOLUTE path"
   exit 1
fi

repository=$1

#   create SVN repository

echo "Creating local CODESH SVN repository in: " $repository
svnadmin create ${repository}


#   prepare directory tree

mkdir -p listFiles
cd listFiles

cat > taglist.txt << EOD
EOD

cat > snaplist.txt << EOD
EOD

cd ..

svn import listFiles file://${repository}/listFiles -m "List of Tags and Snapshots"

#   clean-up
rm -rf listFiles

