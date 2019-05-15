#!/usr/bin/env python2
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
 
import cmd, os, string, sys, shutil, commands
import re
from vstate import *
from subprocess import Popen,PIPE,STDOUT

def writetologfile(line):
    LogFile.logfile.write(line + '\n')
    LogFile.fulllogfile.write('\n>>> ' + line + '\n')

def getUniqueID():
    cmdline = "date --iso-8601='minutes' -u"
    for line in os.popen(cmdline).readlines():
        shortline = line[:-1]  # strip '\n'
        id = Options.userID + '-' + shortline[0:4]+shortline[5:7]+shortline[8:10]+'-'+shortline[11:13]+shortline[14:16]
    return id        

def checkParameters(wordlist):
   command = wordlist[0]
   length = len(wordlist) - 1
   
   commandDict = {'extract':['1','20'],
                  'browse':['0','2'],
                  'inspect':['1','2'],
                  'log':['1','15'],
                  'record':['1','1'],
                  'getsnapshot':['1','1'],
                  'takesnapshot':['1','15'],
                  'tagcopy':['2','3'],
                  'tagdelete':['1','2']
                 }

   if not (command in commandDict):
      return 1
 
   if length == 0:
      if string.atoi(commandDict[command][0]) == 0:
         return 1
      print "Command >> " + command + " << needs at least " + commandDict[command][0] + " parameters. Please retry."
      return 0           
  
   if length < string.atoi(commandDict[command][0]):
      print "You entered command >> " + command + " << with lesser number of parameters than the " + commandDict[command][0] + " needed. Please retry."
      return 0

   if length > string.atoi(commandDict[command][1]):
      print "You entered command >> " + command + " << with more parameters than the " + commandDict[command][0] + " allowed. Please retry."
      return 0
 
   return 1

def getUniqueIDsec():
    # down to the second
    cmdline = "date --iso-8601='seconds' -u"
    for line in os.popen(cmdline).readlines():
        shortline = line[:-1]  # strip '\n'
        id = Options.userID + '-' + shortline[0:4]+shortline[5:7]+shortline[8:10]+'-'+shortline[11:13]+shortline[14:16]+shortline[17:19]
    return id        


