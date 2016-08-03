#!/usr/bin/env python
# pipes.py - run pipe commands
import os,subprocess

# popen is deprecated, although easy to use
cmd = "grep paul /etc/passwd | cut -f5 -d:"
me = os.popen(cmd).read()
print me,

# Better to use subprocess, but forks shell (slow)
cmd = "grep paul /etc/passwd | cut -f5 -d:"
me = subprocess.check_output(cmd, shell=True)
print me,

# Faster way to do it, no shell
# note that commands and args must be lists
cmd1 = "grep paul /etc/passwd"
cmd2 = "cut -f5 -d:"
p1 = subprocess.Popen(cmd1.split(), stdout=subprocess.PIPE)
p2 = subprocess.Popen(cmd2.split(), stdin=p1.stdout, stdout=subprocess.PIPE)
me, err = p2.communicate()
print me,

###################################################################
#
#    $ pipes.py
#    Paul Anderson
#    Paul Anderson
#    Paul Anderson
