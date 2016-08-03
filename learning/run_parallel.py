# File: run_jmeter.py
# Author: Tam Le
# Author Email: tam.le@teradata.com
# Date Published: 01/29/2015
# Purpose: This program is running jmeter test plan and validate it's results based on samplers output
# Usage: python run_jmeter.py --database_name=teradata_database --jmeter_test_plan=your_jmeter_test_plan --number_of_loop=1 --duration_in_seconds=30
import sys
import os
import multiprocessing
import shutil
import time
import re
import argparse
import errno
import subprocess
import traceback
import logging
import socket
import zipfile
import uuid
import getpass
import platform
import glob
import uda2c
import random

# scan for error from all files in a directory


# Exectue 3 with 2 failutres and one success:
def run_bteq_FAIL(bteq_in_file, bteq_log_file, database_name, user_name, user_password, bteq_ignore_errors):
    print("*** Running 'run_bteq' with parameters:", bteq_in_file, bteq_log_file, database_name, user_name, user_password, bteq_ignore_errors)
    time.sleep(1)
    if '2' in bteq_log_file:
        return (True, random.randint(1,100))
    else:
        return (False, 0)

def run_parallel(func, bteq_in_file, bteq_log_file, database_name, user_name, user_password, bteq_ignore_errors, num_of_jobs=1):
    """
    Executes in paralled func with passed arguments
    and handles the results
    """

    def bteq_log_name(i):
        """Creates a unique logfile name with 'i' sequence number."""
        if num_of_jobs==1:
            # if running a single process don't change the name:
            return bteq_log_file
        else:
            return str(i).join(os.path.splitext(bteq_log_file))


    pool = multiprocessing.Pool(processes=num_of_jobs)
    results = pool.starmap(func, [(bteq_in_file, bteq_log_name(i), database_name, user_name, user_password, bteq_ignore_errors) for i in range(1, num_of_jobs+1)])
    print (results) 
    this_pass = this_fail = 0
    #https://docs.python.org/2.3/whatsnew/section-enumerate.html
    for i, (bteq_run_result, bteq_errors_that_not_ignore) in enumerate(results, 1):
        
        if not bteq_run_result:
            print ("It Passed")
            this_pass = this_pass + 1
        else:
            print ("Error found that can not be ignored: %s, please check out this log file: %s" % (bteq_errors_that_not_ignore, bteq_log_name(i)))
            this_fail = this_fail + 1


    if this_fail > 0:
        print ("There is %s failed, out of %s jobs" % (this_fail, num_of_jobs))
        sys.exit(1)

    else:
        print ("Test Passed")
        sys.exit(0)

# Python exit wrapper function
def exit(ok=True):
    if ok is True or ok == 0:
        logging.info("================= End: [Jmeter completed sucess] =================")
        sys.exit(0)
    else:
        logging.info("================== End: [Jmeter Fail, please investigate logs] ==================")
        sys.exit(1)

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

    parser = argparse.ArgumentParser(description="### bteq.PY ###")
    parser.add_argument("--database_name", required=True, help="System name")
    parser.add_argument("--user_name", required=True, help="User name")
    parser.add_argument("--user_password", required=True, help="User password")
    parser.add_argument("--ignore_error", required=False, default=[],
            help="Error number should be ignored. Must be integers separated by commas.", action=IgnoreErrorAction)

    return parser.parse_args()


if __name__ == "__main__":

    try:

#        args = setup_argparse()

#        database_name = args.database_name
#        user_name = args.user_name
#        user_password = args.user_password
#        ignore_error = args.ignore_error

        bteq_in_file = "bteq_queries.txt"
        bteq_log_file = "bteq_queries_output.log"
        database_name = "hela"
        user_name = "dbc"
        user_password = "dbc"
        bteq_ignore_errors = [2631, 3822, 3807]
        num_of_jobs = 100

        run_parallel(uda2c.run_bteq, bteq_in_file, bteq_log_file, database_name, user_name, user_password, bteq_ignore_errors, num_of_jobs)
        #run_parallel(run_bteq_FAIL, bteq_in_file, bteq_log_file, database_name, user_name, user_password, bteq_ignore_errors, num_of_jobs)


    except Exception as e:
        logging.error(traceback.format_exc())
        exit(1)

    exit(0)
