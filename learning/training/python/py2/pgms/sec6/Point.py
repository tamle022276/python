# Point.py - Point class

class Point:
    __count = 0                       # Point counter
    def __init__(self, x = 0, y = 0): # constructor
        self.move(x, y)
        Point.__count += 1            # incr Point counter

    def __del__(self):                # destructor
        Point.__count -= 1            # decr Point counter

    def __str__(self):                # string method
        return "(%d, %d)" %(self.__x, self.__y)

    def move(self, x, y):             # move to new location
        self.__x = x                  # instance data
        self.__y = y                  # instance data

    def getX(self): return self.__x   # x location
    def getY(self): return self.__y   # y location
    def up(self): self.__y += 1       # move up
    def down(self): self.__y -= 1     # move down
    def right(self): self.__x += 1    # move right
    def left(self): self.__x -= 1     # move left
    def clear(self): self.move(0, 0)  # move to (0,0)

    @staticmethod                     # static method
    def numPoints():                  # no self arg
        return Point.__count          # return counter

