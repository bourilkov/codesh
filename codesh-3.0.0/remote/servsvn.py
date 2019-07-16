#!/usr/bin/env python3
#***************************************************
#* Copyright (C) 2008, University of Florida       *
#* Authors: D.Bourilkov, S.Sonapeer                *
#* All rights reserved.                            *
#*                                                 *
#* Licensing: GNU General Public License (GPL) v2  *
#***************************************************

# installs a SVN server as demon
# ALWAYS RUN IN A NEW CLEAN DIRECTORY

import cmd, os, string, sys, glob, crypt, socket, shutil

def changeToCodeshRepo():
  global svnrepo

  # prepare directory tree
  os.system('mkdir -p listFiles')
  currDir = os.getcwd()
  os.chdir(currDir+'/listFiles')
  os.system('false | cat >> taglist.txt')
  os.system('false | cat >> snaplist.txt')
  os.chdir(currDir)
  os.system('svn import listFiles file://'+svnrepo+'/listFiles -m "List of Tags and Snapshots"')

  # clean-up
  os.system('rm -rf listFiles')


def setSvnRepoAccess():
  global svnUserName
  global svnrepo

  flag = 0

  svnserveFileHandle = file(svnrepo+'/conf/svnserve.conf','r')
  svnserveTempFileHandle = file(svnrepo+'/conf/tempsvnserve','wt')
  for line in svnserveFileHandle:
    if 'anon-access' in line:
       text = "anon-access = read\n"
       svnserveTempFileHandle.write(text)
       flag = 1

    if 'auth-access = write' in line:
       text = "auth-access = write\n"
       svnserveTempFileHandle.write(text)
       flag = 1
    
    if 'password-db = passwd' in line:
       text = "password-db = passwd\n"
       svnserveTempFileHandle.write(text)
       flag = 1
    
    if flag == 0:
       svnserveTempFileHandle.write(line) 

    flag = 0

  os.system('mv '+svnrepo+'/conf/tempsvnserve '+svnrepo+'/conf/svnserve.conf')
  svnserveFileHandle.close()
  svnserveTempFileHandle.close()

  svnpasswdFileHandle = file(svnrepo+'/conf/passwd','r')
  svnpasswdTempFileHandle = file(svnrepo+'/conf/tempPasswd','wt')
  
  for line in svnpasswdFileHandle:
    if 'harry' in line:
       print("Please Enter the user name and password to access the svn repository")
       print("Remember : This User Name is used later to access the repository normally or through CODESH.")
      
       svnUserName = input("User Name: ")
       svnPassword = input("Password: ")
       svnpasswdTempFileHandle.write(svnUserName+' = '+svnPassword+'\n')

       os.system('mv '+svnrepo+'/conf/tempPasswd '+svnrepo+'/conf/passwd')
       break
    else:
       svnpasswdTempFileHandle.write(line)


def createSvnRepo():
  global svnrepo 

  exists = 0
  while not exists:
    try:
       com = 'mkdir '+svnrepo
       (stdin, stdout, stderr) = os.popen3(com,'t')
       for line in stderr.readlines():
           shortline = line[:-1]  # strip '\n'
           print(shortline)
           raise
    except:
       print("There is already a directory called '"+svnrepo+"' at path given by you.")
       print("Please enter another repository name.")
       s = input("Repository Location=> ")
       if s:
          svnrepo = s
    else:
       exists = 1

  os.system('svnadmin create '+svnrepo)

  
def setSvnServer():
  global svnrepo
  global svnport

  print("\nSVN Server will listen to the repositories under Path:"+svnrepo+"\n")
  os.system('svnserve -d --listen-port '+str(svnport)+' -r '+svnrepo)

def checkSvnPortExists():
  global svnport
  global svnExistingPorts

  while 1:
    print("\nEnter the nonstandard SVN port within the range 3691-3699")
    svnport = eval(input("port: "))
    
    if str(svnport) in svnExistingPorts:
       print("\nAnother SVN server is listening at the port provided by you. Please select different port.")
    else:
        if svnport < 3691 or svnport > 3699:
           print("\nYour input is outside the range provided by us. Please select once again.")
        else:
           break

                                                           
def checkSvnServerExists():
  global svnrepo
  global svnExistingPorts

  print("\nSearching if SVN Server already exists....\n")  
  os.system('ps auxww | fgrep svnserve | cat >> tempFile')
 
  svnServPaths = []
  tempFileHandle = open("tempFile", 'r').readlines()
  
  for line in tempFileHandle:
    shortline = line[:-1]
    if ' svnserve -d' in shortline:
        j = 0
        wordlist = shortline.split()

        while 1:
           if '--listen-port'in wordlist[j]:
              break
           else:
              j = j + 1

        svnExistingPorts.append(wordlist[j+1])      # Next thing in wordlist after '--listen-port' has to be port number
        svnServPaths.append(wordlist[j+3])
        print("SVN server already exists on this machine. Specifications are as follows:")
        print(shortline)
    
  print(svnServPaths)
  for servPath in svnServPaths:
     if servPath in svnrepo:
        print("Your repository can't be under the existing server's repository.")
        print("Please give new repository path which is above the existing server's path.")
        os.system('rm -rf tempFile')
        return 0

  os.system('rm -rf tempFile')
  return 1


svnExistingPorts = []
svnport = "3600"
svnUserName = ""
validRepoPath = 0

print("\nWe suggest users to execute this script in an empty directory.")
print("\nAre you sure you are in the right place?\n")
reply = input("Press 'y' to continue or 'n' to exit, cd to an empty directory and execute the script there? (y/n): ")

if reply == 'y':

  while not validRepoPath:
     print("\nEnter the SVN Repository Location for the svn server.\n")
     svnrepo = input("Repository Location: ")
     validRepoPath = checkSvnServerExists()
     svnServPaths = []

  print("A new SVN server can be created to listen at the repository path given by you.")
  checkSvnPortExists()

  setSvnServer()
  createSvnRepo()
  setSvnRepoAccess()

  print("\nA Standard SVN repository is created under the path:"+svnrepo)
  reply = input("Do you now want to convert this SVN repository to CODESH SVN repository?(y/n): ")

  if reply == "y": # Converting the SVN repository to CODESH SVN repository
     changeToCodeshRepo()
     words = svnrepo.split('/')
     print("\nNew SVN repository is now converted to CODESH repository.")
     print("This CODESH SVN repository can be accessed remotely through CODESH using repository path as below:")
     print("svn://"+svnUserName+"@"+socket.gethostname()+":"+str(svnport)+"/"+"\n")
  else:
     print("\nYou can now find Standard SVN repository under path:"+svnrepo+" & it is accesible remotely through port:"+str(svnport))

