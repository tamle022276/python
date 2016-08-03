def intersect(arg1, arg2):
    """
    >>> intersect([1, 2, 3, 4], (2, 4, 6, 8))
    [2, 4]
    >>> intersect([1, 2, 3], (4, 6))
    []
    >>>
    """
    common = []
    for arg in arg1:
        if arg in arg2:
            common.append(arg)
    return common
