#!/usr/bin/env python2

import cmd, os, string, sys, shutil

os.system('rm -rf sandbox/')
# os.system('rm -f testoutput.txt')
os.system('rm -f sha')
os.system('rm -f codesh.bash.cvsRepochk.conf')
os.system('rm -f codesh.bash.asciiRepochk.conf')
os.system('rm -f codesh.bash.svnRepochk.conf')
os.system('rm -f codesh.??sh.ascii.conf')
os.system('rm -f codesh.??sh.cvs.conf')
os.system('rm -f codesh.??sh.svn.conf')
os.system('../clean.codesh')
os.system('rm -f ????-????????-????-*.conf')
