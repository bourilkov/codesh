#!/usr/bin/env python3
#***************************************************
#* Copyright (C) 2006, University of Florida       *
#* Authors: D.Bourilkov,                           *
#*          V.Khandelwal, S.Totala, S.Sonapeer     *
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
from subprocess import Popen,PIPE,STDOUT

# define Exceptions

class configException(Exception):
    """Configuration exception"""
    pass

class extractException(Exception):
    """Don't extract codesh logs exception"""
    pass

def cvs(command):
    if Options.debuglevel == 0:
        com = 'cvs -Q -d ' + Repository.location + ' ' + command
    else:
        com = 'cvs -d ' + Repository.location + ' ' + command
    os.system(com)


def addcommittag(filename,annotation,tag):
     cvs('add ' + filename)
     cvs('commit -m "' + annotation + '" ' + filename)
     cvs('tag -c ' + tag + ' ' + filename)
     
def getUniqueTag(line,type):
    logdir = 'tlogs'

    newline = line.split()
    tag = newline[0]
    
    if type == "tag":
        cvs('co ' + logdir + '/' + LogFile.logfname)
        cvs('status -v ' + logdir + '/' + LogFile.logfname + ' > temp.txt')
        cvs('release -d ' + logdir)
        com = 'cat temp.txt | grep "(rev" | grep ' + tag
    elif type == "snap":
        cvs('co snapshots/snaplist.txt')
        os.system('cp snapshots/snaplist.txt temp.txt')
        com = 'cat temp.txt | grep ' + tag

    count = 0
    print(">>> Similar tags found:")
    for line in os.popen(com).readlines():
        print(line)
        shortline = line.split()
        count = count + 1
     
    if count == 1:
       newline[0] = shortline[0]
       line = " ".join(newline)
       return line,1
    else:
       return line,0

def checkRepo(sourceRepo):
    logdir = 'tlogs'
    # os.system('rm -rf tlogs')
    try:
       com = 'cvs -d ' + sourceRepo + ' co ' + logdir + '/dummy.file'
       (stdin, stdout, stderr) = os.popen3(com,'t')
       for line in stderr.readlines():
          shortline = line[:-1]  # strip '\n'
          print(shortline)
          raise
       file = open(logdir + '/dummy.file')
    except:
       print("The destination repository given as >> " + sourceRepo + " << is not valid.")
       return 1

def tagcopy(file,tag,torepos,fromrepos):
    annotation = " "
    os.chdir('tempdest')
    Repository.location = torepos
    cvs('co ' + file)
    os.system('cp -f ' + State.initialdir + '/' + file + ' ' + file)
    addcommittag(file,annotation,tag)
    Repository.location = fromrepos
    os.chdir(State.initialdir)

def caves(cavescommand, data):
    parlist = []
    parlist = data.strip().split()
#   print "parlist, length: ",parlist,len(parlist)

# go to initial dir
    weweredir = State.curdir
    os.chdir(State.initialdir)

