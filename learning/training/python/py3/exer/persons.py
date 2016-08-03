#!/usr/bin/env python3
# persons.py - Person program
from Person import Person

person1 = Person("Bob", 28)
person2 = Person("Jack", 42)
person3 = Person("Mary", 38)
person4 = Person()
person4.setName("Jim")
person4.setAge(35)

print("There are %d people" %Person.numPersons())

for person in (person1, person2, person3, person4):
    print(person)

# delete all persons ...your code here...
print("There are %d people" %Person.numPersons())

#################################################
#
#    $ persons.py
#    There are 4 people
#    Name: Bob Age: 28
#    Name: Jack Age: 42
#    Name: Mary Age: 38
#    Name: Jim Age: 35
#    There are 0 people
#
