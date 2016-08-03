# Clock.py - Clock class
from ClockException import *

class Clock: 
    def __init__(self, hour, minute):
        self.setHour(hour)
        self.setMinute(minute)

    def getHour(self): return self.__hour
    def getMinute(self): return self.__minute
    def setHour(self, hour): 
        if hour < 0 or hour > 23:
            raise HourException(hour)
        self.__hour = hour
    def setMinute(self, minute): 
        if minute < 0 or minute > 59:
            raise MinuteException(minute)
        self.__minute = minute

