#!/usr/bin/env python2
#***************************************************
#* Copyright (C) 2007, University of Florida       *
#* Authors: D.Bourilkov, S.Sonapeer                *
#* All rights reserved.                            *
#*                                                 *
#* Licensing: GNU General Public License (GPL) v2  *
#***************************************************
#******************************************
#*                                        *
#*             C O D E S H                *
#*                                        *
#*    COllaborative DEvelopment SHell     *
#*                                        *
#*     Conception: Dimitri Bourilkov      *
#*                                        *
#*         Lead developers:               *
#*          Dimitri Bourilkov             *
#*          Vaibhav Khandelwal            *
#*          Sanket  Totala                *
#*          Sharad  Sonapeer              *
#*                                        *
#*  http://cern.ch/bourilkov/caves.html   *
#*                                        *
#******************************************
 
import cmd, os, string, sys, shutil
from vstate import *
from extract import *

# define Exceptions

class repositoryException(Exception):
    """Repository exception"""
    pass

class configException(Exception):
    """Configuration exception"""
    pass

class extractException(Exception):
    """Don't extract codesh logs exception"""
    pass

def svn(command1,command2):
    if Options.debuglevel == 0:
        com = 'svn --quiet ' + command1 + ' ' + Repository.location + command2
    else:                                                 
        com = 'svn ' + command1 + ' ' + Repository.location + command2
        print 'svn will run: ' + com
    os.system(com)

def svn1(command):
    if Options.debuglevel == 0:
        com = string.replace(command, 'svn ', 'svn --quiet ', 1)
    else:                                                 
        com = command
        print 'svn will run: ' + com
    os.system(com)


def getUniqueTag(line,type):

    newline = line.split()
    tag = newline[0]

    if type == "tag":
        svn('export','/listFiles/taglist.txt temp.txt')
    elif type == "snap":   
        svn('export','/listFiles/snaplist.txt temp.txt')

    com = 'cat temp.txt | grep ' + tag
    count = 0
    print ">>> Similar tags found:"
    for line in os.popen(com).readlines():
        shortline = line[:-1]  # strip '\n'
        print shortline
        count = count + 1

    if count == 1:
       newline[0] = shortline
       line = string.join(newline)
       return line,1
    else:
       return line,0

def checkRepo(sourceRepo):
   try:
     if (string.find(sourceRepo,"file://")) >= 0 or (string.find(sourceRepo,"svn://")) >= 0:
         fileExists = 1
     else: raise
   except:
      print "This is SVN repository"
      print "You have to enter the path like 'file:///PATH/TO/REPOSITORY' "
      print "                        OR like  'svn:///PATH/TO/REPOSITORY' "
      return 1

   try:
      com = 'svn --quiet export ' + sourceRepo + '/listFiles/taglist.txt temp.txt'
      os.system(com)
      if os.path.isfile(os.getcwd()+'/temp.txt'):
         exists = 1
         os.system('rm -f temp.txt')
      else: raise
   except:
      print "The destination repository given as >> " + sourceRepo + " << is not valid."
      return 1

def caves(cavescommand, data):
    parlist = []
    parlist = string.split(data.strip())
#   print "parlist, length: ",parlist,len(parlist)

# go to initial dir
    weweredir = State.curdir
    os.chdir(State.initialdir)

