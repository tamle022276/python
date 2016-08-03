# Pixel.py - Pixel class
from Point import Point

class Pixel(Point):                                # inherit from Point
    def __init__(self, color = "", x = 0, y = 0):  # constr
        Point.__init__(self, x, y)                 # Point constr
        self.setColor(color)                       # set color

    def getColor(self): return self.__color
    def setColor(self, color): self.__color = color
    def clear(self): 
        Point.clear(self)                          # call Point clear()
        self.__color = ""                          # default

    def __str__(self):                             # string method
        return "color is %s at %s" %(self.__color, Point.__str__(self))

