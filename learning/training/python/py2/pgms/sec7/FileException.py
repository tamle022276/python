# FileException.py - FileException hierarchy
from MyException import MyException

class FileException(MyException):
    def __init__(self, filename):
        self._filename = filename

class OpenFileException(FileException):
    def __init__(self, _filename):
        FileException.__init__(self, _filename)
    def response(self):
        return "Can't open " + self._filename

class ReadFileException(FileException):
    def __init__(self, _filename):
        FileException.__init__(self, _filename)
    def response(self):
        return "Can't read " + self._filename

class WriteFileException(FileException):
    def __init__(self, _filename):
        FileException.__init__(self, _filename)
    def response(self):
        return "Can't write " + self._filename

