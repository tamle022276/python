# Circle2.py - Circle class
import math

class Circle:
    def __init__(self, radius = 1):   # constructor, default arg
        self.setRadius(radius)        # call setter

    def setRadius(self, radius):      # setter method
        if (radius <= 0):
            radius = 1                # default if neg
        self.__radius = radius        # instance data

    def getRadius(self):              # getter method
        return self.__radius          # return radius

    def area(self):                   # instance method
        return math.pi * self.__radius * self.__radius
