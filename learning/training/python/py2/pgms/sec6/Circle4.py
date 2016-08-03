# Circle4.py - Circle class

class Circle(object):                 # inherit from object
    def __init__(self, radius = 1):   # constructor
        self.setRadius(radius)        # call setter

    def setRadius(self, radius):      # setter method
        if (radius <= 0):
            radius = 1                # default if neg
        self.__radius = radius        # instance data

    def getRadius(self):              # getter method
        return self.__radius          # return radius

    radius = property(getRadius, setRadius, None, None)

