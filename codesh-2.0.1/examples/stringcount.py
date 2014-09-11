#!/usr/bin/env python2
# Counting the number of times the string argv[2]
# occurs in a file argv[1]
import sys, string
fname = sys.argv[1]
str = sys.argv[2]
text = open(fname,'r').read()
print 'String =>',str,'<= occurs =>',string.count(text, str),'<= times in file =>',fname
