#!/usr/bin/env python3
# scripts.py - run linux commands
import sys, os

nargs = len(sys.argv)-1
if nargs < 1:
    sys.stderr.write("Usage: scripts.py directory name(s)\n")
    exit(1)

direc = sys.argv[1]
names = " "
if nargs == 2:
    names = " -name " + sys.argv[2]

cmd = "find " + direc + names + \
   " | xargs file | grep script | cut -f1 -d:"

scripts = os.popen(cmd).read()
print(scripts, end="")

###############################################
#
#    $ scripts.py /usr/bin/ "h*"
#    /usr/bin/h2ph
#    /usr/bin/hp-plugin-ubuntu
#    /usr/bin/helpztags
#    /usr/bin/h2xs
#
