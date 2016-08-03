#!/usr/bin/env python3
# pixels.py - Pixels and Points program
from Point import Point
from Pixel import Pixel

p1 = Point(5, 5)                # Point at (5, 5)
p2 = Pixel("red", 10, 20)       # red Pixel at (10, 20)
p2.move(30, 40)                 # move to (30, 40)

p3 = Pixel("green", 40, 60)     # green Pixel at (40, 60)
p3.down()                       # move down
p3.right()                      # move right

print("There are %d Points" %Point.numPoints())

for p in [p1, p2, p3]:
    print(p)

p3.clear()                      # clear Pixel
print(p3)                       # color should be cleared

#################################################
#
#    $ pixels.py
#    There are 3 Points
#    (5, 5)
#    color is red at (30, 40)
#    color is green at (41, 59)
#    color is  at (0, 0)
#
