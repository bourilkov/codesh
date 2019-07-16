#!/usr/bin/env python3
#***************************************************
#* Copyright (C) 2008, University of Florida       *
#* Authors: D.Bourilkov, S.Sonapeer                *
#* All rights reserved.                            *
#*                                                 *
#* Licensing: GNU General Public License (GPL) v2  *
#***************************************************

# installs a CVS pserver
# first make a backup of:
#
#  /etc/services    file
#  /etc/xinetd.d    directory
#
# ALWAYS RUN IN A NEW CLEAN DIRECTORY

import cmd, os, string, sys, glob, crypt, socket, shutil

def getUniqueID():
    cmdline = "date --iso-8601='minutes' -u"
    for line in os.popen(cmdline).readlines():
        shortline = line[:-1]  # strip '\n'
        id = shortline[0:4]+shortline[5:7]+shortline[8:10]+'-'+shortline[11:13]+shortline[14:16]
    return id

def changeToCodeshRepo():
  global cvsUserName
  global cvsrepo

  cvsFile ='modulesadd'
  currDir = os.getcwd()
  cvsfile = open(currDir+'/'+cvsFile,'w')

  texttowrite = "#  CVS modules file\n\nCVSROOT\tCVSROOT\nmodules\tCVSROOT modules\nloginfo\tCVSROOT loginfo\ncommitinfo\tCVSROOT commitinfo\nrcsinfo\tCVSROOT rcsinfo\neditinfo\tCVSROOT editinfo\n\n#  add CODESH modules here\n\ntdata\ttdata\ntlogs\ttlogs\ntsource\ttsource\n"

  cvsfile.write(texttowrite)
  cvsfile.close()

  os.system('cvs -d :pserver:'+cvsUserName+'@localhost:'+cvsrepo+' login')

  os.system('cvs -d '+cvsrepo+' co CVSROOT/modules')
  os.chdir(currDir+'/CVSROOT')
  os.system('false | cat >> modulesold')
  os.system('mv modules modulesold')
  os.system('cat modulesold ../modulesadd > modules')
  os.system('cvs -d '+cvsrepo+' ci -m "Updated with codesh modules" modules')
  os.system('rm -f modulesold')
  os.chdir(currDir)

  # clean up
  os.system('cvs -Q -d '+cvsrepo+' release -d CVSROOT')
  os.system('rm -f modulesadd')

  # prepare directory tree
  os.system('false | cat >> dummy.file')
  os.system('false | cat >> mylog.1')
  os.system('false | cat >> myfulllog.1')
  os.system('false | cat >> snaplist.txt')
  os.system('mkdir tdata')
  os.system('mkdir tlogs')
  os.system('mkdir tsource')
  os.system('mkdir snapshots')

  os.system('cp dummy.file tdata')
  os.system('cp mylog.1 tlogs')
  os.system('cp myfulllog.1 tlogs')
  os.system('cp dummy.file tlogs')
  os.system('cp dummy.file tsource')
  os.system('cp snaplist.txt snapshots')
  os.system('rm -f dummy.file')
  os.system('rm -f mylog.1')
  os.system('rm -f myfulllog.1')
  os.system('rm -f snaplist.txt')

  # create modules in CODESH repository

  os.chdir(currDir+'/tdata')
  os.system('cvs -d '+cvsrepo+' import -m "Local CODESH repository" tdata codesh local')
  #Os.system('cvs -d :pserver:'+cvsUserName+'@localhost:'+cvsrepo+' import -m "Local CODESH repository" tdata codesh local')
  os.chdir(currDir+'/tlogs')
  os.system('cvs -d '+cvsrepo+' import -m "Local CODESH repository" tlogs codesh local')
  os.chdir(currDir+'/tsource')
  os.system('cvs -d '+cvsrepo+' import -m "Local CODESH repository" tsource codesh local')
  os.chdir(currDir+'/snapshots')
  os.system('cvs -d '+cvsrepo+' import -m "snapshot list file" snapshots snaplist list1')
  os.chdir(currDir)

  os.system('cvs -d :pserver:'+cvsUserName+'@localhost:'+cvsrepo+' logout')

  # clean - up
  os.system('rm -rf tdata')
  os.system('rm -rf tlogs')
  os.system('rm -rf tsource')
  os.system('rm -rf snapshots')

  # Changing the Permissions
  os.system('chown -R '+cvsuser+' '+cvsrepo+'/tdata')
  os.system('chgrp -R '+cvsgrp+' '+cvsrepo+'/tdata')
  os.system('chmod 750 -R '+cvsrepo+'/tdata')

  os.system('chown -R '+cvsuser+' '+cvsrepo+'/tlogs')
  os.system('chgrp -R '+cvsgrp+' '+cvsrepo+'/tlogs')
  os.system('chmod 750 -R '+cvsrepo+'/tlogs')

  os.system('chown -R '+cvsuser+' '+cvsrepo+'/tsource')
  os.system('chgrp -R '+cvsgrp+' '+cvsrepo+'/tsource')
  os.system('chmod 750 -R '+cvsrepo+'/tsource')

  os.system('chown -R '+cvsuser+' '+cvsrepo+'/snapshots')
  os.system('chgrp -R '+cvsgrp+' '+cvsrepo+'/snapshots')
  os.system('chmod 750 -R '+cvsrepo+'/snapshots')


