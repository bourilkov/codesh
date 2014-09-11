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
 
import cmd, os, string, sys, shutil
import re

class DirectoryPrompt:
    def __init__(self, subprompt='> '):
        self.linenumber = 0
        self.subprompt = subprompt
    def __repr__(self):
        self.linenumber = self.linenumber + 1
        if '-b' not in sys.argv:
            return os.getcwd()+' [%d] '%(self.linenumber)+self.subprompt
        else:
            return ''

class Repository:
    # flag:  0 Run without repository
    #        1 Repository set, not verified
    #        2 Repository set and verified == working
    flag = 0
    # default repository type
    # type = 'cvs'
    type = 'ascii'
    location = 'Repository.location NOT set => NO persistent logbooks!'
    locationtoinput = 'my repository location'
    # flag whether the repository is of type remote ASCII
    # username@hostname for the remote host on which the repository resides
    remoteAsciiUser = ''
    # location of the repository on the remote host
    remoteAsciiRepoLocation = ''

class Options:
    # Version
    #version = 'v0.1'
    version = 'CODESH_SA_2_0'
    # use MySQL database for annotations (0 - no/1 - yes)
    # no database by default
    configuremysql = '0'
    mysqlhost = ''
    mysqluser = ''
    mysqlpass = ''
    # User ID - 4 characters (default = 'user' as a generic placeholder)
    # individual users will benefit from personalization
    userID = 'user'
    # Group ID - 8 characters (default = 'testgrup' as a generic placeholder)
    # individual groups will benefit from personalization
    groupID = 'testgrup'
    #
    # loglevel:  0 - simple shell: no state kept
    #            1 - some sophistication: environment propagated
    #            2 - more sophistication: (1) & aliases propagated
    #            3 - XXXL sophistication: (2) & state changes displayed
    #loglevel = 0
    #loglevel = 1
    loglevel = 2
    #loglevel = 3
    #
    # codeshloglevel:  0 - NO codesh commands in logfiles
    #                  1 - INCLUDE codesh commands in logfiles
    codeshloglevel = 0
    #
    # statelevel:  0 - no INITIAL/FINAL state info
    #              1 - INITIAL/FINAL state info
    statelevel = 1
    #
    # debuglevel:  0 - no debug
    #              1 - some debug
    #              2 - max debug
    debuglevel = 0
    #debuglevel = 1
    #debuglevel = 2
    #
    # cleanpath: 0 - do nothing
    #            1 - eliminate duplicate paths (from lazy programmers!)
    #                applies to PATH and MANPATH
    cleanpath = 0
    if loglevel > 0: cleanpath = 1
    #
    # shell (tcsh OR bash /default/)
    shell = "default"
    #shell = "tcsh"
    shell = "bash"
    #
    # list of extensions: macro files with extensions in the
    # list are logged automatically by do_run command
    # empty by default if -c used i.e. NO automatic logging
    if '-c' in sys.argv:
        extensionlist = []
    else:
        # automatic by default for interactive mode: .py, .sh, .csh, .pl
        extensionlist = ['.py', '.sh', '.csh', '.pl']
        # extensionlist = ['.sh', '.csh', '.pl']

    #
    # tracked list: automatically store files with extensions in this list
    # empty by default
    # can be populated with a line in the config file e.g. Trackedlist .ext1/.ext2/.ext3  etc. /no spaces!/
    trackedlist = []

    # list of commands for option 1 - using tee (more "interactive")
    teeList = ["more","less","vi","vim","emacs","top","bash","tcsh","time","diff","cmsRun"]
    #
    print "******************************************"
    print "*                                        *"
    print "*             C O D E S H                *"
    print "*                                        *"
    print "*    COllaborative DEvelopment SHell     *"
    print "*                                        *"
    print "*     Conception: Dimitri Bourilkov      *"
    print "*                                        *"
    print "*         Lead developers:               *"
    print "*          Dimitri Bourilkov             *"
    print "*          Vaibhav Khandelwal            *"
    print "*          Sanket Totala                 *"
    print "*          Sharad Sonapeer               *"
    print "*                                        *"
    print "*        bourilkov@phys.ufl.edu          *"
    print "*                                        *"
    print "******************************************"
    #
    # The user can change options in several ways
    #

    # if -c ... config file is specified ... read from it
    # else
    #     chk if codesh.conf ... if yes read from it 
    #         else
    #           chk -b  ... if not present ask for options
    #           i.e. wait for user input when NOT in batch mode
    
    s = "n"
    configfile = ""
    if '-b' in sys.argv:
        batchmode = 1
    else:
        batchmode = 0
    if '-c' in sys.argv:
        i = 0
        while i < len(sys.argv) - 1:
            if sys.argv[i] == '-c':
               configfile = sys.argv[i+1]
               break
            i = i + 1
        if configfile == "":
            print 'Error ... Usage: python2 codesh.py [-c configfile] [-b]'
            print '  =============> you used -c BUT specified NO file'
        if not os.path.isfile(configfile):
            print "Error ... config file => " + configfile + " <= doesn't exist"
    else:
        filenames = os.listdir(".")
        if 'codesh.conf' in filenames:
            configfile = 'codesh.conf'
        else:
            if '-b' not in sys.argv:
               s = raw_input("Change defaults y/n ?: ")
            else:                                         # batch
               s = "n"

    if s == 'y':
        s = raw_input("Repository flag (0:no - 1:yes) => " + `Repository.flag` + " ?: ")
        if s: Repository.flag = string.atoi(s)
        if Repository.flag != 0:
           Repository.flag = 1
           s = raw_input("Repository type(ascii/cvs/svn) => " + Repository.type + " ?: ")
           if s: Repository.type = s
           s = raw_input("Repository => " + Repository.locationtoinput + " ?: ")
           if s: Repository.location = s
        s = raw_input("Default subshell (bash/tcsh) will be => " + shell + " ?: ")
        if s: shell = s
        s = raw_input("Loglevel (0:min - 3:max) => " + `loglevel` + " ?: ")
        if s: loglevel = string.atoi(s)
        s = raw_input("Codeshloglevel (0:min - 1:max) => " + `codeshloglevel` + " ?: ")
        if s: codeshloglevel = string.atoi(s)
        s = raw_input("Statelevel (0:min - 1:max) => " + `statelevel` + " ?: ")
        if s: statelevel = string.atoi(s)
        s = raw_input("Debuglevel (0:min - 3:max) => " + `debuglevel` + " ?: ")
        if s: debuglevel = string.atoi(s)
        s = raw_input("Cleanpath (0:no - 1:yes) => " + `cleanpath` + " ?: ")
        if s: cleanpath = string.atoi(s)
        s = raw_input("User ID (4 characters) => " + `userID` + " ?: ")
        if s:
            if len(s) > 4: userID = s[0:4]
            elif len(s) <= 4:
                userID = s
                if len(s) < 4:
                    for ki in range(len(s),4): userID = userID + "x"
        s = raw_input("Group ID (8 characters) => " + `groupID` + " ?: ")
        if s:
            if len(s) > 8: groupID = s[0:8]
            elif len(s) <= 8:
                groupID = s
                if len(s) < 8:
                    for ki in range(len(s),8): groupID = groupID + "x"
        configuremysql = raw_input("Configure MySQL (0:no - 1:yes) => " + `configuremysql` + " ?: ")
        # print configuremysql
        if configuremysql == '1': 
            s = raw_input("MySQL Hostname => " + `mysqlhost` + " ?: ")
            if s: mysqlhost = s 
            s = raw_input("MySQL Username => " + `mysqluser` + " ?: ")
            if s: mysqluser = s            
            #s = raw_input("MySQL Password => " + `mysqlpass` + " ?: ")
            #if s: mysqlpass = s 
            import getpass
            s = getpass.getpass("MySQL Password => " + `mysqlpass` + " ?: ")

    elif s == 'n' and configfile != "":
        try:          # to open/read config file
            conffile = open(configfile, "r")
            for line in conffile.readlines():
                wordlist = string.split(line)
                keyvalues = wordlist[1:]
                if len(keyvalues) > 2:
                    print 'Error while parsing config file:',configfile
                    print "Problem with config file: ",configfile
                    print "==== Will use default for non-changed options ===="
                    break
                if 'Repository' in keyvalues:
                    Repository.location = keyvalues[1]
                    Repository.flag = 1
                elif 'Repositorytype' in keyvalues:
                    Repository.type = keyvalues[1]
                elif 'Subshell' in keyvalues:
                    shell = keyvalues[1]
                elif 'Loglevel' in keyvalues:
                    loglevel = string.atoi(keyvalues[1])
                elif 'Codeshloglevel' in keyvalues:
                    codeshloglevel = string.atoi(keyvalues[1])
                elif 'Statelevel' in keyvalues:
                    statelevel = string.atoi(keyvalues[1])
                elif 'Debuglevel' in keyvalues:
                    debuglevel = string.atoi(keyvalues[1])
                elif 'CleanPath' in keyvalues:
                    cleanpath = string.atoi(keyvalues[1])
                elif 'UserID' in keyvalues:
                    userID = keyvalues[1]
                elif 'GroupID' in keyvalues:
                    groupID = keyvalues[1]
                elif 'MysqlHostname' in keyvalues:   
                    mysqlhost = keyvalues[1]
                elif 'MysqlUsername' in keyvalues:   
                    mysqluser = keyvalues[1]
                elif 'MysqlPassword' in keyvalues:   
                    mysqlpass = keyvalues[1]
                elif 'Extensionlist' in keyvalues:   
                    extensionlist = string.split(keyvalues[1],'/')
                elif 'Trackedlist' in keyvalues:   
                    trackedlist = string.split(keyvalues[1],'/')
            conffile.close()
        except:       # problem => stick to defaults
            print "Problem with config file: ",configfile
            print "==== Will use default for non-changed options ===="

    # check whether the repository is of type remote ASCII
    if Repository.type == 'ascii' and string.find(Repository.location,"@") > 0:
        [Repository.remoteAsciiUser, Repository.remoteAsciiRepoLocation] = string.split(Repository.location,':')

    if Repository.type != 'ascii' and Repository.type != 'cvs' and Repository.type != 'svn': Repository.type = 'ascii' # default
    if shell != "bash" and shell != "tcsh": shell = "bash"
    if loglevel < 0 or loglevel > 3: loglevel = 3
    if codeshloglevel < 0 or codeshloglevel > 1: codeshloglevel = 0
    if statelevel < 0 or statelevel > 1: statelevel = 1
    if debuglevel < 0 or debuglevel > 3: debuglevel = 0
    if cleanpath < 0 or cleanpath > 1: cleanpath = 0
    if loglevel > 0: cleanpath = 1
    print "******************************************"
    print "*                                        *"
    print "*  Type help OR ? at the command prompt  *"
    print "*   to get a full list of commands or    *"
    print "*    help about individual commands      *"
    print "*                                        *"
    print "*  To EXIT just type the usual ctrl-D    *"
    print "*                                        *"
    print "******************************************"
    print "==> Starting CODESH:  version = " + version
    print "==> with '" + Repository.type + "' repository: " + Repository.location
    print "==> Default subshell: " + shell
    print "==> Loglevel   = ", loglevel
    if loglevel == 0:
        print "     simple shell: no state kept"
    elif loglevel == 1:
        print "     some sophistication: environment propagated"
    elif loglevel == 2:
        print "     more sophistication: environment & aliases propagated"
    elif loglevel == 3:
        print "     XXXL sophistication:"
        print "     environment & state changes propagated and displayed"
    print "==> Codeshloglevel   = ", codeshloglevel
    if codeshloglevel == 0:
        print "     NO codesh commands in logfiles"
    elif codeshloglevel == 1:
        print "     INCLUDE codesh commands in logfiles"
    print "==> Statelevel   = ", statelevel
    if statelevel == 0:
        print "     no INITIAL/FINAL state info"
    elif statelevel == 1:
        print "     INITIAL/FINAL state info"
    print "==> Debuglevel = ", debuglevel
    if debuglevel == 0:
        print "     no debug"
    elif debuglevel == 1:
        print "     some debug"
    elif debuglevel == 2:
        print "     max debug"
    elif debuglevel == 3:
        print "     max++ debug"
    print "==> Cleanpath  = ", cleanpath
    if cleanpath == 0:
        print "     do nothing"
    elif cleanpath == 1:
        print "     eliminate duplicate paths (from lazy programmers!)"
        print "     applies to PATH and MANPATH"
        print "     if loglevel > 0 cleanpath is AUTOMATICALLY set to 1"
    if mysqlhost != '':
        print "==> Will use SQL server <=="
        print "     MySQL Hostname => ",mysqlhost
        print "     MySQL Username => ",mysqluser
    print "==> UserID =",userID         
    print "==> GroupID =",groupID

