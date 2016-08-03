#!/usr/bin/env python3
# mycircle5.py - Circle program
from Circle5 import Circle

c1 = Circle(10)              
print("radius = %g" %c1.radius)     # get property

c1.radius = 20                      # set property
print("radius = %g" %c1.radius)     # get property

c1.radius = -30                     # bad radius
print("radius = %g" %c1.radius)     # get property

#################################################
#
#    $ mycircle5.py
#    radius = 10
#    radius = 20
#    radius = 1
#
