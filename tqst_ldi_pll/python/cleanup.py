#!/usr/bin/python3
# Author: tl151006
# File: cleanup.py
# Date Published: 03/25/2016
# Purpose: Run cleanup for LDI and PLL test
# Usage: python cleanup.py --dbs_name=hela --dbc_password=dbc --scriptPath=/tmp --run_timestamp=2016-03-25
import sys
import os
import time
import re
import argparse
import teradata
import errno
import traceback
import logging
import getpass
import platform
os_user_name = getpass.getuser()
os_type = platform.system()
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', '..', 'common'))  
import tdtestpy

common_error = "2631, 3802" #Transaction ABORTed due to deadlock and Database 'abc' does not exist.

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
    parser.add_argument("--dbc_password", required=True, help="DBC password")
    parser.add_argument("--scriptPath", required=True, help="Get current Jmeter test plan path")
    parser.add_argument("--run_timestamp", required=True, help="Get current run time")
    parser.add_argument("--ignore_error", required=False, default=[],
            help="Error number should be ignored. Must be integers separated by commas.", action=IgnoreErrorAction)

    return parser.parse_args()
                
# Python exit wrapper function
def exit(ok=True):
    if ok is True or ok == 0:
        logging.info("================= End: Cleanup Successful!] =================")
        sys.exit(0)
    else:
        logging.info("================== End: Cleanup Failed!] ==================")
        sys.exit(1)

if __name__ == "__main__":


    try:
        
        
        args = setup_argparse()
        
        dbs_name = args.dbs_name
        dbc_password = args.dbc_password
        scriptPath = args.scriptPath
        run_timestamp = args.run_timestamp
        ignore_error = args.ignore_error
        con_method = "odbc"

        udaExec = teradata.UdaExec (appName="CLEANUP", version="1.0", logConsole=True)
        dbc_con = udaExec.connect(method=con_method, system=dbs_name, username= "dbc", password= dbc_password)
        
        # Set logs variables
        cleanup_log_path = os.path.join(scriptPath, "output", dbs_name, run_timestamp, "latest")
        failedtask = os.path.join(scriptPath, "output", dbs_name, run_timestamp, "failed")
        passed_dir = os.path.join(scriptPath, "output", dbs_name, run_timestamp, "passed")
    
        cleanup_log_name = os.path.join(cleanup_log_path, "cleanup.log")
        cleanup_ignore_errors = tdtestpy.get_ignore_errors(common_error) + ignore_error
                
        # dump python log to demo_log_path        
        fh = logging.FileHandler(cleanup_log_name, mode="a", encoding="utf8")
        fh.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
        fh.setLevel(logging.DEBUG)
        root = logging.getLogger()
        root.addHandler(fh) 
        
                        
        logging.info("================== Cleanup Start ==================")
        # Using tdtestpy drop_users function to drop all users start with sitq_ldi_pll_user
        delete_user_with = "sit_ldi_pll_"
        cleanup_task = tdtestpy.DBSaccess (dbc_con)
        
        with dbc_con.cursor() as cursor:            
            cursor.execute ("select UserName from dbc.users where UserName like '%s'" % (delete_user_with + '%'))
            user_list = [item[0] for item in cursor.fetchall()]
            if len(user_list) != 0:
                for user_name in user_list:
                    # Make sure to end ilolated loading just in case TPT for LDI tables failed during test
                    item_inv_eil = user_name.strip() + "_ITEM_INV_LDI"
                    item_inv_plan_eil = user_name.strip() + "_ITEM_INV_PLAN_LDI"
                    item_eil = user_name.strip() + "_ITEM_LDI"
                    return_rea_eil = user_name.strip() + "_RETURN_REASON_LDI"
                    return_trans_line_eil = user_name.strip() + "_RETURN_TRANS_LINE_LDI"
                    cursor.execute("END ISOLATED LOADING FOR QUERY_BAND 'LDILoadGroup=%s;'" % (item_inv_eil), ignoreErrors=[9887])
                    cursor.execute("END ISOLATED LOADING FOR QUERY_BAND 'LDILoadGroup=%s;'" % (item_inv_plan_eil), ignoreErrors=[9887])
                    cursor.execute("END ISOLATED LOADING FOR QUERY_BAND 'LDILoadGroup=%s;'" % (item_eil), ignoreErrors=[9887])
                    cursor.execute("END ISOLATED LOADING FOR QUERY_BAND 'LDILoadGroup=%s;'" % (return_rea_eil), ignoreErrors=[9887])
                    cursor.execute("END ISOLATED LOADING FOR QUERY_BAND 'LDILoadGroup=%s;'" % (return_trans_line_eil), ignoreErrors=[9887]) 
                    if not cleanup_task.drop_user(user_name):
                        logging.error ("Drop user return error")
                        tdtestpy.copy_file (cleanup_log_name, failedtask)
                        exit(1)
        
        # Copy logs to passed if nothing wrong
        tdtestpy.copy_file (cleanup_log_name, passed_dir)
        
    except Exception as e:
        logging.error(traceback.format_exc())
        tdtestpy.copy_file (cleanup_log_name, failedtask)
        exit(1)
        
    exit(0)