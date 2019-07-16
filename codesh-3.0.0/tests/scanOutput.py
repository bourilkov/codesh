#!/usr/bin/env python3

import cmd, os, string, sys, shutil

infoDict = {'01':['Environment variables with tcsh'],
            '02':['Environment variables with bash'],
            '03':['Aliases with tcsh'],
            '04':['Aliases with bash'],
            '05':['Use of eval with tcsh'],
            '06':['Use of eval with bash'],
            '11':['Ascii repository: if you forget to set it'],
            '12':['Ascii repository with bash: log and browse'],
            '13':['Ascii repository with tcsh: log and browse'],
            '14':['Ascii repository with bash: extract bash/tcsh sessions'],
            '15':['Ascii repository with tcsh: extract bash/tcsh sessions'],
            '16':['Cvs repository: if you forget to set it'],
            '17':['Cvs repository with bash: log and browse'],
            '18':['Cvs repository with tcsh: log and browse'],
            '19':['Cvs repository with bash: extract bash/tcsh sessions'],
            '20':['Cvs repository with tcsh: extract bash/tcsh sessions'],
            '21':['Ascii repository with bash: take snapshots'],
            '22':['Ascii repository with bash:  get snapshots'],
            '23':['Cvs repository with bash: take snapshots'],
            '24':['Cvs repository with bash:  get snapshots']}

testDict = {'01':['Codesh-tcsh-env1'],
            '02':['Codesh-bash-env2'],
            '03':['Codesh-tcsh-alias1','Codesh-tcsh-alias2'],
            '04':['Codesh-bash-alias1','Codesh-bash-alias2'],
            '05':['Codesh-tcsh-eval1'],
            '06':['Codesh-bash-eval1'],
            '11':['test-11','session without repository'],
            '12':['browse <tag>: test-12 s','test-12'],
            '13':['browse <tag>: test-13 s','test-13'],
            '14':['extract <tag>:','test-13.conf'],
            '15':['test-12.conf','extract <tag>:'],
            '16':['test-16','session without repository'],
            '17':['browse <tag>: test-17 s','test-17'],
            '18':['browse <tag>: test-18 s','test-18'],
            '19':['Test 17: bash with cvs repository','test-18.conf'],
            '20':['test-17.conf','Test 18: tcsh with cvs repository'],
            '21':['takesnapshot <tag> <annotation>: test-21'],
            '22':['getsnapshot <tag>','Test 21: Take snapshots with bash and ascii repository'],
            '23':['takesnapshot <tag> <annotation>: test-23'],
            '24':['getsnapshot <tag>','Test 23: Take snapshots with bash and cvs repository']}

success = 0

tempkeys=list(testDict.keys())
tempkeys.sort()

for k in tempkeys:
    outputfile = open('testoutput.txt','r')
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

