# Person.py - Person class

class Person:
    __count = 0
    def __init__(self, name="", age=21):    # constructor
        self.setName(name)
        self.setAge(age)
        Person.__count += 1

    def __del__(self):                      # destructor
        Person.__count -= 1                 # decr Point counter

    def setName(self, name):                # setter method
        self.__name = name

    def getName(self):                      # getter method
        return self.__name

    def setAge(self, age):                  # setter method
        if (age <= 0):
            age = 21
        self.__age = age

    def getAge(self):                       # getter method
        return self.__age

    def __str__(self):                      # string method
        return "Name: %s Age: %d" \
            %(self.__name, self.__age)

    @staticmethod                           # static method
    def numPersons():                       # no self arg
        return Person.__count               # return counter

