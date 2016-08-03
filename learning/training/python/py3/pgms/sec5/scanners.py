#!/usr/bin/env python3
# scanners.py - file I/O

# Read file and print
myFile = open("testfile", "r")
print(myFile.read())
myFile.close()

# Read file by chars
myFile = open("testfile")
for char in myFile.read():
    print(char, end="")
print()
myFile.close()

# Read text file line by line
myFile = open("testfile")
for line in myFile.readlines(): print(line, end="")
print()
myFile.close()

# Read byte chunks, 20 at a time
myFile = open("testfile")
file = ""
while True:
    chunk = myFile.read(20)
    file += chunk
    if not chunk: break         # eof
print(file)
myFile.close()

###############################################
#
#    $ scanners.py
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
