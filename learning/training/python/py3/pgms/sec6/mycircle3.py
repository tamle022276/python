#!/usr/bin/env python3
# mycircle3.py - Circle program
from Circle3 import Circle

c1 = Circle()                  # default Circle
print("radius = %g" %c1.getRadius())
print("area = %g" %c1.area())

c2 = Circle(10)                # create Circle
print("radius = %g" %c2.getRadius())
print("area = %g" %c2.area())

print(Circle.numCircles(), "circles")   # 2 circles
del c1, c2                     # delete circles

if (Circle.numCircles() == 0):
    print("no more circles")   # no more circles

#################################################
#
#    $ mycircle3.py
#    radius = 1
#    area = 3.14159
#    radius = 10
#    area = 314.159
#    2 circles
#    no more circles
#
