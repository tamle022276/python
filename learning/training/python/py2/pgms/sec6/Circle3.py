# Circle3.py - Circle class
import math

class Circle:
    __count = 0                       # class counter
    def __init__(self, radius = 1):   # constructor
        self.setRadius(radius)        # call setter
        Circle.__count += 1           # incr class counter

    def __del__(self):                # destructor
        Circle.__count -= 1           # decr class counter

    def setRadius(self, radius):      # setter method
        if (radius <= 0):
            radius = 1                # default if neg
        self.__radius = radius        # instance data

    def getRadius(self):              # getter method
        return self.__radius          # return radius

    def area(self):                   # instance method
        return math.pi * self.__radius * self.__radius

    @staticmethod                     # static method
    def numCircles():                 # no self arg
        return Circle.__count         # return class counter

