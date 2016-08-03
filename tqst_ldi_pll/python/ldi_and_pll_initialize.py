#!/usr/bin/python3
# Author: tl151006
# File: ldi_and_pll_initialize.py
# Date Published: 03/14/2016
# Purpose: Run pretest for LDI and PLL test
# Usage: python ldi_and_pll_initialize.py --database_name=db_name --user_name=db_user --user_password=db_password --ignore_error=error_1,error_2,error_n
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
os_user_name = getpass.getuser()
os_type = platform.system()

#if os_user_name == "tomcat":
#    sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'common'))
#else:
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', '..', 'common'))
import tdtestpy

common_error = "2631" #Transaction ABORTed due to deadlock

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
    parser.add_argument("--num_users", required=True, help="Number of users will run this test")
    parser.add_argument("--dbc_password", required=True, help="DBC password")
    parser.add_argument("--node_password", required=False, default='Sit4me123!', help="root password")
    parser.add_argument("--scriptPath", required=True, help="Get current Jmeter test plan path")
    parser.add_argument("--run_timestamp", required=True, help="Get current run time")
    parser.add_argument("--pll_write", required=True, help="pll_write")
    parser.add_argument("--ignore_error", required=False, default=[],
            help="Error number should be ignored. Must be integers separated by commas.", action=IgnoreErrorAction)

    return parser.parse_args()

# Python exit wrapper function
def exit(ok=True):
    if ok is True or ok == 0:
        logging.info("================= End: Pretest Success!] =================")
        sys.exit(0)
    else:
        logging.info("================== End: Pretest Failed!] ==================")
        sys.exit(1)

if __name__ == "__main__":


    try:
        udaExec = teradata.UdaExec (appName="LDI_PLL_PRETEST", version="1.0", logConsole=True)
        
        args = setup_argparse()
        
        dbs_name = args.dbs_name
        num_users = int(args.num_users)
        dbc_password = args.dbc_password
        node_password = args.node_password
        scriptPath = args.scriptPath
        pll_write = args.pll_write
        run_timestamp = args.run_timestamp
        ignore_error = args.ignore_error
        con_method = "odbc"
        
        pretest_con = udaExec.connect(method=con_method, system=dbs_name, username= "dbc", password= dbc_password)

        
        # Set logs variables
        test_log_path = os.path.join(scriptPath, "output", dbs_name, run_timestamp, "latest")
        failedtask = os.path.join(scriptPath, "output", dbs_name, run_timestamp, "failed")
        passed_dir = os.path.join(scriptPath, "output", dbs_name, run_timestamp, "passed")
        #completed_log = os.path.join(scriptPath, "output", "completed")
        
        test_log_name = os.path.join(test_log_path, "pretest.log")
        bteq_ignore_errors = tdtestpy.get_ignore_errors(common_error) + ignore_error

                
        # dump python log to demo_log_path        
        fh = logging.FileHandler(test_log_name, mode="a", encoding="utf8")
        fh.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
        fh.setLevel(logging.DEBUG)
        root = logging.getLogger()
        root.addHandler(fh) 
                
        logging.info("================== Pretest Starts ==================")
        
        # Check DBSControl Internal Fields: 332. PartitionLockingLevel must equal 95 if pll_write is set to "y"
        if pll_write == 'true':
            with pretest_con.cursor() as cursor:
                cursor.execute("delete from systemfe.opt_cost_table")
                cursor.execute("delete from systemfe.Opt_DBSCtl_Table")
                cursor.execute("diagnostic dump costs %s '%s'" % (dbs_name, dbs_name))
                cursor.execute("select FieldValue from SystemFe.Opt_DBSCtl_Table where FieldName = 'PartitionLockingLevel' and FieldNum = 332")
                res = cursor.fetchone()
                pll_value = int(res[0])
                if pll_value != 95:
                    logging.error ("Pretest failed with error: DBSControl internal fields 332 PartitionLockingLevel must = 95 when run PLL write. \
                    Current setting on %s is %s, please start DBSControl and run 'mod int 332 = 95' \
                    and restart the database for change to become effective" % (dbs_name, pll_value))
                    tdtestpy.copy_file (test_log_name, failedtask)
                    exit(1)
            
        # Get number of users existing in the system
        with pretest_con.cursor() as cursor:
            cursor.execute("select count(*) from dbc.users where UserName like 'sit_ldi_pll_user%'")
            res = cursor.fetchone()
            existing_user = res[0]
            if existing_user < num_users:
                logging.error ("You asked to run with %s users, but current setup has %s users, please rerun setup and try again" % (num_users, existing_user))
                tdtestpy.copy_file (test_log_name, failedtask)
                exit(1)
                
            # Release lock on users
            logging.info("Start release lock on all users")
            user_id = 0
            while user_id < num_users:
                user_id += 1
                cursor.execute("release lock sit_ldi_pll_user%s, override" % (user_id))
                        
        # Run run initial checktable for all users from linux client only since ssh won't work with window client yet.
        
          
        if os_type == "Windows":
            logging.info ("Checktable is not running because SSH does not support Window client yet")
        else:
            # create datacheck class instance from common code tdtestpy 
            datacheck_instance = tdtestpy.DataCheck (dbs_name, node_password)            
            user_id = 0
            while user_id < num_users:
                user_id += 1
                user_name = "sit_ldi_pll_user" + str(user_id)
                CheckTableName = "none"
                CheckLevel = "two"
                check_log_name = user_name + "_pretest_checktable.log"
                checktable_log = os.path.join(test_log_path, check_log_name)
                logging.info("Running checktable for user: %s" % (user_name))
                if not datacheck_instance.checktable (user_name, CheckTableName, CheckLevel, checktable_log): 
                    logging.error("Checktable for user %s failed, log file name: %s" % (user_name, checktable_log))
                    tdtestpy.copy_file (checktable_log, failedtask)
                    exit(1)
        # Copy logs to passed if nothing wrong
        tdtestpy.copy_file (test_log_name, passed_dir)
        tdtestpy.copy_file (checktable_log, passed_dir)
        
    except Exception as e:
        logging.error(traceback.format_exc())
        tdtestpy.copy_file (test_log_name, failedtask)
        exit(1)
        
    exit(0)
