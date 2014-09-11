codesh
======

## COllaborative DEvelopment SHell

### Conception: Dimitri Bourilkov

                        Project: CODESH

                          Basic Idea
                         ============

CODESH - COllaborative DEvelopment SHell is an intelligent shell,
which automatically logs a user's command line (shell) session:
commands, scripts executed, output produced, changes to environment
variables, alias creation and other information needed to recreate the
session later. This session is uniquely tagged and stored in local or
distributed backend repositories and can be extracted and reproduced
at any time by the user who created the session or by collaborators
located anywhere in the world.

The fundamental concept in CODESH is to store all the information
necessary to reproduce a user's session. This is achieved by
maintaining a virtual logbook, which records the initial state
(pre-conditions of a session), all the commands typed by the user, all
the outputs generated and also all the programs (shell scripts)
executed to produce the results. Also the changes made to the
environment i.e. environment variables and aliases are recorded.  When
a user's session ends, or even before, if the user so desires, CODESH
tags the complete log along with the data and source program files
with a uniquely generated tag and logs it to a repository. The
repositories can contain hundreds and thousands of such stored
sessions.

Reproduction of a session is possible by extracting the log, data and
source files, and executing the commands listed in the log files
including running the scripts that are downloaded from the repository
in their original form as when the session was recorded. Later changes
or even deletion of scripts have no effect on the reproducibility of
sessions as the scripts can be retrieved from the repository anytime.

Also the environment changes can be carried across sessions. The
repositories of such sessions can be on the local machine for personal
usage or on shared servers for the use of collaborating
groups. Generally the user will store all his sessions locally and
'publish' a few important sessions to some shared repository. He may
also extract and reproduce stored sessions of other collaborators.

Version 1.2.0 introduces the novel concept of a flex session. The
convenient log-and-replay mechanism of CODESH is expanded to
log-modify-and-replay. Now individuals and groups can not only log,
share and reproduce their sessions at will, they can browse and
inspect sessions from private or shared repositories, alter them on
the fly from the command line or files containing the changes, and
"replay" many similar sessions starting from a previously recorded
session.  The modified sessions can in turn be recorded for further
use and reuse.

There is also a feature, aptly called 'Snapshot', which allows logging
entire directory structures under the current working directory. This
can later be retrieved and thus it provides a virtual working
directory. Using this concept, a virtual session can be copied to any
place on the same machine or even across machines and restarted or
modified. Of course this is possible if the user works relative to the
root of the snapshot directory without using absolute paths.

