# Student.py - Student class
from Person import Person

class Student(Person):
    def __init__(self, name="", age=21, major="undeclared", gpa=0.0):
        Person.__init__(self, name, age)        # call super constr
        self.setMajor(major)
        self.setGPA(gpa)

    def setMajor(self, major):                  # setter method
        self.__major = major

    def getMajor(self):                         # getter method
        return self.__major

    def setGPA(self, gpa):                      # setter method
        self.__gpa = gpa

    def getGPA(self):                           # getter method
        return self.__gpa

    def __str__(self):                          # string method
        return "%s Major: %s GPA: %g" \
            %(Person.__str__(self),             # call super method
                 self.__major, self.__gpa)

