"""myinterest.entrypoint: provides entry point main()."""

__version__ = "1.0"

import sys
from .loans import calc

def main():
    if len(sys.argv) < 4:
      sys.stderr.write("Usage: myinterest.py cash rate time\n")
      exit(1)

    print("Executing myinterest version %s:" %__version__)

    cash = int(sys.argv[1])
    rate = float(sys.argv[2])
    time = int(sys.argv[3])

    print("cash = ", cash)
    print("interest = ", rate)
    print("time period = ", time)

    calc(cash, rate, time)
