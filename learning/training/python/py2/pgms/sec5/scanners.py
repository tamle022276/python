#!/usr/bin/env python
# scanners.py - file I/O

# Read file and print
myFile = open("testfile", "r")
print myFile.read()
myFile.close()

# Read file by chars
myFile = open("testfile")
for char in myFile.read():
    print char,
print
myFile.close()

# Read text file line by line
myFile = open("testfile")
for line in myFile.readlines(): print line,
print
myFile.close()

# Read byte chunks, 20 at a time
myFile = open("testfile")
file = ""
while True:
    chunk = myFile.read(20)
    file += chunk
    if not chunk: break         # eof
print file
myFile.close()

###############################################
#
#    $ scanners.py
#    This is line one.
#    This is line two.
#    This is line three.
#    This is line four.
#    
#    T h i s   i s   l i n e   o n e . 
#    T h i s   i s   l i n e   t w o . 
#    T h i s   i s   l i n e   t h r e e . 
#    T h i s   i s   l i n e   f o u r . 
#    
#    This is line one.
#    This is line two.
#    This is line three.
#    This is line four.
#    
#    This is line one.
#    This is line two.
#    This is line three.
#    This is line four.
#
