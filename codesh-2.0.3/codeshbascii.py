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

class Command:
    current = ''
    
def asc(command):
    if(Repository.remoteAsciiUser == ''):  # local: under my thumb
        com = command
    else:  # remote and more tricky
        if string.find(command,"scp -pr ") > -1:  # scp is already prepared
            com = command
        else:
            com = "ssh " + Repository.remoteAsciiUser + " " + command
    if Options.debuglevel > 0: print "== codeshbascii.py will run command => " + com
    os.system(com)

def addcommittag(filename,annotation,tag):
    if(Repository.remoteAsciiUser == ''):  # local: under my thumb
        asc('cp ' + filename + ' ' + Repository.location + '/' + tag + '/' + filename)
    else:  # remote and more tricky  copy FROM local
        asc('scp -pr ' + filename + ' ' + Repository.remoteAsciiUser + ":" + Repository.location + '/' + tag + '/' + filename)

def getUniqueTag(line,type):

    newline = line.split()
    tag = newline[0]
   
    if(Repository.remoteAsciiUser == ''):  # local: under my thumb
        placetolist = Repository.location
    else:  # remote and more tricky
        placetolist = Repository.remoteAsciiRepoLocation

    if type == "tag":
        asc('ls -1 ' + placetolist + ' | grep -v snapshots > temp.txt')
    elif type == "snap":
        asc('ls -1 ' + placetolist + '/snapshots/ > temp.txt')
        
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

def fileexists(filename):
    flag = 0
    if(Repository.remoteAsciiUser == ''):  # local: under my thumb
        if os.path.exists(filename): flag = 1  # true
    else:  # remote and more tricky
        if os.system("ssh " + Repository.remoteAsciiUser + " ls " + filename) == 0: flag = 1  # true
    return flag

def filecopy(source, destination):
    if Command.current == 'tagcopy':  # most tricky: can be both FROM/TO local
        itinerary = source + destination
        if string.find(itinerary,"@") > 0:  # remote (use scp)
            asc('scp -pr ' + source + ' ' + destination)
        else:  # local
            asc('cp -pr ' + source + ' ' + destination)
        return
    if(Repository.remoteAsciiUser == ''):  # local: under my thumb
        asc('cp -f -pr ' + source + ' ' + destination)
    else:  # remote and more tricky
        if Command.current == 'takesnapshot':  # copy TO remote
            asc('scp -pr ' + source + ' ' + Repository.remoteAsciiUser + ":" + destination)
        else:    # copy TO local
            asc('scp -pr ' + Repository.remoteAsciiUser + ":" + source + ' ' + destination)

def checkRepo(sourceRepo):
    try:
       if(Repository.remoteAsciiUser == ''):  # local: under my thumb
          filename = sourceRepo + '/asciiRepoValid'
       else:  # remote and more tricky
          filename = Repository.remoteAsciiRepoLocation + "/asciiRepoValid"
       if fileexists(filename): exists = 1
       else: raise
    except:
       print "The destination repository given as >> " + sourceRepo + " << is not valid."
       return 1

def caves(cavescommand, data):
    Command.current = cavescommand
    parlist = []
    parlist = string.split(data.strip())
#   print "parlist, length: ",parlist,len(parlist)

# go to initial dir
    weweredir = State.curdir
    os.chdir(State.initialdir)

