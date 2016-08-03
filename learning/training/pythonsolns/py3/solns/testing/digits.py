def translate(num):
    """
    >>> num = 18 
    >>> translate(num)
    'eighteen'
    >>> num = 39 
    >>> translate(num)
    'thirty nine'
    >>> num = 61 
    >>> translate(num)
    'sixty one'
    >>> num = 80 
    >>> translate(num)
    'eighty '
    >>>
    """
    specials = { 0:"zero", 11:"eleven", 12:"twelve", 13:"thirteen", 14: "fourteen",
                15:"fifteen", 16:"sixteen", 17:"seventeen", 18:"eighteen", 19:"nineteen" }

    ones = { 0:"", 1:"one", 2:"two", 3:"three", 4:"four", 5:"five", 6:"six",
              7:"seven", 8:"eight", 9:"nine" }

    tens = { 1:"ten", 2:"twenty", 3:"thirty", 4:"forty", 5:"fifty", 6:"sixty",
                 7:"seventy", 8:"eighty", 9:"ninety" }

    if (num in specials):
        return specials[num]

    if (num < 10):
        return ones[num]

    one = ones[num % 10]
    ten = tens[num // 10]
    return ten + " " + one