def changePermissions():
  global cvsUserName
  global cvsrepo
 
  passwdfile = open(cvsrepo+'/CVSROOT/passwd','w')
  print("\nPlease enter the (remote, not UNIX) CVS user name and password to access the cvs repository.\n")
  print("  Remember: This User Name is used later to access the repository normally or through CODESH.\n")
  cvsUserName = input("User Name: ")
  cvsPassword = input("Password: ")
  cvsSalt     = 's2'
  cvsSalt     = input("Salt (2 symbols): ")
  cvsPassword = crypt.crypt(cvsPassword,cvsSalt[0:2])
  passwdfile.write(cvsUserName+':'+cvsPassword+':'+cvsuser)
  passwdfile.close()

  writerfile = open(cvsrepo+'/CVSROOT/writers','w')
  writerfile.write(cvsUserName)
  writerfile.close()

  os.system('chown -R '+cvsuser+' '+cvsrepo+'/CVSROOT')
  os.system('chgrp -R '+cvsgrp+' '+cvsrepo+'/CVSROOT')
  os.system('chmod 750 '+cvsrepo+'/CVSROOT')

  os.system('chown '+cvsuser+' '+cvsrepo)
  os.system('chgrp '+cvsgrp+' '+cvsrepo)
  os.system('chmod 750 '+cvsrepo)
 
  currentDir = os.getcwd()  
  os.chdir(cvsrepo)
  os.chdir('..')
  changedDir = os.getcwd()

  os.system('chgrp '+cvsgrp+' '+changedDir)
  os.system('chmod 755 '+changedDir)
  os.chdir(currentDir)

  os.system('chmod 444 '+cvsrepo+'/CVSROOT/*checkoutlist*')
  os.system('chmod 444 '+cvsrepo+'/CVSROOT/*commitinfo*')
  os.system('chmod 444 '+cvsrepo+'/CVSROOT/*edit*')
  os.system('chmod 444 '+cvsrepo+'/CVSROOT/*cvswrappers*')
  os.system('chmod 444 '+cvsrepo+'/CVSROOT/*loginfo*')
  os.system('chmod 444 '+cvsrepo+'/CVSROOT/*modules*')
  os.system('chmod 444 '+cvsrepo+'/CVSROOT/*notify*')
  os.system('chmod 444 '+cvsrepo+'/CVSROOT/*rcsinfo*')
  os.system('chmod 444 '+cvsrepo+'/CVSROOT/*taginfo*')
  os.system('chmod 444 '+cvsrepo+'/CVSROOT/*verifymsg*')

  os.system('chmod 666 '+cvsrepo+'/CVSROOT/val-tags') 
  os.system('chmod 666 '+cvsrepo+'/CVSROOT/history')

  os.system('chmod 700 '+cvsrepo+'/CVSROOT/passwd')
  os.system('chmod u+s '+cvsrepo+'/CVSROOT/passwd')
  os.system('chmod 700 '+cvsrepo+'/CVSROOT/writers')
  os.system('chmod u+s '+cvsrepo+'/CVSROOT/writers')

  os.system('chmod 775 '+cvsrepo+'/CVSROOT/Emptydir')


