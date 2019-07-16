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

def extractcd(cmdline):
    wordlist = cmdline.split()
    if wordlist[0] != 'cd': return None
    if len(wordlist) > 1:
        dirname = wordlist[1]
    else:
        dirname = ''
    if Options.loglevel > 0:
        envset()
        fnenv = State.envfname
    # 'cd' by itself means 'go home'
    if dirname == '':
        dirname = os.environ['HOME']
    # 'cd -' means 'go to previous dir'
    if dirname == '-':
        dirname = State.olddir
    # 'cd ..' means 'go to upper dir'
    if dirname == '..':
        dirname = "/".join(os.getcwd().split('/')[:-1])
        if dirname == '': dirname = '/'
    # now DO cd
    if Options.debuglevel > 1: print("==> Will do ==> " + wordlist[0] + ' ' + dirname)
    State.olddir = os.getcwd()
    os.chdir(dirname)
    State.curdir = os.getcwd()
    if Options.loglevel > 0:
        cmdline = "env > " + fnenv
        os.system(cmdline)
        envsnap(fnenv)
    if Options.loglevel == 3: trackchanges()

def extractrun(cmdline,listReplacement,delim):
    
    if len(listReplacement) != 0:

       # Replace the word to alternate command
       newShortline = cmdline.split()
    
       for s in newShortline:
           # scan the user replacement list for words
           # to be replaced in the commandline
           for entry in listReplacement:
               wordToReplace = entry.split(delim)
               if wordToReplace[0][1:] == s:
                   newShortline[newShortline.index(s)] = wordToReplace[1][:-1]
    
       # Construct a new command line
       shortline = " ".join(newShortline)
       if cmdline != shortline:   
          print("New Command is: " + shortline)
       cmdline = shortline

    # run commands for extract
    fnal = State.aliasfname
    if Options.shell == "bash":
        prolog = "/bin/bash -c '"
        prolog = prolog + ". " + fnal + "; "
        clobber = "|"
    else:
        prolog = "/bin/tcsh -c '"
        prolog = prolog + "source " + fnal + "; "
        clobber = "!"
    if Options.loglevel > 0:
        fnenv = State.envfname
        envsnap(fnenv)
        envset()
    if Options.loglevel >= 2:
        cmdline = aliasdo(cmdline)
    cmdline = prolog + cmdline + " ; env >" + clobber + " " + fnenv + " ; alias >" + clobber + " " + fnal + " '"
    if Options.debuglevel > 2: print("==> Will do: " + cmdline)
    for line in os.popen(cmdline).readlines():
        shortline = line[:-1]  # strip '\n'
        print(shortline)
    if Options.loglevel > 0:  envsnap(fnenv)
    if Options.loglevel >= 2: aliassnap(fnal)
    if Options.loglevel == 3: trackchanges()

def getReplacementList(parlist):
  listReplacement = []
  delim = parlist[2]
  data = "".join(parlist[3:])

  if parlist[1] == 'd':
     data = data + "\n"
     replacement = ''
     quote = 0
     traverseIndex = 0
     while(1):     # Aceess the comandline word by word to get
                   # the replacement list
       if(data[traverseIndex] == "\n"):
          break
       else:
          if data[traverseIndex] == '"':
             quote = quote + 1
          if quote == 1:     # For opening quote
             replacement = replacement + data[traverseIndex]
          if quote == 2:     # For closing quote
             replacement = replacement + '"'
             listReplacement.append(replacement)
             quote = 0
             replacement = ''
          traverseIndex = traverseIndex + 1

  if parlist[1] == 'file':
      try:
          replacefile = open(parlist[3], "r")
          for line in replacefile.readlines():
              shortline = line[:-1]  # strip '\n'
              if shortline != '' : listReplacement.append(shortline)
      except:
          print("Cannot open file: ",parlist[3])
          print(" when trying to extract+modify tag: ",parlist[0])

  if Options.debuglevel > 1:
      print("Replacement list: ",listReplacement)
      print("Delimeter: ",delim)

  return listReplacement, delim
