#!/bin/bash
#
#   Create a local CODESH CVS repository in location $1
#   You need write permission for $1
#
#   Author  D.Bourilkov 04-Oct-2006
#
#   Usage: go to a clean working directory where
#   you have write permissions and run this script;
#   the working directory should be different from $1
#

if [ $# -lt 1 ]
then
   echo "Usage:  "`basename $0`" <repository_location>"
   exit 1
fi

repository=$1
echo "Creating local CODESH CVS repository in: " $repository

#   prepare modules addition
cat > modulesadd << EOD
#
#  CVS modules file
#
CVSROOT        CVSROOT
modules        CVSROOT modules
loginfo        CVSROOT loginfo
commitinfo     CVSROOT commitinfo
rcsinfo        CVSROOT rcsinfo
editinfo       CVSROOT editinfo
#
#  add CODESH modules here
#
tdata          tdata
tlogs          tlogs
tsource        tsource
EOD

#   create an empty CODESH repository
cvs -d $repository init
#   update the modules file in CVSROOT
cvs -d $repository co CVSROOT/modules
cd CVSROOT
mv modules modulesold
cat modulesold ../modulesadd > modules
cvs -d $repository ci -m "Updated with codesh modules" modules
rm -f modulesold
cd ..

#   clean-up
cvs -Q -d $repository release -d CVSROOT
rm -f modulesadd

#   prepare directory tree

cat > dummy.file << EOD
dummy
EOD

cat > snaplist.txt << EOD
EOD

mkdir tdata
mkdir tlogs
mkdir tsource
mkdir snapshots
cp dummy.file tdata
cp dummy.file tlogs
cp dummy.file tsource
cp snaplist.txt snapshots
rm -f dummy.file
rm -f snaplist.txt

#   create modules in CODESH repository
cd tdata
cvs -d $repository import -m "Local CODESH repository" tdata codesh local
cd ../tlogs
cvs -d $repository import -m "Local CODESH repository" tlogs codesh local
cd ../tsource
cvs -d $repository import -m "Local CODESH repository" tsource codesh local
cd ../snapshots
cvs -d $repository import -m "snapshot list file" snapshots snaplist "list1"
cd ..

#   clean-up
rm -rf tdata
rm -rf tlogs
rm -rf tsource
rm -rf snapshots
