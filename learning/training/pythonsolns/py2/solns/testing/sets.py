def intersect(*args):
    """
    >>> intersect([1, 2, 3, 4], (2, 4, 6, 8), [2, 4])
    [2, 4]
    >>>
    """
    result = []
    for arg in args[0]:
        for other in args[1:]:
            if arg not in other: break
        else:
            result.append(arg)
    return result

def union(*args):
    """
    >>> union([1, 2, 3, 4], (2, 4, 6, 8), [3, 9])
    [1, 2, 3, 4, 6, 8, 9]
    >>>
    """
    result = []
    for seq in args:
        for item in seq:
            if item not in result:
                result.append(item)
    return result