# SVN back-end
    if Repository.type == 'svn':     # svn

        logdir = 'tlogs'
        macrodir = 'tsource'
        datdir = 'tdata'

        # check for valid repository
        if Repository.flag == 0:
            print "You selected a session without repository."
            print "Can't run this command."
            print "If you need a repository, start a new session and specify one."
            os.chdir(weweredir)
            return
        if Repository.flag == 1:
            if Repository.location == 'Repository.location NOT set => NO persistent logbooks!':
                print "Repository NOT initialized."
                print "Please give repository location."
                s = raw_input("Repository => " + Repository.locationtoinput + " ?: ")
                if s: Repository.location = s
            if string.find(Repository.location,"@") > 0: # Check if the SVN repository is remote and the user can login.
                homeDir =  os.environ.get('HOME')
                [firstPart, secondPart] = string.split(Repository.location,'@')
                [protocol,userName] = string.split(firstPart,'//')
                [host,repoLocation] = string.split(secondPart,'/')
                flgSvnUser = 0
                flgHost = 0
                for fileName in os.listdir(homeDir+'/.subversion/auth/svn.simple'):
                   flgSvnUser = 0
                   flgHost = 0
                   dataFile = open(homeDir+"/.subversion/auth/svn.simple/"+fileName, 'r').readlines()
                   for line in dataFile:
                       shortline = line[:-1]
                       if userName in shortline: # svnuser always comes before server in svn file!
                          flgSvnUser = 1
                       if host in shortline:
                          flgHost = 1
                if flgSvnUser == 1 and flgHost == 1:
                    print "Remote SVN repository login found. Ready to check access."
                else:
                    com = 'svn --quiet export ' + Repository.location + '/listFiles/taglist.txt temp.txt'              
                    print "Remote SVN repository login not found. You may face trouble while running CODESH in Batch mode."
                    print "You are advised to exit and use following command to get logged in."
                    print "'"+com+"'"
            exists = 0
            fileExists = 0

            while not fileExists: # to check if protocol file:// or svn:// is included for svn in the repository path
                try:
                    if (string.find(Repository.location,"file://")) >= 0 or (string.find(Repository.location,"svn://")) >= 0:
                       fileExists = 1
                    else: raise
                except:
                    print "This is SVN repository"
                    print "You have to enter the path like 'file:///PATH/TO/REPOSITORY' "
                    print "                        OR like  'svn:///PATH/TO/REPOSITORY' "
                    s = raw_input("Repository => " + Repository.locationtoinput + " ?: ")
                    if s:
                        Repository.location = s

            while not exists:
                try:
                    if os.path.isfile(os.getcwd() + '/temp.txt'):
                        os.system('rm -f temp.txt')
                    svn('export','/listFiles/taglist.txt temp.txt')
                    if os.path.isfile(os.getcwd() + '/temp.txt'):
                        exists = 1
                        os.system('rm -f temp.txt')
                    else: raise
                except:
                    print "The initialized Repository is unaccessible."
                    print "Please give valid repository location or say EXIT."
                    s = raw_input("Repository => " + Repository.locationtoinput + " ?: ")
                    if s:
                        if s == 'EXIT':
                            print "You decided to run without repository."
                            print "CODESH will not use persistent logbooks for this session."
                            os.chdir(weweredir)
                            return
                        Repository.location = s
                else:
                    exists = 1
                    Repository.flag = 2


        # prepare & run commands
        ### BROWSE ###
        if cavescommand == 'browse':
            if len(parlist) > 0:
                tag = parlist[0]
            else:
                tag = ""
            if len(parlist) > 1:
                option = parlist[1]
            else:
                option = " "
            
            if tag == "" or option == 's':
                svn('export','/listFiles/taglist.txt temp.txt')

                if tag == "": com = 'cat temp.txt'
                if option == 's': com = 'cat temp.txt | grep ' + tag
                count = 0
                for line in os.popen(com).readlines():
                    shortline = line[:-1]  # strip '\n'
                    print shortline
                    count = count + 1
                    if count > 40:
                       print "Number of tags exceeds 40. Hence displaying only the first 40 tags."
                       print "The temp.txt file has a list of all the tags"
                       break  
                os.system('rm -f temp.txt')

            elif parlist[0] == 'snap':
                svn('export','/listFiles/snaplist.txt temp.txt')
                com = 'cat temp.txt'
                count = 0
                for line in os.popen(com).readlines():
                    shortline = line[:-1]  # strip '\n'
                    print shortline
                    count = count + 1
                    if count > 40:
                       print "Number of snapshots exceeds 40. Hence displaying only the first 40 snapshots."
                       print "The temp.txt file has a list of all the snapshots"
                       break  
                os.system('rm -f temp.txt')
            else:
                
                if Options.mysqlhost != '':
                    connection = 'mysql -h ' + Options.mysqlhost + ' -u ' + Options.mysqluser + ' -p' + Options.mysqlpass + ' -e '
                    com = connection + ' "select * from codesh01 where tag like ' + "'" + tag + "%'" + '" codesh01;'
                    for line in os.popen(com).readlines():
                        shortline = line[:-1]  # strip '\n'
                        print shortline

                try:
                    os.system('mkdir -p '+ logdir)
                    svn('export','/'+tag+'/'+logdir+'/'+LogFile.logfname + ' ' + logdir + '/' + LogFile.logfname)

                    logfile = open(logdir + '/' + LogFile.logfname, "r")
                    for line in logfile.readlines():
                        shortline = line[:-1]  # strip '\n'
                        words = string.split(shortline)
                        if words[0][0] == '#':
                            print "Comment is: ",shortline
                            continue
                        if string.find(shortline,"Macro:") >= 0:
                            print shortline
                        else:
                            print "Command is: ",shortline
                    logfile.close()
                    os.system('rm -rf ' + logdir)
                except:
                    print "Tag " + tag + " doesn't exist in repository: " + Repository.location
        ### LOG ###
        elif cavescommand == 'log':
            LogFile.logfile.close()
            LogFile.fulllogfile.close()
            if len(parlist) < 1:
              print "The log syntax entered is wrong"
              print "log syntax is:"
              print "log <tag>"
              os.chdir(weweredir)
              return
            tag = parlist[0]
            if len(parlist) > 1:
                annotation = string.join(parlist[1:]," ")
            else:
                annotation = " "
            annotation = string.replace(annotation, '"', '')
            annotfname = tag + '.annotation'
            annotfile = open(annotfname,'w')
            annotfile.write(annotation + '\n')
            annotfile.close()
            os.system('mkdir ' + tag)
            os.system('mkdir ' + tag + '/' + logdir)
            os.system('mkdir ' + tag + '/' + macrodir)
            LogFile.logfile = open(LogFile.logfname,'r')
            for line in LogFile.logfile.readlines():
                shortline = line[:-1]  # strip '\n'
                print shortline
                if string.find(shortline,"Macro:") >= 0:
                    wordlist = string.split(shortline)
                    macrofile = wordlist[1]
                    if Options.debuglevel > 2: print "Macro is: ",macrofile
                    os.system('cp -f ' + weweredir + '/' + macrofile + ' ' + tag + '/' + macrodir)
            LogFile.logfile.close()
            os.system('cp -f ' + LogFile.logfname + ' ' + tag + '/' + logdir + '/' + LogFile.logfname)
            os.system('cp -f ' + LogFile.fulllogfname + ' ' + tag +'/' + logdir + '/' + LogFile.fulllogfname)
            os.system('cp -f ' + annotfname + ' ' + tag + '/' + logdir + '/' + annotfname)
            os.system('rm -f ' + LogFile.logfname)
            os.system('rm -f ' + LogFile.fulllogfname)
            os.system('rm -f ' + annotfname)
            if Options.loglevel == 3 and Options.statelevel == 1:
                os.system('cp -f ' + State.envfnameinit  + ' ' + tag + '/' + logdir + '/' + State.envfnameinit)
                os.system('cp -f ' + State.aliasfnameinit + ' ' + tag + '/' + logdir + '/' + State.aliasfnameinit)
                os.system('cp -f ' + State.envfname + ' ' + State.envfnameinit)
                os.system('cp -f ' + State.aliasfname + ' ' + State.aliasfnameinit)
                os.system('cp -f ' + State.envfname + ' ' + tag + '/' + logdir + '/' + State.envfnamefinal)
                os.system('cp -f ' + State.aliasfname + ' ' + tag + '/' + logdir + '/' + State.aliasfnamefinal)

            svn('import ' + tag,'/' + tag + ' -m "Adding a New Session"')
            os.system('rm -rf ' + tag)
            os.system('rm -rf listFiles')
            svn('checkout','/listFiles' + ' listFiles')
            listFile = open('listFiles/taglist.txt', "a")
            listFile.write(tag + '\n')
            listFile.close()
            os.chdir('listFiles')
            svn1('svn commit -m "log commit"')
            os.chdir("..")
            os.system('rm -rf listFiles')

            freshlogfile = LogFile()

            if Options.mysqlhost != '':
                connection = 'mysql -h ' + Options.mysqlhost + ' -u ' + Options.mysqluser + ' -p' + Options.mysqlpass + ' -e '
                command = " INSERT INTO codesh01 VALUES ('" + tag + "',NULL,'" + annotation + "','" + Options.userID + "','" + Options.groupID + "','" + Repository.location + "')"  
                com = connection + '"' + command + '" codesh01;'
                for line in os.popen(com).readlines():
                    shortline = line[:-1]  # strip '\n'
                    print shortline
        ### INSPECT / EXTRACT ###
        elif cavescommand == 'inspect' or cavescommand == 'extract':
            if len(parlist) < 1:
                if cavescommand == 'inspect':
                    print "The inspect syntax entered is wrong"
                    print "inspect syntax is:"
                    print "inspect <tag> <brief|complete>"
                if cavescommand == 'extract':
                    print "The extract syntax entered is wrong"
                    print "extract syntax is:"
                    print "extract <tag>"
                os.chdir(weweredir)
                return
            # 2.5 repositoryException = "Repository exception"
            # 2.5 configException = "Configuration exception"
            # 2.5 extractException = "Don't extract codesh logs exception"
            tag = parlist[0]
            listReplacement = []
            delim = ''
            if len(parlist) > 1:
                option = parlist[1]
                if len(parlist) > 3:
                    listReplacement, delim = getReplacementList(parlist)
            else:
                option = " "
            try:
                replogdir = '/' + tag + '/' + logdir
                repmacrodir = '/' + tag + '/' + macrodir
                if option[0] == 'c' or cavescommand == 'extract':
                    if Options.loglevel == 3 and Options.statelevel == 1:  # get INITIAL/FINAL state of transition
                        svn('export',replogdir + '/' + State.envfnameinit + ' ' + State.envfnameinit)
                        svn('export',replogdir + '/' + State.aliasfnameinit + ' ' + State.aliasfnameinit)
                        svn('export',replogdir + '/' + State.envfnamefinal + ' ' + State.envfnamefinal)
                        svn('export',replogdir + '/' + State.aliasfnamefinal + ' ' + State.aliasfnamefinal)
                svn('export',replogdir + '/' + LogFile.logfname + ' ' + tag +'.log')

                if cavescommand == 'extract':
                                        
                    logfile = open(tag +'.log')
                    linenumber = 0
               
                    repository = ''
                    shell = ''
                    loglevel = -1
                    codeshloglevel = -1
                    statelevel = -1
                    debuglevel = -1
                    cleanpath = -1

                    header_in_logfile = 0 
                    for line in logfile.readlines():
                        keyvalues = string.split(line)
                        if keyvalues[0] == '#':
                            header_in_logfile = 1
                            if 'Repository' in keyvalues[1:]:
                                repository = keyvalues[2]
                            elif 'Subshell' in keyvalues[1:]:
                                shell = keyvalues[2]
                            elif 'Loglevel' in keyvalues[1:]:
                                loglevel = string.atoi(keyvalues[2])
                            elif 'Codeshloglevel' in keyvalues[1:]:
                                codeshloglevel = string.atoi(keyvalues[2])
                            elif 'Statelevel' in keyvalues[1:]:
                                statelevel = string.atoi(keyvalues[2])
                            elif 'Debuglevel' in keyvalues[1:]:
                                debuglevel = string.atoi(keyvalues[2])
                            elif 'Cleanpath' in keyvalues[1:]:
                                cleanpath = string.atoi(keyvalues[2])
                        else:
                            break

                    logfile.close()

                    if header_in_logfile == 1:
                        if codeshloglevel == 1: raise extractException
                        if (shell != Options.shell or loglevel != Options.loglevel or
                        statelevel != Options.statelevel or cleanpath != Options.cleanpath):
                            # sys.exit()
                            tagconffile = tag + '.conf'
                            tagconf = open(tagconffile,'w')
                            tagconf.write('# Repository ' + Repository.location + '\n')
                            tagconf.write('# Repositorytype ' + Repository.type + '\n')
                            tagconf.write('# Subshell ' + shell + '\n')
                            tagconf.write('# Loglevel ' + str(loglevel) + '\n')
                            tagconf.write('# Codeshloglevel ' + str(codeshloglevel) + '\n')
                            tagconf.write('# Statelevel ' + str(statelevel) + '\n')
                            tagconf.write('# Debuglevel ' + str(debuglevel) + '\n')
                            tagconf.write('# Cleanpath '  + str(cleanpath) + '\n')
                            tagconf.close()
                            raise configException

                logfile = open(tag +'.log')
                for line in logfile.readlines():
                    os.chdir(State.initialdir)
                    shortline = line[:-1]  # strip '\n'
                    words = string.split(shortline)
                    if words[0][0] == '#':
                        print "Comment is: ",shortline
                        continue
                    if string.find(shortline,"Macro:") >= 0:
                        print shortline
                    else:
                        print "Command is: " + shortline
                    if string.find(shortline,"Macro:") >= 0:
                        if option[0] == 'c' or cavescommand == 'extract':  # complete - get macro sources
                            wordlist = string.split(shortline)
                            macrofile = wordlist[1]
                            # print "Macro is: ",macrofile
                            svn('export',repmacrodir + '/' + macrofile + ' ' + weweredir + '/' + macrofile)
                            os.chmod(weweredir + '/' + macrofile,0744)
                    else:
                        if cavescommand == 'extract':  # run it !
                            if linenumber == 0 and Options.loglevel == 3 and Options.statelevel == 1:  # init state for extract (from repository)
                                os.system('cp -f ' + State.envfnameinit + ' ' + State.envfname)
                                os.system('cp -f ' + State.aliasfnameinit + ' ' + State.aliasfname)
                            linenumber = linenumber + 1
                            try:
                                os.chdir(weweredir)
                                # old: os.system(shortline)
                                if shortline[0:2] == 'cd':
                                    extractcd(shortline)
                                    weweredir = State.curdir
                                else:
                                    extractrun(shortline,listReplacement,delim)
                                    os.chdir(State.initialdir)
                            except:
                                print "Problem in extracting on line: " + linenumber + " >>> " + shortline
                logfile.close()
            except repositoryException:
                print 'Tag => ' + tag + ' <= does not exist in repository  ' + Repository.location
            except extractException:
                print 'Extract does NOT work for codesh log files'
                print ' (when codeshloglevel == 1 and the logfile'
                print ' contains a mix of shell and codesh commands)'
                print 'To extract the tag re-start Codesh using batch mode'
                print 'e.g. codesh.py -b < ' + tag +'.log'
            except configException:
                print 'Configurations of the tag to be extracted'
                print 'are different from the current configurations.'
                print 'Extraction cannot proceed.'
                print 'Copying the Configurations of the desired tag to ' + tagconffile
                print 'To extract the tag re-start Codesh using the -c option'
                print 'e.g. codesh.py -c ' + tag + '.conf'
                print 'and issue again the extract <tag> command.'
            except:
                print "Problem inspecting OR extracting Tag: " + tag
        ### TAGCOPY ###
        elif cavescommand == 'tagcopy':
            if len(parlist) < 2:
                print "The tagcopy syntax entered is wrong"
                print "tagcopy syntax is:"
                print "tagcopy <tag> <to> <from>"
                print "   if <from> is omitted then copy from CURRENT repository"
                os.chdir(weweredir)
                return
            sourcerepos = Repository.location
            try:
                tag = parlist[0]
                if len(parlist) > 1:
                    # checking if destination repository is valid
                    flag = checkRepo(parlist[1])
                    if flag == 1: return
                    destinationrepos = parlist[1]
                if len(parlist) > 2:
                    # checking if source repository is valid
                    flag = checkRepo(parlist[2])
                    if flag == 1: return
                    sourcerepos = parlist[2]
                svn1('svn export ' + sourcerepos + '/' + tag + ' ' + tag)
                svn1('svn import ' + tag + ' ' + destinationrepos + '/' + tag + ' -m "Copying Tag"')
                os.system('rm -rf ' + tag)
                os.system('rm -rf listFiles')
                svn1('svn checkout ' + destinationrepos + '/listFiles' + ' listFiles')
                listFile = open('listFiles/taglist.txt', "a")
                listFile.write(tag + '\n')
                listFile.close()
                os.chdir('listFiles')
                svn1('svn commit -m "log commit"')
                os.chdir("..")
                os.system('rm -rf listFiles')
            except:
                print "Wrong parameters for tagcopy:",parlist
 	### TAGDELETE ###
        elif cavescommand == 'tagdelete':
            if len(parlist) < 1:
                print "The tagdelete syntax entered is wrong"
                print "tagdelete syntax is:"
                print "tagdelete <tag> <in_repository>"
                os.chdir(weweredir)
                return
            targetrepository = Repository.location
            try:
                tag = parlist[0]
                if len(parlist) > 1: 
                   targetrepository = parlist[1]
                   flag = checkRepo(targetrepository)
                   if flag == 1: return
                s = raw_input("You are about to delete tag: " + tag + " from " + targetrepository + " (Y/N) ?: ")
                if s:
                    if s != 'Y':
                        print "You did not reply Y => aborting tagdelete"
                        return
                svn1('svn delete ' + targetrepository + '/' + tag + ' -m "Deleting Directory"')
		
                # Deleting the tag name from the taglist.txt in the svn repository
                os.system('rm -rf listFiles')
                svn1('svn checkout ' + targetrepository + '/listFiles' + ' listFiles')
                listFile = open('listFiles/taglist.txt', "r")
                os.system('rm -f temptag.txt')
                tempFile = open('temptag.txt', "w")
                for line in listFile.readlines():
                    shortline = line[:-1]  # strip '\n'                    
                    if shortline != tag:
                       tempFile.write(shortline + '\n')
                listFile.close()
                tempFile.close()
                if Options.debuglevel > 1: os.system('echo Old taglist.txt; cat listFiles/taglist.txt')
                os.system('rm -f listFiles/taglist.txt')
                os.system('mv -f ' + 'temptag.txt ' + 'listFiles/taglist.txt')
                os.chdir('listFiles')
                if Options.debuglevel > 1: os.system('echo New taglist.txt; cat taglist.txt')
                svn1('svn commit -m "log commit"')
                os.chdir("..")
                os.system('rm -rf listFiles')

            except:
                print "Wrong parameters for tagdelete:",parlist
        ### TAKESNAPSHOT ###
        elif cavescommand == 'takesnapshot':
            os.chdir(weweredir)
            if len(parlist) < 1:
                print "The takesnapshot syntax entered is wrong"
                print "takesnapshot syntax is:"
                print "takesnapshot <tag>"
                return
            try:
                tag = parlist[0]
                if len(parlist) > 1:
                    annotation = string.join(parlist[1:]," ")
                else:
                    annotation = " "
                annotfname = tag + '.annotation'
                annotfile = open(annotfname,'w')
                annotfile.write(annotation + '\n')
                annotfile.close()
                svn('import','/snapshots/' + tag + ' -m "taking snapshot"')
                os.system('rm -f ' + annotfname)
                os.chdir(State.initialdir)
                os.system('rm -rf listFiles')
                svn('checkout','/listFiles ' + ' listFiles')
                listFile = open('listFiles/snaplist.txt', "a")
                listFile.write(tag + '\n')
                listFile.close()
                os.chdir('listFiles')
                if Options.debuglevel > 1: os.system('cat snaplist.txt')
                svn1('svn commit -m "log commit"')
                os.chdir("..")
                os.system('rm -rf listFiles')
            except:
                print "Error taking snapshot"
        ### GETSNAPSHOT ###
        elif cavescommand == 'getsnapshot':
            os.chdir(weweredir)
            if len(parlist) < 1:
                print "The getsnapshot syntax entered is wrong"
                print "getsnapshot syntax is:"
                print "getsnapshot <tag>"
                return
            try:
                tag = parlist[0]
                svn('export','/snapshots/' + tag + ' ' + tag)
            except:
                print "Error getting snapshot"
        else:
            print 'Unknown codesh command: ' + cavescommand

# go back to current dir
    os.chdir(weweredir)