# CVS back-end
    if Repository.type == 'cvs':     # cvs

        logdir = 'tlogs'
        macrodir = 'tsource'
        datdir = 'tdata'

        # check for valid repository
        if Repository.flag == 0:
            print("You selected a session without repository.")
            print("Can't run this command.")
            print("If you need a repository, start a new session and specify one.")
            os.chdir(weweredir)
            return
        if Repository.flag == 1:
            if Repository.location == 'Repository.location NOT set => NO persistent logbooks!':
                print("Repository NOT initialized.")
                print("Please give repository location.")
                s = input("Repository => " + Repository.locationtoinput + " ?: ")
                if s: Repository.location = s
            if Repository.location.find("@") > 0: # Check if the CVS repository is remote and the user can login.
                homeDir =  os.environ.get('HOME')
                cvsfile = open(homeDir+'/.cvspass', "r")
                flgRepoLogged = 0
                for line in cvsfile.readlines():
                    shortline = line[:-1]  # strip '\n'
                    if shortline.find(Repository.location) >= 0:
                        print("Remote CVS repository login found. Ready to check access.")
                        flgRepoLogged = 1
                        break
                if flgRepoLogged == 0:
                       com = 'cvs -d '+Repository.location+' login'
                       print("Remote CVS repository login not found. You may face trouble while running CODESH.")
                       print("You are advised to exit and use command : "+com+" to login to remote CVS repository")
            exists = 0
            while not exists:
                try:
                    com = 'cvs -d ' + Repository.location + ' co ' + logdir + '/dummy.file'
                    # 2.5 (stdin, stdout, stderr) = os.popen3(com,'t')
                    p = Popen(com, shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE, close_fds=True)
                    (stdin, stdout, stderr) = (p.stdin, p.stdout, p.stderr)
                    for line in stderr.readlines():
                        shortline = line[:-1]  # strip '\n'
                        print(shortline)
                        raise
                    file = open(logdir + '/dummy.file')
                    cvs('release -d ' + logdir)
                except:
                    print("The initialized Repository is unaccessible.")
                    print("Please give valid repository location or say EXIT.")
                    s = input("Repository => " + Repository.locationtoinput + " ?: ")
                    if s:
                        if s == 'EXIT':
                            print("You decided to run without repository.")
                            print("CODESH will not use persistent logbooks for this session.")
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
                cvs('co ' + logdir + '/' + LogFile.logfname)
                cvs('status -v ' + logdir + '/' + LogFile.logfname + ' > temp.txt')
                cvs('release -d ' + logdir)
                if tag == "": com = 'cat temp.txt | grep "(rev"'
                if option == 's': com = 'cat temp.txt | grep "(rev" | grep ' + tag
                count = 0
                for line in os.popen(com).readlines():
                    shortline = line[:-1]  # strip '\n'
                    print(shortline)
                    count = count + 1
                    if count > 40:
                       print("Number of tags exceeds 40. Hence displaying only the first 40 tags.")
                       print("The temp.txt file has a list of all the tags")
                       break  

            elif parlist[0] == 'snap':
                cvs('co snapshots/snaplist.txt')
                os.system('cp snapshots/snaplist.txt temp.txt')
                cvs('release -d snapshots')
                com = 'cat temp.txt'
                count = 0
                for line in os.popen(com).readlines():
                    shortline = line[:-1]  # strip '\n'
                    print(shortline)
                    count = count + 1
                    if count > 40:
                       print("Number of snapshots exceeds 40. Hence displaying only the first 40 snapshots.")
                       print("The temp.txt file has a list of all the snapshots")
                       break
                os.system('rm -f temp.txt')
            else:
                
                if Options.mysqlhost != '':
                    connection = 'mysql -h ' + Options.mysqlhost + ' -u ' + Options.mysqluser + ' -p' + Options.mysqlpass + ' -e '
                    com = connection + ' "select * from codesh01 where tag like ' + "'" + tag + "%'" + '" codesh01;'
                    for line in os.popen(com).readlines():
                        shortline = line[:-1]  # strip '\n'
                        print(shortline)

                try:
                 try:
                    cvs('co -r ' + tag + ' ' + logdir + '/' + LogFile.logfname)
                    cvs('co -r ' + tag + ' ' + logdir + '/' + LogFile.fulllogfname)
                    logfile = open(logdir + '/' + LogFile.logfname, "r")
                    for line in logfile.readlines():
                        shortline = line[:-1]  # strip '\n'
                        words = shortline.split()
                        if words[0][0] == '#':
                            print("Comment is: ",shortline)
                            continue
                        if shortline.find("Macro:") >= 0:
                            print(shortline)
                        else:
                            print("Command is: ",shortline)
                    logfile.close()
                 except:
                    print("Tag " + tag + " doesn't exist in repository: " + Repository.location)
                finally:
                    cvs('release -d ' + logdir)
        ### LOG ###
        elif cavescommand == 'log':
            LogFile.logfile.close()
            LogFile.fulllogfile.close()
            if len(parlist) < 1:
              print("The log syntax entered is wrong")
              print("log syntax is:")
              print("log <tag>")
              os.chdir(weweredir)
              return
            tag = parlist[0]
            if len(parlist) > 1:
                annotation = " ".join(parlist[1:])
            else:
                annotation = " "
            annotation = annotation.replace('"', '')
            LogFile.logfile = open(LogFile.logfname,'r')
            for line in LogFile.logfile.readlines():
                shortline = line[:-1]  # strip '\n'
                print(shortline)
                if shortline.find("Macro:") >= 0:
                    wordlist = shortline.split()
                    macrofile = wordlist[1]
                    # print "Macro is: ",macrofile
                    cvs('co ' + macrodir + "/dummy.file")
                    os.chdir(macrodir)
                    cvs('update -A dummy.file')
                    cvs('update -A ' + macrofile)
                    os.system('cp -f ' + weweredir + '/' + macrofile + '  .')
                    addcommittag(macrofile,annotation,tag)
                    os.chdir("..")
                    cvs('release -d ' + macrodir)
            LogFile.logfile.close()
            cvs('co ' + logdir + "/dummy.file")
            cvs('update -A ' + logdir + "/dummy.file")
            cvs('update -A ' + logdir + '/' + LogFile.logfname)
            cvs('update -A ' + logdir + '/' + LogFile.fulllogfname)
            os.system('cp -f ' + LogFile.logfname + ' ' + logdir + '/' + LogFile.logfname)
            os.system('cp -f ' + LogFile.fulllogfname + ' ' + logdir + '/' + LogFile.fulllogfname)
            addcommittag(logdir + '/' + LogFile.logfname,annotation,tag)
            os.system('rm -f ' + LogFile.logfname)
            addcommittag(logdir + '/' + LogFile.fulllogfname,annotation,tag)  
            os.system('rm -f ' + LogFile.fulllogfname)
            if Options.loglevel == 3 and Options.statelevel == 1:
                cvs('update -A ' + logdir + '/' + State.envfnameinit)
                cvs('update -A ' + logdir + '/' + State.aliasfnameinit)
                os.system('cp -f ' + State.envfnameinit + ' ' + logdir + '/' + State.envfnameinit)
                os.system('cp -f ' + State.aliasfnameinit + ' ' + logdir + '/' + State.aliasfnameinit)
                addcommittag(logdir + '/' +  State.envfnameinit,annotation,tag)  
                addcommittag(logdir + '/' +  State.aliasfnameinit,annotation,tag)
                os.system('cp -f ' + State.envfname + ' ' + State.envfnameinit)
                os.system('cp -f ' + State.aliasfname + ' ' + State.aliasfnameinit)
                cvs('update -A ' + logdir + '/' + State.envfnamefinal)
                cvs('update -A ' + logdir + '/' + State.aliasfnamefinal)
                os.system('cp -f ' + State.envfname + ' ' + logdir + '/' + State.envfnamefinal)
                os.system('cp -f ' + State.aliasfname + ' ' + logdir + '/' + State.aliasfnamefinal)
                addcommittag(logdir + '/' +  State.envfnamefinal,annotation,tag)
                addcommittag(logdir + '/' +  State.aliasfnamefinal,annotation,tag)
            cvs('release -d ' + logdir)
            freshlogfile = LogFile()

            if Options.mysqlhost != '':
                connection = 'mysql -h ' + Options.mysqlhost + ' -u ' + Options.mysqluser + ' -p' + Options.mysqlpass + ' -e '
                command = " INSERT INTO codesh01 VALUES ('" + tag + "',NULL,'" + annotation + "','" + Options.userID + "','" + Options.groupID + "','" + Repository.location + "')"  
                com = connection + '"' + command + '" codesh01;'
                for line in os.popen(com).readlines():
                    shortline = line[:-1]  # strip '\n'
                    print(shortline)
            
        ### INSPECT / EXTRACT ###
        elif cavescommand == 'inspect' or cavescommand == 'extract':
            if len(parlist) < 1:
                if cavescommand == 'inspect':
                    print("The inspect syntax entered is wrong")
                    print("inspect syntax is:")
                    print("inspect <tag> <brief|complete>")
                if cavescommand == 'extract':
                    print("The extract syntax entered is wrong")
                    print("extract syntax is:")
                    print("extract <tag>")
                os.chdir(weweredir)
                return
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
             try:
                if option[0] == 'c' or cavescommand == 'extract':
                    if Options.loglevel == 3 and Options.statelevel == 1:  # get INITIAL/FINAL state of transition
                        cvs('co -r' + tag + ' ' + logdir + '/' + State.envfnameinit)
                        cvs('co -r' + tag + ' ' + logdir + '/' + State.aliasfnameinit)
                        cvs('co -r' + tag + ' ' + logdir + '/' + State.envfnamefinal)
                        cvs('co -r' + tag + ' ' + logdir + '/' + State.aliasfnamefinal)
                        os.system('cp -f ' + logdir + '/' + State.envfnameinit + ' ' + State.envfnameinit)
                        os.system('cp -f ' + logdir + '/' + State.aliasfnameinit + ' ' + State.aliasfnameinit)
                        os.system('cp -f ' + logdir + '/' + State.envfnamefinal + ' ' + State.envfnamefinal)
                        os.system('cp -f ' + logdir + '/' + State.aliasfnamefinal + ' ' + State.aliasfnamefinal)
                cvs('co -r' + tag + ' ' + logdir + '/' + LogFile.logfname)
                os.system('cp -f ' + logdir + '/' + LogFile.logfname + ' ' + tag +'.log')

                if cavescommand == 'extract':
                                        
                    logfile = open(logdir + '/' + LogFile.logfname,'r')
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
                        keyvalues = line.split()
                        if keyvalues[0] == '#':
                            header_in_logfile = 1
                            if 'Repository' in keyvalues[1:]:
                                repository = keyvalues[2]
                            elif 'Subshell' in keyvalues[1:]:
                                shell = keyvalues[2]
                            elif 'Loglevel' in keyvalues[1:]:
                                loglevel = int(keyvalues[2])
                            elif 'Codeshloglevel' in keyvalues[1:]:
                                codeshloglevel = int(keyvalues[2])
                            elif 'Statelevel' in keyvalues[1:]:
                                statelevel = int(keyvalues[2])
                            elif 'Debuglevel' in keyvalues[1:]:
                                debuglevel = int(keyvalues[2])
                            elif 'Cleanpath' in keyvalues[1:]:
                                cleanpath = int(keyvalues[2])
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

                logfile = open(logdir + '/' + LogFile.logfname,'r') 
                for line in logfile.readlines():
                    os.chdir(State.initialdir)
                    shortline = line[:-1]  # strip '\n'
                    words = shortline.split()
                    if words[0][0] == '#':
                        print("Comment is: ",shortline)
                        continue
                    if shortline.find("Macro:") >= 0:
                        print(shortline)
                    else:
                        print("Command is: " + shortline)
                    if shortline.find("Macro:") >= 0:
                        if option[0] == 'c' or cavescommand == 'extract':  # complete - get macro sources
                            wordlist = shortline.split()
                            macrofile = wordlist[1]
                            # print "Macro is: ",macrofile
                            cvs('co -r' + tag + ' ' + macrodir +'/' + macrofile)
                            os.system('cp -f ' + macrodir + '/' + macrofile + ' ' + weweredir + '/' + macrofile)
                            if Repository.location.find(":pserver:") >= 0:  # make macro from pserver EXECUTABLE
                                os.chmod(weweredir + '/' + macrofile,0o744)
                            cvs('release -d ' + macrodir)
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
                                print("Problem in extracting on line: " + linenumber + " >>> " + shortline)
                logfile.close()
                # cvs('release -d ' + logdir)
             except extractException:
                print('Extract does NOT work for codesh log files')
                print(' (when codeshloglevel == 1 and the logfile')
                print(' contains a mix of shell and codesh commands)')
                print('To extract the tag re-start Codesh using batch mode')
                print('e.g. codesh.py -b < ' + tag +'.log')
             except configException:
                print('Configurations of the tag to be extracted')
                print('are different from the current configurations.')
                print('Extraction cannot proceed.')
                print('Copying the Configurations of the desired tag to ' + tagconffile)
                print('To extract the tag re-start Codesh using the -c option')
                print('e.g. codesh.py -c ' + tag + '.conf')
                print('and issue again the extract <tag> command.')
             except:
                print("Problem inspecting OR extracting Tag: " + tag)
            finally:
                os.chdir(State.initialdir)
                cvs('release -d ' + logdir)
        ### TAGCOPY ###
        elif cavescommand == 'tagcopy':
            os.chdir(weweredir)
            if len(parlist) < 2:
                print("The tagcopy syntax entered is wrong")
                print("tagcopy syntax is:")
                print("tagcopy <tag> <to> <from>")
                print("   if <from> is omitted then copy from CURRENT repository")
                return
            oldrepos = Repository.location
            sourcerepos = oldrepos
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
                # prepare destination repository
                os.system('mkdir tempdest')
                os.chdir('tempdest')
                Repository.location = destinationrepos
                cvs('co ' + logdir + '/dummy.file')
                cvs('co ' + macrodir + '/dummy.file')
                cvs('co ' + datdir + '/dummy.file')
                os.chdir(State.initialdir)
                Repository.location = sourcerepos
                cvs('co -r ' + tag + ' ' + logdir + '/' + LogFile.logfname)
                tagcopy(logdir + '/' + LogFile.logfname,tag,destinationrepos,sourcerepos)
                logfile = open(logdir + '/' + LogFile.logfname,'r')
                linenumber = 0
                for line in logfile.readlines():
                    os.chdir(State.initialdir)
                    shortline = line[:-1]  # strip '\n'
                    if shortline.find("Macro:") >= 0:
                        print(shortline)
                    else:
                        print("Command is: " + shortline)
                    if shortline.find("Macro:") >= 0:
                        wordlist = shortline.split()
                        macrofile = wordlist[1]  
                        # print "Macro is: ",macrofile
                        cvs('co -r' + tag + ' ' + macrodir +'/' + macrofile)
                        tagcopy(macrodir + '/' + macrofile,tag,destinationrepos,sourcerepos)
                        cvs('release -d ' + macrodir)
                logfile.close()
                cvs('release -d ' + logdir)
                os.system('rm -rf tempdest')
                Repository.location = oldrepos
            except:
                print("Wrong parameters for tagcopy:",parlist)
                Repository.location = oldrepos
        ### TAGDELETE ###
        elif cavescommand == 'tagdelete':
            os.chdir(weweredir)
            if len(parlist) < 1:
                print("The tagdelete syntax entered is wrong")
                print("tagdelete syntax is:")
                print("tagdelete <tag> <in_repository>")
                return
            targetrepository = Repository.location
            try:
                tag = parlist[0]
                if len(parlist) > 1:
                   targetrepository = parlist[1] 
                   flag = checkRepo(targetrepository)
                   if flag == 1: return
                s = input("You are about to delete tag: " + tag + " from " + targetrepository  + " (Y/N) ?: ")
                if s:
                    if s != 'Y':
                        print("You did not reply Y => aborting tagdelete")
                        return
                os.system('mkdir tempdir')
                os.chdir('tempdir')
                cvs('co -r ' + tag + ' ' + logdir)
                cvs('co -r ' + tag + ' ' + macrodir)
                cvs('co -r ' + tag + ' ' + datdir)
                cvs('tag -d ' + tag + ' ' + logdir)
                cvs('tag -d ' + tag + ' ' + macrodir)
                cvs('tag -d ' + tag + ' ' + datdir)
                os.chdir(State.initialdir)
                os.system('rm -rf tempdir')
            except:
                print("Wrong parameters for tagdelete:",parlist)
        ### TAKESNAPSHOT ###
        elif cavescommand == 'takesnapshot':
            os.chdir(weweredir)
            if len(parlist) < 1:
                print("The takesnapshot syntax entered is wrong")
                print("takesnapshot syntax is:")
                print("takesnapshot <tag>")
                return
            try:
                tag = parlist[0]
                if len(parlist) > 1:
                    annotation = " ".join(parlist[1:])
                else:
                    annotation = " "
                cvs('import -kb -m "' + annotation + '" ' + 'snapshots/' + tag + ' ' + tag + ' ' + 'tag1')
                cvs('co snapshots/snaplist.txt')
                listFile = open('snapshots/snaplist.txt', "a")
                listFile.write(tag + '\n')
                listFile.close()
                cvs('update -A snapshots/snaplist.txt')
                addcommittag('snapshots/snaplist.txt',"",tag)  
            except:
                print("Error taking snapshot")
        ### GETSNAPSHOT ###
        elif cavescommand == 'getsnapshot':
            os.chdir(weweredir)
            if len(parlist) < 1:
                print("The getsnapshot syntax entered is wrong")
                print("getsnapshot syntax is:")
                print("getsnapshot <tag>")
                return
            try:
                tag = parlist[0]
                cvs('co -kb -d ' + tag + ' snapshots/' + tag)
            except:
                print("Error getting snapshot")
        else:
            print('Unknown codesh command: ' + cavescommand)

# go back to current dir
    os.chdir(weweredir)

