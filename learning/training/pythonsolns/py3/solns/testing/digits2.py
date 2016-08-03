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
    tens = ("twenty", "thirty", "forty", "fifty", "sixty",
            "seventy", "eighty", "ninety")

    teens = ("ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen",
            "sixteen", "seventeen", "eighteen", "nineteen")

    ones = ("zero", "one", "two", "three", "four", "five",
            "six", "seven", "eight", "nine")

    if num <= 9:
        return ones[num]

    if num <= 19:
        return teens[num % 10]

    ten = tens[(num // 10)-2]
    one = " "
    if num % 10:
       one += ones[num % 10] 
    return ten + one

