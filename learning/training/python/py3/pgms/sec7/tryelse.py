#!/usr/bin/env python3
# tryelse.py - try with else

def doSomething():
    L1 = [0, 1, 2]
    #L1[3] = 3
    #print(L1 + "abc")

try:
    doSomething()
except IndexError:
    print("Out of range")
except (AttributeError, TypeError, SyntaxError):
    print("Parse error")
except:
    print("Other error")
else:
    print("No errors")

###################################################
#
#     $ tryelse.py
#     No errors
#