class LogFile:
    logfname = 'mylog.1'
    fulllogfname = 'myfulllog.1'
    logfile = open(logfname,'w')

    logfile.write('# Repository ' + Repository.location + '\n')
    logfile.write('# Repositorytype ' + Repository.type + '\n')
    logfile.write('# Subshell ' + Options.shell + '\n')
    logfile.write('# Loglevel ' + str(Options.loglevel) + '\n')
    logfile.write('# Codeshloglevel ' + str(Options.codeshloglevel) + '\n')
    logfile.write('# Statelevel ' + str(Options.statelevel) + '\n')
    logfile.write('# Debuglevel ' + str(Options.debuglevel) + '\n')
    logfile.write('# Cleanpath '  + str(Options.cleanpath) + '\n')

    fulllogfile = open(fulllogfname,'w')

class State:
    # initial directory
    initialdir = os.getcwd()
    # working directory
    curdir = os.getcwd()
    olddir = curdir

    # environment variables in a dictionary AND file
    if Options.shell == "bash":
        envfname = initialdir + '/store-env-output.sh'
        if Options.statelevel == 1:
            envfnameinit  = 'env-initial.sh'
            envfnamefinal = 'env-final.sh'
        cmdline = "/bin/bash -c 'env >| " + envfname + "'"
    else:
        envfname = initialdir + '/store-env-output.csh'
        if Options.statelevel == 1:
            envfnameinit  = 'env-initial.csh'
            envfnamefinal = 'env-final.csh'
        cmdline = "/bin/tcsh -c 'env >! " + envfname + "'"
    os.system(cmdline)
    envdict = {}
    tempenvvarkeys = os.environ.keys() # returns an unsorted list of keys in the dict
    tempenvvarkeys.sort()
    envvarkeys = [] # global - start empty and fill below
    # omit irrelevant variables
    vetolist = ["SHLVL","LINES","COLUMNS","MACHTYPE","HOSTTYPE","OSTYPE","PS1","_"]
    for key in tempenvvarkeys:         # store key, value pairs
        if not key in vetolist:
            # omit irrelevant variables
            envvarkeys.append(key)
            envdict[key] = os.environ[key]
    envvarkeys.sort()
    if Options.loglevel == 3:
        envfnameold = envfname + '.old'
        shutil.copy2(envfname,envfnameold)
        if Options.statelevel == 1:
            shutil.copy2(envfname,envfnameinit)

    # aliases in a dictionary AND file
    if Options.shell == "bash":
        aliasfname = initialdir + '/store-alias-output.sh'
        if Options.statelevel == 1:
            aliasfnameinit  = 'alias-initial.sh'
            aliasfnamefinal = 'alias-final.sh'
        #cmdline = '/bin/bash -c "alias >| ' + aliasfname + '"'
        if (os.path.isfile(os.environ['HOME']+"/.bashrc") != 0):
            cmdline = "/bin/bash -c 'BASH_ENV=$HOME/.bashrc;. $BASH_ENV;alias >|" + aliasfname + "'"
        else:
            cmdline = "/bin/bash -c 'alias >|" + aliasfname + "'"
    else:
        aliasfname = initialdir + '/store-alias-output.csh'
        if Options.statelevel == 1:
            aliasfnameinit  = 'alias-initial.csh'
            aliasfnamefinal = 'alias-final.csh'
        #cmdline = '/bin/tcsh -c "alias >! ' + aliasfname + '"'
        cmdline = "/bin/tcsh -c 'alias >! " + aliasfname + "'"

    os.system(cmdline)

    aliasdict = {}
    # omit irrelevant aliases
    aliasvetolist = ["mc","which","pp","rs","terminal","nman"]
    tempfile = open(aliasfname,'r')
    if Options.shell == "tcsh":
        aliasfnamecsh = aliasfname + "-torun"
        cshfile = open(aliasfnamecsh,'w')
        L = []
        for line in tempfile.readlines():
            shortline = line[:-1]  # strip '\n'
            indexal = string.find(shortline,"\t")
            alias = shortline[0:indexal]
            content = shortline[indexal+1:]
            if not alias in aliasvetolist:
                L.append('alias ' + alias + ' "' + content + '"\n')
                if Options.debuglevel > 0: print 'alias ' + alias + ' "' + content + '"'
                aliasdict[alias] = content
        cshfile.writelines(L)
        cshfile.close()
        tempfile.close()
        os.system("rm -f " + aliasfname)
        os.system("mv -f " + aliasfnamecsh + " " + aliasfname)
    if Options.shell == "bash":
        for line in tempfile.readlines():
            shortline = line[:-1]  # strip '\n'
            indexal = string.find(shortline,"=")
            wordlist = string.split(shortline[0:indexal])
            alias = wordlist[1]
            content = shortline[indexal+1:]
            # taking out all the single quotes
            content = re.sub("'","",content)
            if not alias in aliasvetolist:
                if Options.debuglevel > 0: print 'alias ' + alias + ' "' + content + '"'
                aliasdict[alias] = content
        tempfile.close()
    aliaskeys = aliasdict.keys()
    aliaskeys.sort()
    if Options.loglevel == 3:
        aliasfnameold = aliasfname + '.old'
        shutil.copy2(aliasfname,aliasfnameold)
        if Options.statelevel == 1:
            shutil.copy2(aliasfname,aliasfnameinit)

