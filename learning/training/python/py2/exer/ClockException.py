# ClockException.py - ClockException hierarchy
from MyException import MyException 

class ClockException(MyException):
    # your code here...
    def response(self): return "Clock Error"

class HourException(ClockException):
    # your code here...
    pass

class MinuteException(ClockException):
    # your code here...
    pass

