# CommaFormat.py - format numbers with commas

def format(number):
    import re
    regex = "(\d)(?=(\d{3})(?!\d))"
    return re.sub(regex, r"\1,", number)

def show(number):
   """
   >>> show("1234")
   1,234
   >>> show("123456")
   123,456
   """
   print(format(number))
