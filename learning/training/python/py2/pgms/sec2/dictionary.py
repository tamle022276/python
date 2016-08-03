#!/usr/bin/env python
# dictonary.py - dictonaries

colors = {"red" : 0x00f, "green" : 0x0f0}
colors["blue"] = 0xf00
print "%d entries" %len(colors)
print colors
print colors.keys(), colors.values()
print colors.items()
del colors["blue"]
print colors.has_key("blue")  # print("blue" in colors) with python 3

##############################################
#
#     $ dictionary.py
#     3 entries
#     {'blue': 3840, 'green': 240, 'red': 15}
#     ['blue', 'green', 'red'] [3840, 240, 15]
#     [('blue', 3840), ('green', 240), ('red', 15)]
#     False
#