def curdirset(newdir=''):
    # 'cd' by itself means 'go home'
    if newdir == '': newdir = os.environ['HOME']
    State.curdir = newdir

def curdirget():
    return State.curdir

def curdirprint():
    print 'Current directory \t', State.curdir

def envset():
    for key in State.envvarkeys:         # set key, value pairs
        os.environ[key] = State.envdict[key]

def envadd(newkey,newval):
    State.envdict[newkey] = newval
    State.envvarkeys = State.envdict.keys()
    State.envvarkeys.sort()
    os.environ[newkey] = newval

def envget():
    State.envvarkeys = os.environ.keys()
    State.envvarkeys.sort()
    for key in State.envvarkeys:         # get key, value pairs
        State.envdict[key] = os.environ[key]

def envsnap(envfname):
    tempfile = open(envfname,'r')
    newfname = envfname + "-temp"
    newfile = open(newfname,'w')
    L = []
    for line in tempfile.readlines():
        shortline = line[:-1]  # strip '\n'
        indexal = string.find(shortline,"=")
        variable = shortline[0:indexal]
        value = shortline[indexal+1:]
        if variable == 'PATH' or variable == 'MANPATH':
            if Options.cleanpath == 1:
                dirtypath = value
                pathlist = string.split(dirtypath,":")
                if len(pathlist) > 0:
                    cleanpath = ''
                    cleanpathlist = []
                    for path in pathlist:
                        if path not in cleanpathlist:
                            cleanpathlist.append(path)
                            cleanpath = cleanpath + path + ':'
                    cleanpath = cleanpath[:-1] # strip last :
                    value = cleanpath
                    if variable == 'PATH': os.environ['PATH'] = cleanpath
                    if variable == 'MANPATH': os.environ['MANPATH'] = cleanpath
        # omit irrelevant variables
        if not variable in State.vetolist:
            L.append(variable + '=' + value + '\n')
            State.envdict[variable] = value
    State.envvarkeys = State.envdict.keys()
    State.envvarkeys.sort()
    tempfile.close()
    newfile.writelines(L)
    newfile.close()
    os.system("rm -f " + envfname)
    os.system("mv -f " + newfname + " " + envfname)

