# BArray.py - Bounded Array

class BArray:
    def __init__(self, lb, ub):            # constr
        self.__lower = lb
        self.__upper = ub
        self.__array = list(range(lb, ub+1))

    def lb(self):
        return self.__lower

    def ub(self):
        return self.__upper

    def length(self):
        return self.__upper - self.__lower+1

    def __getitem__(self, index):          # indexing
        return self.__array[index - self.__lower]

    def __setitem__(self, index, value):   # index assign
        self.__array[index - self.__lower] = value

    def getRange(self):
       return range(self.__lower, self.__upper+1)

