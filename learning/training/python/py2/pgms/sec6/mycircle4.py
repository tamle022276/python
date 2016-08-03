#!/usr/bin/env python
# mycircle4.py - Circle program
from Circle4 import Circle

c1 = Circle(10)              
print "radius = %g" %c1.radius      # get property

c1.radius = 20                      # set property
print "radius = %g" %c1.radius      # get property

c1.radius = -30                     # bad radius
print "radius = %g" %c1.radius      # get property

#################################################
#
#    $ mycircle4.py
#    radius = 10
#    radius = 20
#    radius = 1
#