def envprint(variable=''):
    for key in State.envvarkeys:         # print key, value pairs
        if variable == '':
            print key, '\t', State.envdict[key]
        elif key == variable:
            print key, '\t', State.envdict[key]

def aliasadd(newkey,newval):
    State.aliasdict[newkey] = newval
    State.aliaskeys = State.aliasdict.keys()
    State.aliaskeys.sort()

def aliassnap(aliasfname):
    tempfile = open(aliasfname,'r')
    if Options.shell == "tcsh":
        aliasfnamecsh = aliasfname + "-torun"
        cshfile = open(aliasfnamecsh,'w')
        L = []
        for line in tempfile.readlines():
            shortline = line[:-1]  # strip '\n'
            indexal = string.find(shortline,"\t")
            alias = shortline[0:indexal]
            content = shortline[indexal+1:]
            if not alias in State.aliasvetolist:
                L.append('alias ' + alias + ' "' + content + '"\n')
                State.aliasdict[alias] = content
        cshfile.writelines(L)
        cshfile.close()
        tempfile.close()
        os.system("rm -f " + aliasfname)
        os.system("mv -f " + aliasfnamecsh + " " + aliasfname)
    if Options.shell == "bash":
        for line in tempfile.readlines():
            shortline = line[:-1]  # strip '\n'
            indexal = string.find(shortline,"=")
            wordlist = string.split(shortline[0:indexal])
            alias = wordlist[1]
            content = shortline[indexal+1:]
            # taking out all the single quotes
            content = re.sub("'","",content)
            if not alias in State.aliasvetolist:
                State.aliasdict[alias] = content
        tempfile.close()
    State.aliaskeys = State.aliasdict.keys()
    State.aliaskeys.sort()

