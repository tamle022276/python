# PerfectNumber.py - perfect numbers

def isPerfect(number):
    perfect = 0
    for n in range(1, number):
        if (number % n == 0):
            perfect += n
    return perfect == number

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
