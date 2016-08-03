#ignore_error can be many, it separate by comma and it is optional
#Sample run 1 with ignore error: python uda_python.py --database_name=hela --user_name=dbc --user_password=dbc --ignore_error=3822,3807
#Sample run 2 without ignore error: python uda_python.py --database_name=hela --user_name=dbc --user_password=dbc

import sys
import os
import shutil
import time
import re
import argparse
import teradata
import errno
import subprocess
import traceback
import logging
import socket
import zipfile
import uuid
import getpass
import platform

# Check and validate input parameters
def setup_argparse():
    class IgnoreErrorAction(argparse.Action):
        def __init__(self, option_strings, dest, nargs=None, **kwargs):
            if nargs is not None:
                raise ValueError("nargs not allowed")
            super(IgnoreErrorAction, self).__init__(option_strings, dest, **kwargs)

        def __call__(self, parser, namespace, values, option_string=None):
            error_nums = []
            for v in values.split(","):
                v = v.strip()
                if not v: continue
                if not v.isdigit():
                    parser.error("Invalid argument values: %s. --ignore_error require integers separated by commas" % v)
                error_nums.append(int(v))
            setattr(namespace, self.dest, error_nums)

    parser = argparse.ArgumentParser(description="### validate_params.py ###")
    parser.add_argument("--dbsName", required=True, help="System name")
    parser.add_argument("--runIteration", required=True, help="Number of iteration")
    parser.add_argument("--runDurationMinutes", required=True, help="Number of minutes test will execute")
    parser.add_argument("--numUsers", required=True, help="Number of users for this test")
    parser.add_argument("--numLDIReadClone", required=True, help="Number of read LDI tables execute in parallel per user")
    parser.add_argument("--numPLLReadClone", required=True, help="Number of read PLL tables execute in parallel per user")
    parser.add_argument("--numALLReadClone", required=True, help="Number of read ALL tables execute in parallel per user")
    parser.add_argument("--runLDIwrite", required=True, help="Run insert/update/delete/load on LDI tables")
    parser.add_argument("--runPLLwrite", required=True, help="Run insert/update/delete/load on PLL tables")
    parser.add_argument("--runValidate", required=True, help="Run validate results on select queries")
    parser.add_argument("--Test", required=True, help="Run test phase")
    parser.add_argument("--Setup", required=True, help="Run setup phase")
    parser.add_argument("--Cleanup", required=True, help="Run cleanup phase")
    parser.add_argument("--dbcPassword", required=True, help="Password of DBC if not using default dbc")
    parser.add_argument("--UpdateControlFile", required=True, help="Update control files if new sql add or expected result to change")
    
    return parser.parse_args()

# Python exit wrapper function
def exit(ok=True):
    if ok is True or ok == 0:
        logging.info("================= End: [Validate test parameters completed sucessful] =================")
        sys.exit(0)
    else:
        logging.info("================== End: [Validate test parameters completed with error] ==================")
        sys.exit(1)

if __name__ == "__main__":

    try:
        # Get variables
        args = setup_argparse()
        dbsName = args.dbsName
        runIteration = int(args.runIteration)
        runDurationMinutes = args.runDurationMinutes
        numUsers = args.numUsers
        numLDIReadClone = args.numLDIReadClone
        numPLLReadClone = args.numPLLReadClone
        numALLReadClone = args.numALLReadClone
        runLDIwrite = args.runLDIwrite
        runPLLwrite = args.runPLLwrite
        runValidate = args.runValidate
        Test = args.Test
        Setup = args.Setup
        Cleanup = args.Cleanup
        dbcPassword = args.dbcPassword
        UpdateControlFile = args.UpdateControlFile
        # Setting up python log

        fh = logging.FileHandler("validate_log.txt", mode="a", encoding="utf8")
        fh.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
        fh.setLevel(logging.DEBUG)
        root = logging.getLogger()
        root.addHandler(fh)

        #if not dbsName:
        #   print("dbsName can not be NULL or empty, please fix this variable and try again")
        #   exit(1)
        if 0 <= runIteration <= 99999:
            print("dbsName can not be NULL or empty, please fix this variable and try again")
            exit(1)

    except Exception as e:
        logging.error(traceback.format_exc())
        exit(1)

    exit(0)

