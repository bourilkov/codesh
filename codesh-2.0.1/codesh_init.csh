#!/bin/csh
#  Initialize PYTHONPATH for CODESH in csh/tcsh
#   To use CODESH just source this script in the
#   directory where you checked out the CODESH code,
#   then change to your working directory

if ( $?PATH == 0 ) then
 setenv PATH `pwd`
else
 setenv PATH `pwd`:${PATH}
endif

if ( $?PYTHONPATH == 0 ) then
 setenv PYTHONPATH `pwd`
else
 setenv PYTHONPATH `pwd`:${PYTHONPATH}
endif