def createCvsRepo():
  global cvsrepo

  exists = 0
  while not exists:
    try:
       com = 'mkdir '+cvsrepo
       (stdin, stdout, stderr) = os.popen3(com,'t')
       for line in stderr.readlines():
           shortline = line[:-1]  # strip '\n'
           print(shortline) 
           raise
    except:
       print("There is already a directory called '"+cvsrepo+"' at path given by you.")
       print("Please enter another repository name.")
       s = input("Repository Location=> ")
       if s:
          cvsrepo = s
    else:
       exists = 1

  os.system('cvs -d '+cvsrepo+' init')


def manageCvsRepository():
  global cvsUserName 
  global cvsrepo
  global cvsport

  createCvsRepo()
  changePermissions()
  
  print("\nA Standard CVS repository is created under the path:"+cvsrepo)
  reply = input("Do you now want to convert this CVS repository to CODESH CVS repository?(y/n): ")
  
  if reply == "y": # Converting the CVS repository to CODESH CVS repository
     changeToCodeshRepo()
     print("\nNew CVS repository is now converted to CODESH repository.")
     print("This CODESH CVS repository can be accessed remotely through CODESH using repository path as below:")
     print(":pserver:"+cvsUserName+"@"+socket.gethostname()+":"+cvsport+cvsrepo+"\n")
  else:
     print("\nYou can now find Standard CVS repository under path:"+cvsrepo+" & it is accesible remotely through port:"+cvsport)

def createCvsXinetdFile():
  global cvsrepo
  global cvsport

  cvsFile ='cvs'  
  cvsfile = open('/etc/xinetd.d/'+cvsFile,'w')

  texttowrite = "service\tcvspserver\n\t{\n\t\tdisable\t\t=no\n\t\tsocket_type\t=stream\n\t\twait\t\t=no\n\t\tuser\t\t="+cvsuser+"\n\t\tgroup\t\t="+cvsuser+"\n\t\tlog_type\t= FILE /var/log/cvspserver\n\t\tprotocol\t= tcp\n\t\tenv\t\t='$HOME=/analysistrove/cvs'\n\t\tlog_on_failure\t+= USERID\n\t\tport\t\t="+cvsport+"\n\t\tserver\t\t=/usr/bin/cvs\n\t\tserver_args\t= -f --allow-root="+cvsrepo+" pserver\n\t}"

  cvsfile.write(texttowrite)
  cvsfile.close()

  os.system('chown '+cvsuser+' /etc/xinetd.d/'+cvsFile)
  os.system('chgrp '+cvsgrp+' /etc/xinetd.d/'+cvsFile)
  os.system('chmod 744 /etc/xinetd.d/'+cvsFile)

  os.system('/etc/init.d/xinetd restart')
  os.system('/etc/init.d/xinetd status')


