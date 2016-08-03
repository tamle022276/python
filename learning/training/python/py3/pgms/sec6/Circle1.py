# Circle1.py - Circle class
import math

class Circle:
    def setRadius(self, radius):      # setter method
        self.radius = radius          # instance data

    def getRadius(self):              # getter method
        return self.radius            # return radius

    def area(self):                   # instance method
        return math.pi * self.radius * self.radius
