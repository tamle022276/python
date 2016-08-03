#!/usr/bin/env python
# exinfo.py - exception info
import sys

try:
    raise NotImplementedError("No error")
except:
    info = sys.exc_info()
    print info
    print info[2].tb_frame.f_code.co_filename
    print info[2].tb_lineno

###################################################
#
#     $ exinfo.py
#     (<type 'exceptions.NotImplementedError'>, 
#         NotImplementedError('No error',), 
#             <traceback object at 0xb72af824>)
#     ./exinfo.py
#     6
#
