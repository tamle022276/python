#!/usr/bin/env python
# mythreads.py - spawn threads
from threading import Thread, currentThread
from time import sleep

# your code here...

##################################################
#
#     $ mythreads.py
#     Thread-1 sleeping for 5 secs
#     Thread-2 sleeping for 12 secs
#     Thread-3 sleeping for 3 secs
#     Thread-4 sleeping for 19 secs
#     Thread-5 sleeping for 7 secs
#     Thread-3 has slept for 3 secs
#     Thread-1 has slept for 5 secs
#     Thread-5 has slept for 7 secs
#     Thread-2 has slept for 12 secs
#     Thread-4 has slept for 19 secs
#
