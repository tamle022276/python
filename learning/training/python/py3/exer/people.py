#!/usr/bin/env python3
# people.py - Student, Person program
from Person import Person
from Student import Student

person1 = Person("Bob", 28)
person2 = Person("Jack", 42)
person3 = Student("Mary", 38, "English", 3.5)
person4 = Student("Joe", 31)
person4.setMajor("Math")
person4.setGPA(3.8)

print("There are %d people" %Person.numPersons())

for person in (person1, person2, person3, person4):
    print(person)

#################################################
#
#    $ people.py
#    There are 4 people
#    Name: Bob Age: 28
#    Name: Jack Age: 42
#    Name: Mary Age: 38 Major: English GPA: 3.5
#    Name: Joe Age: 31 Major: Math GPA: 3.8
#