# inherits from cmd.Cmd
class CollaborativeShell(cmd.Cmd):
    # we extend this method
    def parseline(self, line):
        line = line.strip()
        wordlist = string.split(line)
        if len(wordlist) > 0:
            indexeq0 = string.find(wordlist[0],"=")
        else:
            indexeq0 = 0
        if Options.debuglevel > 1: print "==> Input line: " + line
        # print line[0], line[:1], line[:2], line [:3]
        # DB -> list all known commands OR delegate to shell thru do_run

        if len(wordlist) > 0:
           flagPar = checkParameters(wordlist)
           if flagPar == 0:  # return if the parameters given to the command are insufficient or extra
               return None, None, line

        if not line:
            return None, None, line
        # basics
        elif wordlist[0] == 'EOF':
            pass
        elif wordlist[0] == '?':
            line = 'help ' + line[1:]
        elif wordlist[0] == 'help':
            pass
        # execution environmenmt
        elif wordlist[0] == '>':
            if hasattr(self, 'do_shell'):
                line = 'shell ' + line[1:]
            else:
                return None, None, line
        # CODESH commands
        elif wordlist[0] == 'browse':
            pass
        elif wordlist[0] == 'log':
            pass
        elif wordlist[0] == 'tagcopy':
            pass
        elif wordlist[0] == 'tagdelete':
            pass
        elif wordlist[0] == 'inspect':
            pass
        elif wordlist[0] == 'extract':
            pass
        elif wordlist[0] == 'takesnapshot':
            pass
        elif wordlist[0] == 'getsnapshot':
            pass
        elif wordlist[0] == 'getenv':
            pass
        elif wordlist[0] == 'getalias':
            pass
        # implement some shell fuctionality to keep state between commands
        elif wordlist[0] == 'cd':
            pass
        elif wordlist[0] == 'up':
            pass
        elif wordlist[0] == 'setenv':
            pass
        elif wordlist[0] == 'export':
            pass
        elif wordlist[0] == 'record':
            pass
        # implement shell variable commands:
        #    set variable=value   /tcsh/   OR
        #    variable=value   /bash/
        elif wordlist[0] == 'set':
            line = string.replace(line,"set","export",1)
        elif indexeq0 > 0:
            line = "export " + line
        # delegate to shell
        else:
            line = 'run ' + line
        i, n = 0, len(line)
        while i < n and line[i] in self.identchars: i = i+1
        cmd, arg = line[:i], line[i:].strip()
        return cmd, arg, line

    # we extend this method
    def emptyline(self):
        return None

    def help_help(self):
        print "Two forms ==> help <COMMAND>  OR  ? <COMMAND>"

    def do_EOF(self, line):
        """ The do_EOF command is called when the user presses Ctrl-D (unix)
            or Ctrl-Z (Windows). """
        print " "
        LogFile.logfile.close()
        LogFile.fulllogfile.close()
        sys.exit()

    def help_cd(self):
        print "cd <dir>: change to directory"

    def do_cd(self, dirname):
        if Options.loglevel > 0:
            envset()
            fnenv = State.envfname
        # 'cd' by itself OR 'cd ~' means 'go home'
        if dirname == '' or dirname == '~':
            localdirname = os.environ['HOME']
        # 'cd -' means 'go to previous dir'
        elif dirname == '-':
            localdirname = State.olddir
        # 'cd ..' means 'go to upper dir'
        elif dirname == '..':
            localdirname = string.join(string.split(os.getcwd(),'/')[:-1],'/')
            if localdirname == '': localdirname = '/'
        # expand shell variables if present
        elif dirname[0] == '$':
            if len(dirname) > 1:
                shvarname = dirname[1:]
                if shvarname in State.envdict.keys():
                    localdirname = State.envdict[shvarname]
                else:  # sorry - undefined variable
                    localdirname = os.getcwd() # do nothing
            else:  # just a $ is not very helpful
                localdirname = os.getcwd() # do nothing
        else: 
		# directory names specified in quotes are modified
                # to correct the directory name
		if dirname[0] == '"':
			dirname = dirname.replace("\"","")
		localdirname = dirname
        # now DO cd
        State.olddir = os.getcwd()
        if os.path.isdir(localdirname):
            os.chdir(localdirname)
        else:
            print "%s: no such directory exists" % localdirname
            return
        State.curdir = os.getcwd()
        cmdline = "cd " + dirname
        if Options.batchmode == 1: print "==> " + cmdline
        writetologfile(cmdline)
        if Options.loglevel > 0:
            cmdline = "env > " + fnenv
            os.system(cmdline)
            envsnap(fnenv)
        if Options.loglevel == 3: trackchanges()

    def help_up(self):
        print "up: change to directory ABOVE current dir"

    def do_up(self, line):
        if Options.loglevel > 0:
            envset()
            fnenv = State.envfname
        # up == 'cd ..' means 'go to upper dir'
        dirname = string.join(string.split(os.getcwd(),'/')[:-1],'/')
        if dirname == '': dirname = '/'
        # now DO cd
        State.olddir = os.getcwd()
        os.chdir(dirname)
        State.curdir = os.getcwd()
        cmdline = "cd .."
        if Options.batchmode == 1: print "==> " + cmdline
        writetologfile(cmdline)
        if Options.loglevel > 0:
            cmdline = "env > " + fnenv
            os.system(cmdline)
            envsnap(fnenv)
        if Options.loglevel == 3: trackchanges()

    def help_setenv(self):
        print "setenv <VARIABLE> <value>: set environment variables"

    def do_setenv(self, varvaluepair):
        indexeq = string.find(string.lstrip(varvaluepair)," ")
        if indexeq > 0:
            var = varvaluepair[0:indexeq]
            value = varvaluepair[indexeq+1:]
            # deal with shell command expansion
            if value[0] == "`":
                expanded = []
                command = "echo "+value
                for line in os.popen(command).readlines():
                    shortline = line[:-1]
                    expanded.append(shortline)
                value = expanded[0]
            envadd(var,value)
        else:
            print "COMMAND has the form => setenv <VARIABLE> <value>"
            return
        if Options.shell == "bash":
            historyline = "export " + var + "=" + value
        if Options.shell == "tcsh":
            historyline = "setenv " + var + " " + value
        if Options.batchmode == 1: print "==> " + historyline
        writetologfile(historyline)

    def help_export(self):
        print "export <VARIABLE>=<value>: set environment variables"

    def do_export(self, varvaluepair):
        indexeq = string.find(varvaluepair,"=")
        if indexeq > 0:
            var = varvaluepair[0:indexeq]
            value = varvaluepair[indexeq+1:]
            # deal with shell command expansion
            if value[0] == "`":
                expanded = []
                command = "echo "+value
                for line in os.popen(command).readlines():
                    shortline = line[:-1]
                    expanded.append(shortline)
                value = expanded[0]
            envadd(var,value)
        else:
            print "COMMAND has the form => export <VARIABLE>=<value>"
            return
        if Options.shell == "bash":
            historyline = "export " + var + "=" + value
        if Options.shell == "tcsh":
            historyline = "setenv " + var + " " + value
        if Options.batchmode == 1: print "==> " + historyline
        writetologfile(historyline)

    def help_set(self):
        print "set <VARIABLE>=<value>: set shell variables"
        print "OR JUST <VARIABLE>=<value>: set shell variables"

    def help_getenv(self):
        print "getenv <VARIABLE>: get value for an environment variable (ALL if omitted)"

    def do_getenv(self, variable):
        envprint(variable)

    def help_getalias(self):
        print "getalias <ALIAS>: get value for an alias (ALL if omitted)"

    def do_getalias(self, variable):
        aliasprint(variable)

    def help_run(self):
        print "<command>: run a command in the default shell"

    def do_run(self, cmdline):
        # Replacing all the single quotes with double quotes
        cmdline = re.sub("'",'"',cmdline)
        wordlist = string.split(cmdline)
        # Parse lines beginning with # :
        #    key-value pairs in configuration files OR comments
        if wordlist[0][0] == '#':
             if Options.configfile == "":
                keyvalues = wordlist[1:]
                if len(keyvalues) > 2:
                    print 'Error while parsing file of input commands.'
                    print '  Keyvalues > 2: '
                    print keyvalues
                    return
                if 'Repository' in keyvalues:
                    Repository.location = keyvalues[1]
                    Repository.flag = 1
                elif 'Subshell' in keyvalues:
                    Options.shell = keyvalues[1]
                elif 'Loglevel' in keyvalues:
                    Options.loglevel = string.atoi(keyvalues[1])
                elif 'Codeshloglevel' in keyvalues:
                    Options.codeshloglevel = string.atoi(keyvalues[1])
                elif 'Statelevel' in keyvalues:
                    Options.statelevel = string.atoi(keyvalues[1])
                elif 'Debuglevel' in keyvalues:
                    Options.debuglevel = string.atoi(keyvalues[1])
                elif 'CleanPath' in keyvalues:
                    Options.cleanpath = string.atoi(keyvalues[1])
                elif 'UserID' in keyvalues:
                    Options.userID = keyvalues[1]
                elif 'GroupID' in keyvalues:
                    Options.groupID = keyvalues[1]
                elif 'MysqlHostname' in keyvalues:   
                    Options.mysqlhost = keyvalues[1]
                elif 'MysqlUsername' in keyvalues:   
                    Options.mysqluser = keyvalues[1]
                elif 'MysqlPassword' in keyvalues:   
                    Options.mysqlpass = keyvalues[1]
             return
        # do nothing if line begins with  Macro:
        if wordlist[0] == 'Macro:':
            print cmdline
            return
        # automatically detect macro files with extensions
        # in extensions list (e.g. .py, .sh, .csh etc)
        # default is NO automatic detection
        macroname = " "
        if len(Options.extensionlist) > 0:
            for ext in Options.extensionlist:
                if string.find(wordlist[0],ext) >= 0:
                    macroname = string.replace(wordlist[0], "./", "", 1)
                    writetologfile("Macro: " + macroname)
                    if string.find(wordlist[0],"./") == -1:
                        cmdline = "./"+cmdline
                    break

        if (wordlist[0] == "source" or wordlist[0] == "."):
            if len(wordlist)>1:
                macroname = wordlist[1]
                writetologfile("Macro: " + macroname)
            else:
                print "No Parameters given to: " + wordlist[0]
                # print len(wordlist)

        # automatically detect tracked files (with tracked extensions) in tracked list,
        #   which fall outside the scope of extensions list
        #   i.e. do not follow after '. ' or 'source ' or './'
        # default is NO automatic detection
        if len(Options.trackedlist) > 0:
            for ext in Options.trackedlist:
               for entry in wordlist:
                  if string.find(entry,ext) >= 0:
                     trackedname = entry
                     if trackedname == macroname:   # avoid duplications with extensions list
                        continue
                     else:
                        writetologfile("Macro: " + trackedname)

        writetologfile(cmdline)
        historyline = cmdline

        if Options.shell == "bash":
            prolog = "/bin/bash -c '"
            clobber = "|"
            if Options.loglevel >= 2:
                fnal = State.aliasfname
                prolog = prolog + ". " + fnal + "; "
                cmdline = aliasdo(cmdline)
        else:
            prolog = "/bin/tcsh -c '"
            clobber = "!"
            if Options.loglevel >= 2:
                fnal = State.aliasfname
                prolog = prolog + "source " + fnal + "; "
                cmdline = aliasdo(cmdline)
        if Options.loglevel > 0:
            envset()
            fnenv = State.envfname

        # propagate aliases
        newwordlist = string.split(cmdline)
        wordlist[0] = newwordlist[0]

        # deal with running in the background
        background = -1
        background = cmdline.count("&")
        if background > 0: cmdline = cmdline.replace("&","")
        # do not run "eval" in the background
        if wordlist[0] == 'eval': background = -1

        # option 1 - using tee (more "interactive")
        if wordlist[0] in Options.teeList or background > 0:
            idsec = getUniqueIDsec()
            tempfname = 'store-one-command-output.' + idsec
            if Options.debuglevel > 2: print "==> Command output goes to: ", tempfname
            cmdline = cmdline + " | tee " + tempfname

        # deal with running in the background
        if background > 0: cmdline = cmdline + " &"

        if Options.loglevel == 0:
            cmdline = prolog + cmdline + " '"
        elif Options.loglevel == 1:
            cmdline = prolog + cmdline + " ; env >" + clobber + " " + fnenv + " '"
        elif Options.loglevel >= 2:
            cmdline = prolog + cmdline + " ; env >" + clobber + " " + fnenv + " ; alias >" + clobber + " " + fnal + " '"

        # if to run in the background
        if background > 0 and Options.shell == "bash":
            cmdline = cmdline.replace("& ;","& ")
        if Options.debuglevel > 2: print "==> Will do: " + cmdline
        if Options.batchmode == 1: print "==> " + historyline
        
        # execute this if the command is present in the teeList OR is sent to the background
        # option 1 - using tee (more "interactive")
        if wordlist[0] in Options.teeList or background > 0:
            os.system(cmdline)
        else:
        # execute this if the command is not present in the teeList
        # option 2 - using popen (more "command-like")
           # 2.5 (stdin, stdouterr) = os.popen4(cmdline,'t')
           p = Popen(cmdline, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
           (stdin, stdouterr) = (p.stdin, p.stdout)
           for line in stdouterr.readlines():
               shortline = line[:-1]  # strip '\n'
               print shortline
               LogFile.fulllogfile.write(line)

        timespent = 0
        timemax = 2  # sec in the background before moving on
        if background > 0:
            while not os.path.isfile(tempfname):
                os.system("sleep 1")
                timespent = timespent + 1
                if timespent >= timemax:
                    print "==> Continue running in the background for command: " + cmdline
                    break
        if (background > 0 and timespent < timemax) or wordlist[0] in Options.teeList:
            tempfile = open(tempfname,'r')
            for line in tempfile.readlines():
                shortline = line[:-1]  # strip '\n'
                LogFile.fulllogfile.write(line)
            tempfile.close()
            os.remove(tempfname)

        if Options.loglevel > 0:  envsnap(fnenv)
        if Options.loglevel >= 2: aliassnap(fnal)
        if Options.loglevel == 3: trackchanges()

    def help_shell(self):
        print "> <command>: run a command (Script) in special interactive shell"
        print "=> The source code of the Script is AUTOMATICALLY stored"
        print "=> by the system when the user logs the session."

    def do_shell(self, cmdline):
        # Replacing all the single quotes with double quotes
        cmdline = re.sub("'",'"',cmdline)
        # treated as Exe files by default
        wordlist = string.split(cmdline)
        macroname = wordlist[0]
        writetologfile('Macro: ' + macroname)
        macrohere = './'+wordlist[0]
        cmdline = string.replace(cmdline,wordlist[0],macrohere)

        # automatically detect tracked files (with tracked extensions) in tracked list
        # default is NO automatic detection
        if len(Options.trackedlist) > 0:
            for ext in Options.trackedlist:
               for entry in wordlist:
                  if string.find(entry,ext) >= 0:
                     trackedname = entry
                     if trackedname == macroname:   # avoid duplications with extensions list
                        continue
                     else:
                        writetologfile("Macro: " + trackedname)

        writetologfile(cmdline)
        historyline = cmdline

        # default is option 2 - using popen (more "command-like")
        if Options.shell == "bash":
            prolog = "/bin/bash -c '"
            clobber = "|"
            if Options.loglevel >= 2:
                fnal = State.aliasfname
                prolog = prolog + ". " + fnal + "; "
                cmdline = aliasdo(cmdline)
        else:
            prolog = "/bin/tcsh -c '"
            clobber = "!"
            if Options.loglevel >= 2:
                fnal = State.aliasfname
                prolog = prolog + "source " + fnal + "; "
                cmdline = aliasdo(cmdline)

        # propagate aliases
        newwordlist = string.split(cmdline)
        wordlist[0] = newwordlist[0]

        if Options.loglevel > 0:
            envset()
            fnenv = State.envfname

        # option 1 - using tee (more "interactive")
        if wordlist[0] in Options.teeList:
            idsec = getUniqueIDsec()
            tempfname = 'store-one-command-output.' + idsec
            if Options.debuglevel > 2: print "==> Command output goes to: ", tempfname
            cmdline = cmdline + " | tee " + tempfname

        if Options.loglevel == 0:
            cmdline = prolog + cmdline + " '"
        elif Options.loglevel == 1:
            cmdline = prolog + cmdline + " ; env >" + clobber + " " + fnenv + " '"
        elif Options.loglevel >= 2:
            cmdline = prolog + cmdline + " ; env >" + clobber + " " + fnenv + " ; alias >" + clobber + " " + fnal + " '"
        if Options.debuglevel > 2: print "==> Will do: " + cmdline
        if Options.batchmode == 1: print "==> " + historyline

        # execute this if the command is present in the teeList OR is sent to the background
        # option 1 - using tee (more "interactive")
        if wordlist[0] in Options.teeList:
           os.system(cmdline)           
        else:	
        # execute this if the command is not present in the teeList
        # option 2 - using popen (more "command-like")
           # 2.5.(stdin, stdouterr) = os.popen4(cmdline,'t')
           p = Popen(cmdline, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
           (stdin, stdouterr) = (p.stdin, p.stdout)
           for line in stdouterr.readlines():
               shortline = line[:-1]  # strip '\n'
               print shortline
               LogFile.fulllogfile.write(line)

        if wordlist[0] in Options.teeList:
             tempfile = open(tempfname,'r')
             for line in tempfile.readlines():
                   shortline = line[:-1]  # strip '\n'
                   LogFile.fulllogfile.write(line)
             tempfile.close()
             os.remove(tempfname)

        if Options.loglevel > 0:  envsnap(fnenv)
        if Options.loglevel >= 2: aliassnap(fnal)
        if Options.loglevel == 3: trackchanges()


    def help_record(self):
        print "=> record <filename>: marks the file to be logged"
        print "=> The file is AUTOMATICALLY stored"
        print "=> by the system when the user logs the session."
        
    def do_record(self, cmdline):
        wordlist = string.split(cmdline)
        writetologfile('Macro: ' + wordlist[0])

    def help_browse(self):
        print "   browse has 2 forms:"
        print "browse <tag> <s>: browse info about a tag with optional search (s) option"
        print "      OR"
        print "browse <snap>: returns a list of existing snapshots"

    def do_browse(self, tag):
        print "==> browse <tag>:",tag
        if Options.codeshloglevel == 1:
            writetologfile('browse ' + tag)
        caves('browse', tag)

    def help_log(self):
        print "log <tag> <annotation>: log info about a tag with optional annotation"

    def do_log(self, line):
        id = getUniqueID()
        newline = id + '-' + line
        print "==> log <tag> <annotation>:",newline
        caves('log', newline)

    def help_takesnapshot(self):
        print "takesnaphot <tag> <annotation>: log the files and"
        print "   sub-directories of the current working directory"
        print "   with optional annotation"

    def do_takesnapshot(self, line):
        id = getUniqueID()
        newline = id + '-' + line
        print "==> takesnapshot <tag> <annotation>:",line
        cmd = 'du -k --max-depth=0'
        size = string.atoi(string.split(commands.getoutput(cmd))[0])
        if Options.debuglevel > 1: print "==> Size of directory for snapshot in kB is: ",size
        s = 'y'
        if size > 2048:
            print "==> Size of the snapshot exceeds 2048 kB."
            s = 'n'
            s = raw_input("Do you still want to take snapshot - y/n ?: ")        
        if s == 'y':
            currDir = os.getcwd()
            if currDir == Repository.location[:len(currDir)]:
                print "Sorry, the repository is below the current directory."
                print "Taking snapshot is impossible."
            else:
                print "Taking {" + `size` + "} kB snapshot of directory: " + currDir
                caves('takesnapshot', newline)

    def help_getsnapshot(self):
        print "getsnaphot <tag>: extract a previously stored snapshot"

    def do_getsnapshot(self, line):
        print "==> getsnapshot <tag>:",line
        if len(line) == 0:
           print ">>> No tag given. Cannot get snapshot."
           return
        newline, flag = getUniqueTag(line,"snap")
        if flag == 1:
           caves('getsnapshot', newline)
        else:
           print "Given tag/short-tag is not unique. Please re-execute"
           print " the command with a unique tag/short-tag."

    def help_tagcopy(self):
        print "tagcopy <tag> <to> <from>: copy tag to destination from source"
        print "   if <from> is omitted then copy from CURRENT repository"

    def do_tagcopy(self, line):
        print "==> tagcopy <tag> <to> <from>:",line
        if Options.codeshloglevel == 1:
            writetologfile('tagcopy ' + line)
        caves('tagcopy', line)

    def help_tagdelete(self):
        print "tagdelete <tag> <in_repository>: remove tag from repository"
        print "   if <in_repository> is omitted then from CURRENT repository"

    def do_tagdelete(self, line):
        print "==> tagdelete <tag> <in_repository>:",line
        if Options.codeshloglevel == 1:
            writetologfile('tagdelete ' + line)
        caves('tagdelete', line)

    def help_inspect(self):
        print "inspect <tag> <brief|complete>: get info about a tag"
        print "   AND optionally code of executed scripts (complete option)"

    def do_inspect(self, line):
        print "==> inspect <tag> <brief|complete>:",line
        if Options.codeshloglevel == 1:
            writetologfile('inspect ' + line)
        newline, flag = getUniqueTag(line,"tag")
        if flag == 1:
           caves('inspect', newline)
        else:
           print "Given tag/short-tag is not unique. Please re-execute"
           print " the command with a unique tag/short-tag."


    def help_extract(self):
        print "extract has two forms: reproduce OR modify+reproduce"
        print "extract <tag>: get info about a tag AND reproduce the"
        print "   virtual session"
        print "extract <tag> <option> <delimeter> <replacement_list>:"
        print "   get info about a tag, modify AND reproduce the"
        print "   virtual session e.g."
        print '     extract <tag> d / "red/blue"'
        print "        will change in all session commands red to blue and run"
        print '     extract <tag> file / redblue.converter'
        print "        will change in all session commands red to blue and run"
        print "             if the file redblue.converter contains a line"
        print '                   "red/blue"'
        print '   the " in "old1/new1" "old2/new2" ... are obligatory to'
        print "     separate several replacement groups (as many as the user"
        print "     wants); if the # of groups is too long use the file option"

    def do_extract(self, line):
        print "==> extract <tag>:",line
        if Options.codeshloglevel == 1:
            writetologfile('extract ' + line)
        newline, flag = getUniqueTag(line,"tag")
        if flag == 1:
           caves('extract', newline)
        else:
           print "Given tag/short-tag is not unique. Please re-execute"
           print " the command with a unique tag/short-tag."

if Repository.type == "ascii":
    from codeshbascii import *
elif Repository.type == "cvs":
    from codeshb import *
elif Repository.type == "svn":
    from codeshbsvn import *
else:   # default
    from codeshbascii import *


if __name__ == '__main__':  # runs only standalone, NOT when imported
    cmd.Cmd.prompt = DirectoryPrompt('')
#   sys.ps1 = DirectoryPrompt()
#   sys.ps2 = DirectoryPrompt('> ')
    shell = CollaborativeShell()
    shell.cmdloop()
