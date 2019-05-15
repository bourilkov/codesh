#!/usr/bin/env python2

import cmd, os, string, sys, shutil

svnflag = ' '
if len(sys.argv) > 1:
       svnflag = sys.argv[1]

remoteflag = ' '
if len(sys.argv) > 2:
       remoteflag = sys.argv[2]

if remoteflag != 'remote':
  os.system('mkdir -p sandbox')
  originalDir = os.getcwd()
  os.chdir('sandbox')
  newDir = os.getcwd()
  newDirAscii = newDir+'/repoAscii'
  newDirCvs = newDir+'/repoCvs'
  if svnflag == 'svn':
       newDirSvn = newDir+'/repoSvn'
       newURLSvn = 'file://' + newDirSvn
  os.chdir(originalDir)

  if svnflag != 'svn':
       os.system('create-codeshcvsrepository.sh '+ newDirCvs)
       os.system('create-codeshasciirepository.sh '+ newDirAscii)
  if svnflag == 'svn':
       os.system('create-codeshsvnrepository.sh '+ newDirSvn)

if remoteflag == 'remote':
  remotefile = open('remoterepo.file', "r")
  counter = 1
  for line in remotefile.readlines():
       shortline = line[:-1]  # strip '\n'
       print "Line ",counter," : ",shortline
       if counter == 1: newDirAscii = shortline
       if counter == 2: newDirCvs   = shortline
       if counter == 3:
                        newURLSvn   = shortline
                        remotefile.close()
                        break
       counter = counter + 1

# config files for bash

count = 0
confFile = open('codesh.bash.conf','r')
newConfileAscii = open('codesh.bash.ascii.conf','w')
newConfileCvs = open('codesh.bash.cvs.conf','w')
newConfileAsciiRepochk = open('codesh.bash.asciiRepochk.conf','w')
newConfileCvsRepochk = open('codesh.bash.cvsRepochk.conf','w')
if svnflag == 'svn':
       newConfileSvn = open('codesh.bash.svn.conf','w')
       newConfileSvnRepochk = open('codesh.bash.svnRepochk.conf','w')

for line in confFile.readlines():
       count = count + 1

       if count == 1:
		newConfileAscii.write('# Repository '+newDirAscii+'\n')
		newConfileAscii.write('# Repositorytype ascii\n')
		newConfileCvs.write('# Repository '+newDirCvs+'\n')
		newConfileCvs.write('# Repositorytype cvs\n')
                if svnflag == 'svn':
                     newConfileSvn.write('# Repository '+newURLSvn+'\n')
                     newConfileSvn.write('# Repositorytype svn\n')
		newConfileAsciiRepochk.write('# Repository \n')
		newConfileAsciiRepochk.write('# Repositorytype ascii\n')
		newConfileCvsRepochk.write('# Repository \n')
		newConfileCvsRepochk.write('# Repositorytype cvs\n')
                if svnflag == 'svn':
                     newConfileSvnRepochk.write('# Repository \n')
                     newConfileSvnRepochk.write('# Repositorytype svn\n')
       
       newConfileAscii.write(line)
       newConfileCvs.write(line)
       newConfileAsciiRepochk.write(line)
       newConfileCvsRepochk.write(line)
       if svnflag == 'svn':
              newConfileSvn.write(line)
              newConfileSvnRepochk.write(line)

newConfileAscii.close()
newConfileCvs.close()
newConfileAsciiRepochk.close()
newConfileCvsRepochk.close()
if svnflag == 'svn':
       newConfileSvn.close()
       newConfileSvnRepochk.close()

# config files for tcsh

count = 0
confFile = open('codesh.tcsh.conf','r')
newConfileAscii = open('codesh.tcsh.ascii.conf','w')
newConfileCvs = open('codesh.tcsh.cvs.conf','w')
if svnflag == 'svn':
       newConfileSvn = open('codesh.tcsh.svn.conf','w')

for line in confFile.readlines():
       count = count + 1

       if count == 1:
		newConfileAscii.write('# Repository '+newDirAscii+'\n')
		newConfileAscii.write('# Repositorytype ascii\n')
		newConfileCvs.write('# Repository '+newDirCvs+'\n')
		newConfileCvs.write('# Repositorytype cvs\n')
                if svnflag == 'svn':
                     newConfileSvn.write('# Repository '+newURLSvn+'\n')
                     newConfileSvn.write('# Repositorytype svn\n')
       
       newConfileAscii.write(line)
       newConfileCvs.write(line)
       if svnflag == 'svn':
              newConfileSvn.write(line)

newConfileAscii.close()
newConfileCvs.close()
if svnflag == 'svn':
       newConfileSvn.close()
