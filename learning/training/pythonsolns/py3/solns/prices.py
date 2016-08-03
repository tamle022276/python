#!/usr/bin/env python3
# prices.py - min(), max() for dictionary

prices = {"ACME" : 45.23, "AAPL" : 94.43, "IBM" : 192.05,
          "HPQ" : 34.81, "FB" : 68.42}

min_price = min(zip(prices.values(), prices.keys()))
print(min_price)

max_price = max(zip(prices.values(), prices.keys()))
print( max_price)

##########################################

#    $ prices.py
#    (34.81, 'HPQ')
#    (192.05, 'IBM')
