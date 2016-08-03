# ClockException.py - ClockException hierarchy
from MyException import MyException 

class ClockException(MyException):
    def __init__(self, badval):
        self._badval = badval

class HourException(ClockException):
    def __init__(self, _badval):
        ClockException.__init__(self, _badval)
    def response(self):
        return "hour %d not between 0 and 23" %self._badval

class MinuteException(ClockException):
    def __init__(self, _badval):
        ClockException.__init__(self, _badval)
    def response(self):
        return "minute %d not between 0 and 59" %self._badval

