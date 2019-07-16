#!/usr/bin/env python3

import cmd, os, string, sys, shutil

infoDict = {'17':['Svn repository with bash: log and browse'],
            '18':['Svn repository with tcsh: log and browse'],
            '19':['Svn repository with bash: extract bash/tcsh sessions'],
            '20':['Svn repository with tcsh: extract bash/tcsh sessions'],
            '23':['Svn repository with bash: take snapshots'],
            '24':['Svn repository with bash:  get snapshots']}

testDict = {'17':['browse <tag>: test-17 s','test-17'],
            '18':['browse <tag>: test-18 s','test-18'],
            '19':['Test 17: bash with svn repository','test-18.conf'],
            '20':['test-17.conf','Test 18: tcsh with svn repository'],
            '23':['takesnapshot <tag> <annotation>: test-23'],
            '24':['getsnapshot <tag>','Test 23: Take snapshots with bash and svn repository']}

success = 0

tempkeys=list(testDict.keys())
tempkeys.sort()

for k in tempkeys:
    outputfile = open('testoutputsvn.txt','r')
    success = 0
    for line in outputfile.readlines():
        shortline = line[:-1]  # strip '\n'
      
        if (shortline.find(testDict[k][0]) != -1):
            success = 1
            if (len(testDict[k]) == 1):
                success = 2
                print("Test-"+k+" SUCCESSFUL: "+repr(infoDict[k]))
                break
        
        # only when len(testDict[k]) == 2 we can enter this block
        if ((success == 1) and (shortline.find(testDict[k][1]) != -1)):
            success = 2
            print("Test-"+k+" SUCCESSFUL: "+repr(infoDict[k]))
            break
        
    if(success < 2):
        print("Test-"+k+" *==> UNSUCCESSFUL <==*: "+repr(infoDict[k]))

