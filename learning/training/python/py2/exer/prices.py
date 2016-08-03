#!/usr/bin/env python
# prices.py - min(), max() for dictionary

prices = {"ACME" : 45.23, "AAPL" : 94.43, "IBM" : 192.05,
          "HPQ" : 34.81, "FB" : 68.42}

v = prices.values()
k = prices.keys()
mi = min(zip(v,k))
ma = max(zip(v,k))

print mi, ma



# your code here...

##########################################

#    $ prices.py
#    (34.81, 'HPQ')
#    (192.05, 'IBM')
