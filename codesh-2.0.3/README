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


                        Project: CODESH

                          Basic Idea
                         ============

CODESH - COllaborative DEvelopment SHell is an intelligent shell, which
automatically logs a user's command line (shell) session: commands, scripts
executed, output produced, changes to environment variables, alias creation 
and other information needed to recreate the session later. This session is
uniquely tagged and stored in local or distributed backend repositories and
can be extracted and reproduced at any time by the user who created the
session or by collaborators located anywhere in the world.

The fundamental concept in CODESH is to store all the information necessary
to reproduce a user's session. This is achieved by maintaining a virtual
logbook, which records the initial state (pre-conditions of a session), all
the commands typed by the user, all the outputs generated and also all the
programs (shell scripts) executed to produce the results. Also the changes
made to the environment i.e. environment variables and aliases are recorded.
When a user's session ends, or even before, if the user so desires, CODESH tags
the complete log along with the data and source program files with a uniquely
generated tag and logs it to a repository. The repositories can contain
hundreds and thousands of such stored sessions.

Reproduction of a session is possible by extracting the log, data and source
files, and executing the commands listed in the log files including running
the scripts that are downloaded from the repository in their original form
as when the session was recorded. Later changes or even deletion of scripts
have no effect on the reproducibility of sessions as the scripts can be
retrieved from the repository anytime.

Also the environment changes can be carried across sessions. The repositories
of such sessions can be on the local machine for personal usage or on
shared servers for the use of collaborating groups. Generally the user will
store all his sessions locally and 'publish' a few important sessions to some
shared repository. He may also extract and reproduce stored sessions of
other collaborators.

Version 1.2.0 introduces the novel concept of a flex session. The convenient
log-and-replay mechanism of CODESH is expanded to log-modify-and-replay. Now
individuals and groups can not only log, share and reproduce their sessions at
will, they can browse and inspect sessions from private or shared repositories,
alter them on the fly from the command line or files containing the changes,
and "replay" many similar sessions starting from a previously recorded session.
The modified sessions can in turn be recorded for further use and reuse.

There is also a feature, aptly called 'Snapshot', which allows logging entire
directory structures under the current working directory. This can later be
retrieved and thus it provides a virtual working directory. Using this concept,
a virtual session can be copied to any place on the same machine or even across
machines and restarted or modified. Of course this is possible if the user
works relative to the root of the snapshot directory without using absolute
paths.


                         Prerequisites
                        ===============

CODESH requires very little to run: just Python 2 if you use the flat file
(ASCII) backend. If you use the CVS backend, you need a CVS client. Most LINUX
distributions provide CVS clients out of the box so usually there is no need to
install additional packages. If you use the Subversion backend, you need a
Subversion client.


                            HOW-TO
                           ========

    CODESH is very user friendly and easy to use:

    1) Check out the code from the source repository.

    2) Create a local CODESH repository to get going:

       2.1 CVS backend

         chmod u+x create-codeshcvsrepository.sh
         ./create-codeshcvsrepository.sh <local repository location>

       2.2 ASCII backend

         chmod u+x create-codeshasciirepository.sh
         ./create-codeshasciirepository.sh <local repository location>

       2.3 Subversion backend

         chmod u+x create-codeshsvnrepository.sh
         ./create-codeshsvnrepository.sh <local repository location>

    3) Initialize PATH and PYTHONPATH for CODESH:

         in  sh/bash:  . codesh_init.sh

         in csh/tcsh:  source codesh_init.csh

    4) Change to a working directory
       (we strongly recommend to keep it distinct
        from the code directory).

       NOTE on the WORKING DIRECTORY: in order to avoid any possible
          interference with your existing directory/file structure,
          WE STRONGLY RECOMMEND TO CREATE A NEW SUBDIRECTORY (SANDBOX)
          AND START CODESH THERE, ESPECIALLY IF YOU ARE NEW TO CODESH.

    5) Start CODESH:

        5.1 As a shell:

             codesh.py

           User is asked to select options if desired.
           As a minimum the repository location for virtual
           sessions could be defined.
           NOTE: when a file codesh.conf is present in the working
           directory, it will be used automatically and no start-up
           dialog will appear, c.f. 5.2.

        5.2 With a configuration file:

           examples: codesh.bash.conf, codesh.tcsh.conf
           default file: codesh.conf (automatically used if present)

             codesh.py -c <config file>

        5.3 In batch mode (to run commands from FILE):

             codesh.py -b < FILE
             codesh.py -c <config file>  -b < FILE

           FILE can be a logfile for a virtual session produced
           by CODESH or just a collection of shell commands.

    6) Use CODESH:

        Type help or ? for a list of commands.
        Type help <command> or ? <command> for help on specific commands.

        Try out the CODESH commands. All non-CODESH commands
          are delegated to the underlying shell - bash or tcsh.
        Use your favorite shell commands, they should work like in
          a standard shell.

        Log your sessions, browse existing sessions etc.

        Look at the examples in the examples directory.

        Ctrl-D to exit from CODESH.

    7) We provide a script for cleaning up the working directory
       (run it ONLY there):

        clean.codesh

                        Examples and tests
                       ====================

    The  examples  subdir contains basic examples of sessions using the
command line and running scripts. The user can run interactively or in
batch and create the logs of first virtual sessions. The sessions can be
reproduced later from a new and independent location.

    The  tests  subdir contains an expandable test suite for automatic testing
of the basic functionality of CODESH. During development cycles passing all
tests is a precondition for making new releases public. The tests serve a dual
purpose as varied examples of using CODESH in different modes of operation and
at different levels of sophistication.

                        Remote repositories
                       =====================

    The use of remote repositories is transparent. The code is smart enough to
recognize that the repository for the virtual session is a remote one, and
to act accordingly. The user has to make sure that remote authentication and
authorization from the client to the server machine is available. The first
time the user tries to access the remote repository CODESH will verify that
the connection is "live" and issue a warning otherwise.
    
    Remote repositories are specified as follows:

    1) ASCII: access based on ssh and scp

        user@host:<remote_repository_location>

        Access can be controlled e.g. by the use of public and private keys.

        The standard create-codeshasciirepository.sh script can be used
        to create repositories on remote hosts.

    2) CVS: access based e.g. on pserver or kserver

        For pserver on port 2401

         :pserver:user@host:2401<absolute_path_to_remote_repository_location>

         Access can be controlled e.g. by storing the password in
                 ~/.cvspass

        The standard create-codeshcvsrepository.sh script can be used
        to create repositories on remote hosts. Depending on the access mode
        (pserver, kserver) and the local user used by the cvs server,
        additional configuration is usually required e.g. by adjusting the
        file permissions, etc.

    3) Subversion: access based e.g. on svnserve or svnserve over SSH or
       the mod_dav_svn module for Apache

        The standard create-codeshsvnrepository.sh script can be used
        to create repositories on remote hosts. Depending on the access mode
        additional configuration is usually required.
       

    ENJOY!

