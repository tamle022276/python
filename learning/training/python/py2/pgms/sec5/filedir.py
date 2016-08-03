#!/usr/bin/env python
# filedir.py - files and directories
import os

# get current directory
print os.curdir

# list files in current directory
print os.listdir(".") 

# change directory
os.chdir("direc")

# remove file
#os.remove("xfer.pyc")

# mkdir dir if does not exist
dir = "/tmp/source"
if not os.path.exists(dir):
    os.mkdir(dir)

# create path
currentdir = os.curdir
images = os.path.join(currentdir, "mydir", "images")
print images

# get file length
len = os.path.getsize('colors')
print "colors file length is", len

###################################################################
#
#    $ filedir.py
#    .
#    ['mod1.py', 'writef.py', 'scanners.py', 'scripts.py', 'greeting.pyc', 
#    'direc', 'colors', 'mymodule.pyc', 'myfuncs.py', 'mydir', 
#    '.filedir.py.swp', 'interest.pyc', 'interest.py', 
#    'import.py', 'testfile', 'pipes.py', 'from.py', 'fixedfile', 
#    'mod3.py', 'mod2.py', 'fixedrec.py', 'myfuncs.pyc', 'data', 
#    'file_name', 'readf.py', 'filedir.py', 'mod3.pyc', 'treewalk.py', 
#    'greeting.py', 'sets.py', 'assign.py', 'mod2.pyc', 'mymodule.py', 
#    'with.py', 'fromall.py', 'roi.py', 'first_in_line']
#    ./mydir/images
#    colors file length is 71
#
