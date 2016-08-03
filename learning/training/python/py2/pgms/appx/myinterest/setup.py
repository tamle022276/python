"""setup.py: setuptools control."""

import re
from setuptools import setup

version = re.search(
    '^__version__\s*=\s*"(.*)"',
    open('myinterest/myinterest.py').read(),
    re.M
    ).group(1)


with open("README.rst", "rb") as f:
    long_descr = f.read().decode("utf-8")

setup(
    name = "myinterest",
    packages = ["myinterest"],
    entry_points = {
        "console_scripts": ['myinterest = myinterest.myinterest:main']
        },
    version = version,
    description = "Calculate compound interest",
    long_description = long_descr,
    author = "Paul Anderson",
    author_email = "paul@asgteach.com",
    )
