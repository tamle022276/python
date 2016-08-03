#!/usr/bin/env python3
# assign.py - import and from assignments
from mymodule import var, mylist

print("before:", var)
print("before:", mylist)

var = 2                # local var, no change
mylist[0] = -1         # changes mylist

import mymodule
print("after:", mymodule.var)
print("after:", mymodule.mylist)

#####################################
#
#     $ assign.py
#     before: 1
#     before: [1, 2]
#     after: 1
#     after: [-1, 2]
#
