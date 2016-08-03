# MyException.py - Custom MyException hierarchy

class MyException(Exception):
    def response(self):
        assert 0, "did not implement response()"

