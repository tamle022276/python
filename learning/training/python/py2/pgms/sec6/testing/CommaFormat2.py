# CommaFormat2.py - easier format numbers with commas

def format(number):
    return "{:,}".format(int(number))

def show(number):
   """
   >>> show("1234")
   1,234
   >>> show("123456")
   123,456
   """
   print format(number)
