#!/usr/bin/env python3
# list.py - lists

files = ["id.java", "id.py", "id.c"]
files.append("id.php")
print("There are %d files" %len(files))
print("Java file is", files[0])
del files[0]
files.sort()
print("My files are", files)

nums = [2, 4, 6, 8]
print(nums[0:2])
nums[0:2] = [1, 3]
print(nums)
print(nums[1:])
matrix = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
print(matrix[1])
print(matrix[1][1])

##############################################
#
#     $ list.py
#     There are 4 files
#     Java file is id.java
#     My files are ['id.c', 'id.php', 'id.py']
#     [2, 4]
#     [1, 3, 6, 8]
#     [3, 6, 8]
#     [4, 5, 6]
#     5
#