# ASCII FILES back-end
    if Repository.type == 'ascii':     # ascii

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
            exists = 0
            while not exists:
                try:
                    if(Repository.remoteAsciiUser == ''):  # local: under my thumb
                        filename = Repository.location + '/asciiRepoValid'
                    else:  # remote and more tricky
                        filename = Repository.remoteAsciiRepoLocation + "/asciiRepoValid"
                    if fileexists(filename): exists = 1
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
                        if string.find(Repository.location,"@") > 0:  # remote
                            [Repository.remoteAsciiUser, Repository.remoteAsciiRepoLocation] = string.split(Repository.location,':')
                else:
                    exists = 1
                    Repository.flag = 2
                    if Repository.remoteAsciiUser:
                        # store the corrected location in the logfile
                        LogFile.logfile.write('# Repository ' + Repository.location + '\n')
                        Repository.location = Repository.remoteAsciiRepoLocation

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
                asc('ls -1 ' + Repository.location + ' | grep -v snapshots | grep -v asciiRepoValid > temp.txt')
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
            elif parlist[0] == 'snap':
                asc('ls -1 ' + Repository.location + '/snapshots/')
            else:
                
                if Options.mysqlhost != '':
                    connection = 'mysql -h ' + Options.mysqlhost + ' -u ' + Options.mysqluser + ' -p' + Options.mysqlpass + ' -e '
                    com = connection + ' "select * from codesh01 where tag like ' + "'" + tag + "%'" + '" codesh01;'
                    for line in os.popen(com).readlines():
                        shortline = line[:-1]  # strip '\n'
                        print shortline

                try:
                    os.system('mkdir -p '+ logdir)
                    replogdir = Repository.location + '/' + tag + '/' + logdir
                    if not fileexists(replogdir): raise
                    filecopy(replogdir + '/' + LogFile.logfname,logdir)
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
            asc('mkdir '+ Repository.location + '/' + tag)
            asc('mkdir -p ' + Repository.location + '/' + tag +'/' + logdir)
            asc('mkdir -p ' + Repository.location + '/' + tag +'/' + macrodir)
            LogFile.logfile = open(LogFile.logfname,'r')
            for line in LogFile.logfile.readlines():
                shortline = line[:-1]  # strip '\n'
                print shortline
                if string.find(shortline,"Macro:") >= 0:
                    wordlist = string.split(shortline)
                    macrofile = wordlist[1]
                    # print "Macro is: ",macrofile
                    os.system('mkdir -p ' + macrodir)
                    os.chdir(macrodir)
                    os.system('cp -f ' + weweredir + '/' + macrofile + '  .')
                    os.chdir("..")
                    addcommittag(macrodir + '/' + macrofile,annotation,tag)
                    os.system('rm -rf ' + macrodir + '/' + macrofile)
            LogFile.logfile.close()
            os.system('mkdir -p '+ logdir)
            os.system('cp -f ' + LogFile.logfname + ' ' + logdir + '/' + LogFile.logfname)
            os.system('cp -f ' + LogFile.fulllogfname + ' ' + logdir + '/' + LogFile.fulllogfname)
            os.system('cp -f ' + annotfname + ' ' + logdir + '/' + annotfname)
            addcommittag(logdir + '/' + LogFile.logfname,annotation,tag)
            os.system('rm -f ' + LogFile.logfname)
            addcommittag(logdir + '/' + LogFile.fulllogfname,annotation,tag)  
            os.system('rm -f ' + LogFile.fulllogfname)
            addcommittag(logdir + '/' + annotfname,annotation,tag)  
            os.system('rm -f ' + annotfname)
            if Options.loglevel == 3 and Options.statelevel == 1:
                os.system('mkdir -p '+ logdir)
                os.system('cp -f ' + State.envfnameinit + ' ' + logdir + '/' + State.envfnameinit)
                os.system('cp -f ' + State.aliasfnameinit + ' ' + logdir + '/' + State.aliasfnameinit)
                addcommittag(logdir + '/' +  State.envfnameinit,annotation,tag)  
                addcommittag(logdir + '/' +  State.aliasfnameinit,annotation,tag)
                os.system('cp -f ' + State.envfname + ' ' + State.envfnameinit)
                os.system('cp -f ' + State.aliasfname + ' ' + State.aliasfnameinit)
                os.system('cp -f ' + State.envfname + ' ' + logdir + '/' + State.envfnamefinal)
                os.system('cp -f ' + State.aliasfname + ' ' + logdir + '/' + State.aliasfnamefinal)
                addcommittag(logdir + '/' +  State.envfnamefinal,annotation,tag)
                addcommittag(logdir + '/' +  State.aliasfnamefinal,annotation,tag)
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
                replogdir = Repository.location + '/' + tag + '/' + logdir
                if not fileexists(replogdir): raise repositoryException
                repmacrodir = Repository.location + '/' + tag + '/' + macrodir
                if option[0] == 'c' or cavescommand == 'extract':
                    if Options.loglevel == 3 and Options.statelevel == 1:  # get INITIAL/FINAL state of transition
                        filecopy(replogdir + '/' + State.envfnameinit,State.envfnameinit)
                        filecopy(replogdir + '/' + State.aliasfnameinit,State.aliasfnameinit)
                        filecopy(replogdir + '/' + State.envfnamefinal,State.envfnamefinal)
                        filecopy(replogdir + '/' + State.aliasfnamefinal,State.aliasfnamefinal)
                filecopy(replogdir + '/' + LogFile.logfname,tag +'.log')

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
                            filecopy(repmacrodir + '/' + macrofile,weweredir + '/' + macrofile)
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
            os.chdir(weweredir)
            if len(parlist) < 2:
                print "The tagcopy syntax entered is wrong"
                print "tagcopy syntax is:"
                print "tagcopy <tag> <to> <from>"
                print "   if <from> is omitted then copy from CURRENT repository"
                return
            if(Repository.remoteAsciiUser == ''):  # local: under my thumb
                sourcerepos = Repository.location
            else:  # remote and more tricky
                sourcerepos = Repository.remoteAsciiUser + ":" + Repository.location
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
                if len(parlist) > 2: sourcerepos = parlist[2]
                filecopy(sourcerepos + '/' + tag, destinationrepos)
            except:
                print "Wrong parameters for tagcopy:",parlist
 	### TAGDELETE ###
        elif cavescommand == 'tagdelete':
            os.chdir(weweredir)
            if len(parlist) < 1:
                print "The tagdelete syntax entered is wrong"
                print "tagdelete syntax is:"
                print "tagdelete <tag> <in_repository>"
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
                asc('rm -rf ' + targetrepository + '/' + tag)
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
                asc('mkdir ' + Repository.location + '/snapshots/' + tag)
                filecopy(annotfname, Repository.location + '/snapshots/' + tag)
                filecopy('.', Repository.location + '/snapshots/' + tag)
                asc('rm -f ' + annotfname)
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
                filecopy(Repository.location + '/snapshots/' + tag, '.')
            except:
                print "Error getting snapshot"
        else:
            print 'Unknown codesh command: ' + cavescommand

# go back to current dir
    os.chdir(weweredir)

