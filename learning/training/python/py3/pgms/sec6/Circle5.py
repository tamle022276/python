# Circle5.py - Circle class

class Circle(object):                 # inherit from object
    def __init__(self, radius = 1):   # constructor
        self.__radius = radius        # set radius property

    @property
    def radius(self):                 # radius property getter
        return self.__radius          # return radius

    @radius.setter
    def radius(self, radius):         # radius property setter
        if (radius <= 0):
            radius = 1                # default if neg
        self.__radius = radius        # instance data


