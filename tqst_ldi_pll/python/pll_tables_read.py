#!/usr/bin/python3
# Author: tl151006
# File: pll_tables_read.py
# Date Published: 03/14/2016
# Purpose: Run PLL tables read for LDI and PLL test
# Usage: python pll_tables_read.py --database_name=db_name --user_name=db_user --user_password=db_password --ignore_error=error_1,error_2,error_n
# ignore_error can none to many, it separate by comma and it is optional
# Example 1 with 2 ignore errors: python using_common_codes.py --database_name=hela --user_name=dbc --user_password=dbc --ignore_error=3822,3807
import sys
import os
import shutil
import time
import re
import argparse
import teradata
import errno
import traceback
import logging
import socket
import zipfile
import uuid
import getpass
import platform
import threading, queue
import multiprocessing
os_user_name = getpass.getuser()
os_type = platform.system()
#if os_user_name == "tomcat":
#    sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'common'))
#else:
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', '..', 'common')) 
import tdtestpy

common_error = "2631, 2641, 3603, 9624" #Deadlock, table restructured, concurrent change conflict, and Logical row does not exist due to DML run in parallel

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

    parser = argparse.ArgumentParser(description="### setup.py ###")
    parser.add_argument("--dbs_name", required=True, help="System name")
    parser.add_argument("--iteration", required=True, help="Iteration Number of this run")
    parser.add_argument("--threadNum", required=True, help="threadNum Number of this run")
    parser.add_argument("--pll_read_clone", required=True, help="pll_read_clone for this run")
    parser.add_argument("--dbc_password", required=True, help="DBC password")
    parser.add_argument("--user_name", required=True, help="User name")
    parser.add_argument("--scriptPath", required=True, help="Get current Jmeter test plan path")
    parser.add_argument("--run_timestamp", required=True, help="Get current run time")
    parser.add_argument("--ignore_error", required=False, default=[],
            help="Error number should be ignored. Must be integers separated by commas.", action=IgnoreErrorAction)

    return parser.parse_args()

# Copy log file to correct path
def copy_file(src, dest):
   shutil.copy(src, dest)

def run_sql_file(my_db_connect, pll_tables_read_queries, pll_read_clone, pll_tables_read_ignore_errors, run_result=None):
    try:
        with my_db_connect.cursor() as cursor:
            cursor.execute(file=pll_tables_read_queries, ignoreErrors=pll_tables_read_ignore_errors)
    except Exception as e:
        logging.error("PLL Tables Read failed because of this error %d. Please check out this log file: %s" % ((e.args[0]), test_log_name))
        #logging.error(traceback.format_exc())
        run_result.put(False)
    run_result.put(True)
        
def run_sql_file_MultipleThreads(db_conn, pll_tables_read_queries, pll_read_clone, pll_tables_read_ignore_errors):
    threadCount = pll_read_clone
    threads = []
    with db_conn as conn:
        for i in range(0, threadCount):
            run_result = queue.Queue()
            t = threading.Thread(
                target=run_sql_file, args=(conn, pll_tables_read_queries, pll_read_clone, pll_tables_read_ignore_errors, run_result))
            t.daemon = True
            threads.append(t)
            t.start()
        for t in threads:
            t.join()
    return run_result.get()

               
# Python exit wrapper function
def exit(ok=True):
    if ok is True or ok == 0:
        logging.info("================= End: PLL Tables Read Success!] =================")
        sys.exit(0)
    else:
        logging.info("================== End: PLL Tables Read Failed, Please Check Out ERROR Messages Above!] ==================")
        sys.exit(1)

if __name__ == "__main__":


    try:
        udaExec = teradata.UdaExec (appName="PLL_READ", version="1.0", logConsole=True)
        
        args = setup_argparse()
        
        dbs_name = args.dbs_name
        iteration = args.iteration
        threadNum = args.threadNum
        pll_read_clone = int(args.pll_read_clone)
        dbc_password = args.dbc_password
        scriptPath = args.scriptPath
        run_timestamp = args.run_timestamp
        user_name = args.user_name
        ignore_error = args.ignore_error
        con_method = "odbc"
        
        
        
        # Set logs variables
        loopnum = "L" + iteration
        pll_tables_read = os.path.join(scriptPath, "output", dbs_name, run_timestamp, "latest")
        faileddir = os.path.join(scriptPath, "output", dbs_name, run_timestamp, "failed")
        passed_dir = os.path.join(scriptPath, "output", dbs_name, run_timestamp, "passed")
        pll_tables_read_ignore_errors = tdtestpy.get_ignore_errors(common_error) + ignore_error     
        pll_tables_read_queries = os.path.join(scriptPath, "sql", "pll_tables_read.txt")
        bteq_log = user_name + "_pll_tables_read_loop_" + iteration + "_clone.log"
        bteq_out_file = os.path.join(pll_tables_read, bteq_log)
        
        # Delete old log from latest
        prior_run_id = int(str(iteration)) - 1
        org_pll_read_clone = pll_read_clone
        if org_pll_read_clone == 1:
            old_bteq_log = user_name + "_pll_tables_read_loop_" + str(prior_run_id) + "_clone.log"
            old_bteq_out_file = os.path.join(pll_tables_read, old_bteq_log)
            tdtestpy.delete_one_file(old_bteq_out_file)
        else:
            while org_pll_read_clone != 0:
                old_bteq_log = user_name + "_pll_tables_read_loop_" + str(prior_run_id) + "_clone" + str(org_pll_read_clone) + ".log"
                old_bteq_out_file = os.path.join(pll_tables_read, old_bteq_log)
                tdtestpy.delete_one_file(old_bteq_out_file) 
                org_pll_read_clone -= 1 
        old_testuser = user_name + "_pll_read_loop_" + str(prior_run_id) + "_python.log"
        old_test_log_name = os.path.join(pll_tables_read, old_testuser)
        tdtestpy.delete_one_file(old_test_log_name) 
                 
                
        # dump python log to demo_log_path
        testuser = user_name + "_pll_read_loop_" + iteration + "_python.log"
        test_log_name = os.path.join(pll_tables_read, testuser)       
        fh = logging.FileHandler(test_log_name, mode="a", encoding="utf8")
        fh.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
        fh.setLevel(logging.DEBUG)
        root = logging.getLogger()
        root.addHandler(fh) 
                
        
        # Main Body
        logging.info("================== Test Start ==================")
       
        if not tdtestpy.run_bteq_parallel(pll_tables_read_queries, bteq_out_file, dbs_name, user_name, user_name, \
                                       pll_tables_read_ignore_errors, pll_read_clone, faileddir, passed_dir):
            tdtestpy.copy_file(test_log_name, faileddir)
            exit(1)

            
    except Exception as e:
        logging.error(traceback.format_exc())
        tdtestpy.copy_file (test_log_name, faileddir)
        exit(1)
        
    exit(0)
