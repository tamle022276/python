# PerfectNumber.py - perfect numbers

def isPerfect(number):
    # your code here...

def show(number):
    """
    >>> show(28)
    28 is a perfect number
    >>> show(500)
    500 is not a perfect number
    """
    if (isPerfect(number)):
        print format(number),"is a perfect number"
    else:
        print format(number),"is not a perfect number"
