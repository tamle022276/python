#!/usr/bin/env python
# points.py - Point program
from Point import Point

p1 = Point(5, 5)                # Point at (5, 5)
p1.down()                       # move down
p1.right()                      # move right
print "Point 1 at:", p1.getX(), p1.getY()

p2 = Point(10, 20)              # Point at (10, 20)
p2.move(30, 40)                 # move to (30, 40)
print "Point 2 at:", p2.getX(), p2.getY()
print Point.numPoints(), "Points"

del p1, p2                      # delete Point objects
print Point.numPoints(), "Points"

#################################################
#
#    $ points.py
#    Point 1 at: 6 4
#    Point 2 at: 30 40
#    2 Points
#    0 Points
#
