#!/usr/bin/env python
# debug.py - debugging
import sys

try:
    raise NotImplementedError("No error")
except Exception as ex:
    (exc_type, exc_obj, exc_tb) = sys.exc_info()
    fname = exc_tb.tb_frame.f_code.co_filename
    print "File %s, Line %d: %s(\"%s\")" \
        %(fname, exc_tb.tb_lineno, 
            ex.__class__.__name__, exc_obj)

###################################################
#
#     $ debug.py
#     File ./debug.py, Line 6: NotImplementedError("No error")
#
