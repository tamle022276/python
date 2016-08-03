#!/usr/bin/env python3
# exmethods.py - exception methods
import time

class FormatError(Exception):
    def __init__(self, code, file):
        self.__code = code
        self.__file = file
        self.__log = open("logfile", "a") 
    def __del__(self):
        self.__log.close()
    def logError(self):
        self.__log.write("Error at: " + 
            self.__file + " " + str(self.__code) + 
                " " + time.asctime() + "\n")

def parser():
    raise FormatError(12, "myfile")

try:
    parser()
except FormatError as ex:
    ex.logError()

##################################################
#
#     $ exmethods.py
#
#     $ cat logfile
#     Error at: myfile 12 Tue Sep 9 08:46:42 2014
#     Error at: myfile 12 Tue Sep 9 08:47:02 2014
#
