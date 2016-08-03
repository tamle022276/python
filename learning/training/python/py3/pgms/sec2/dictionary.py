#!/usr/bin/env python3
# dictonary.py - dictonaries

colors = {"red" : 0x00f, "green" : 0x0f0}
colors["blue"] = 0xf00
print("%d entries" %len(colors))
print(colors)
print(colors.keys(), colors.values())
print(colors.items())
del colors["blue"]
print("blue" in colors)

##############################################
#
#     $ dictionary.py
#     3 entries
#     {'blue': 3840, 'green': 240, 'red': 15}
#     dict_keys(['blue', 'green', 'red']) dict_values([3840, 240, 15])
#     dict_items([('blue', 3840), ('green', 240), ('red', 15)])
#     False
#