def aliasdo(cmdline):
    # replace the aliases with the real thing
    newcmdline = cmdline
    if Options.debuglevel > 1: print newcmdline
    wordlist = string.split(newcmdline)
    alias = wordlist[0]
    for key in State.aliasdict.keys():
        if key == alias:
            real = State.aliasdict[key]
            newcmdline = string.replace(newcmdline,alias,real)
            if Options.debuglevel > 1: print newcmdline
            return newcmdline
    return newcmdline

def aliasprint(variable=''):
    for key in State.aliaskeys:         # print key, value pairs
        if variable == '':
            print key, '\t', State.aliasdict[key]
        elif key == variable:
            print key, '\t', State.aliasdict[key]

def trackchanges():
    cmdline = 'diff ' + State.envfname + ' ' + State.envfnameold
    #print '====== Environment changes ======'
    #os.system(cmdline)
    first = 0
    for line in os.popen(cmdline):
        if first == 0: print '====== Environment changes ======'
        first = first + 1
        shortline = line[:-1]
        print shortline
    os.remove(State.envfnameold)
    shutil.copy2(State.envfname,State.envfnameold)
    cmdline = 'diff ' + State.aliasfname + ' ' + State.aliasfnameold
    #print '====== Alias changes ======'
    #os.system(cmdline)
    first = 0
    for line in os.popen(cmdline):
        if first == 0: print '====== Alias changes ======'
        first = first + 1
        shortline = line[:-1]
        print shortline
    os.remove(State.aliasfnameold)
    shutil.copy2(State.aliasfname,State.aliasfnameold)