def checkCvsPserverExists():
  global cvsrepo
  global flgcvsuser
  global flgpserver
  
  for fileName in os.listdir('/etc/xinetd.d'):
      dataFile = open("/etc/xinetd.d/"+fileName, 'r').readlines()
      for line in dataFile:
        shortline = line[:-1]
    
        if cvsuser in shortline: # cvsuser always come before pserver in cvspserver file!
          flgcvsuser = 1
  
        if ' pserver' in shortline:
          flgpserver = 1
          if flgcvsuser == 1:
            cvsFile = fileName
            print("CVS pserver already exists for the given user.")
            reply = input("Do you want to add CVS repository in the given path?(y/n): ")
  
            if reply == "y": # adding additional path to abother repository in existing cvspserver for given cvsuser
  
                cvsFileHandle = open('/etc/xinetd.d/'+cvsFile, 'r').readlines()
                cvsTempFileHandle = file('/etc/xinetd.d/cvsTempFile','wt')
                for line in cvsFileHandle:
                  if ' pserver' in line:
                    shortline = line[:-9]
                    shortline = shortline + ' --allow-root='+cvsrepo+' pserver\n'
                    cvsTempFileHandle.write(shortline)   
                  else:
                    cvsTempFileHandle.write(line)
             
                cvsTempFileHandle.close()
                os.system('mv /etc/xinetd.d/cvsTempFile /etc/xinetd.d/'+cvsFile)
                os.system('rm -rf /etc/xinetd.d/cvsTempFile')
  
                os.system('chown '+cvsuser+' /etc/xinetd.d/'+cvsFile)
                os.system('chgrp '+cvsgrp+' /etc/xinetd.d/'+cvsFile)
                os.system('chmod 744 /etc/xinetd.d/'+cvsFile)
                
                os.system('/etc/init.d/xinetd restart')
                os.system('/etc/init.d/xinetd status')
                
                manageCvsRepository()

            else:
                print("You have chosen NOT to add additional repository to an existing pserver")
                break

          if flgpserver == 1 and flgcvsuser == 0:
             print("pserver already exists on this machine")
             break
  
      if flgpserver == 1:
        break;
  

def checkCvsPortExists():
  global cvsport

  flgportexist = 0
  flgportinserted  = 0

  serviceFile = open("/etc/services", 'r').readlines()
  
  for line in serviceFile:
      if  'cvspserver' in line:
        wordlist = line.split()
        portlist = wordlist[1].split('/')
        cvsport = portlist[0]  
        flgportexist = 1

  if flgportexist == 0:
    while cvsport < 2402 or cvsport > 2409:
      print("Enter the nonstandard CVS port within the range 2402-2409 ")
      cvsport = eval(input("port: "))
      print("Your input is outside the range provided by us. Please select once again.")
   
    serviceTempFileHandle = file('/etc/serviceTempFile','wt')
    for line in serviceFile:
      if '/tcp' in line or '/udp' in line:
          if flgportinserted == 0:
              wordlist = line.split()
              portlist = wordlist[1].split('/')
              port = portlist[0]
              port = int(port,10)
              if port > cvsport:
                  text = "cvspserver\t"+str(cvsport)+"/tcp\t\t\t# CVS client/server operations\n"
                  serviceTempFileHandle.write(text)
                  text = "cvspserver\t"+str(cvsport)+"/udp\t\t\t# CVS client/server operations\n"
                  serviceTempFileHandle.write(text)
                  flgportinserted = 1

          serviceTempFileHandle.write(line)
      else:
            serviceTempFileHandle.write(line)
       
    cvsport = str(cvsport)
    os.system('cp -f /etc/services /etc/services.original.'+getUniqueID())
    os.system('mv /etc/serviceTempFile /etc/services')
    os.system('rm -rf /etc/serviceTempFile')


cvsUserName = ""  # remote CVS user name (not UNIX account on the server)
flgcvsuser = 0
flgpserver = 0
cvsport = "2401"

print("\nWe suggest users to execute this script in an empty directory.")
print("\nAre you sure you are in the right place?\n")
reply = input("Press 'y' to continue or 'n' to exit, cd to an empty directory and execute the script there? (y/n): ")

if reply == 'y':
  print("\nIt is time to define the UNIX account which will be used by the pserver to run.\n")
  print("\nEnter the CVS User, Group for the UNIX account and CVS Repository Location for the cvs pserver:\n")
  # here we define the UNIX account for the server
  cvsuser = input("User: ")
  cvsgrp  = input("Group: ")
  cvsrepo = input("Repository Location: ")

  checkCvsPortExists()
  checkCvsPserverExists()

  if flgcvsuser == 0 and flgpserver == 0:      # pserver does not exist on the machine
    createCvsXinetdFile()
    manageCvsRepository()

