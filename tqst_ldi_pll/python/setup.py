#!/usr/bin/python3
# Author: tl151006
# File: setup.py
# Date Published: 03/25/2016
# Purpose: Run setup for LDI and PLL test
# Usage: python setup.py --dbs_name=hela --num_users=5 --dbc_password=dbc --scriptPath=/tmp --run_timestamp=2016-03-25

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
import threading, queue
import multiprocessing
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
    parser.add_argument("--scriptPath", required=True, help="Get current Jmeter test plan path")
    parser.add_argument("--run_timestamp", required=True, help="Get current run time")
    parser.add_argument("--ignore_error", required=False, default=[],
            help="Error number should be ignored. Must be integers separated by commas.", action=IgnoreErrorAction)

    return parser.parse_args()
# Run sql file in multiple threads.         
def run_sql_file_MultipleThreads(input_queries, num_jobs, ignore_errors):
    threadCount = num_jobs
    threads = []
    for i in range(1, threadCount + 1):
        run_result = queue.Queue()
        user_name = "sit_ldi_pll_user" + str(i)
        conn = udaExec.connect(method=con_method, system=dbs_name, username=user_name, password=user_name)
        t = threading.Thread(
            target=run_sql_file, args=(conn, input_queries, ignore_errors, run_result))
        t.daemon = True
        threads.append(t)
        t.start()
    for t in threads:
        t.join()
    if not run_result.get():
        return False
    else:
        return True
 
# Run sql file
def run_sql_file(db_connect, input_sql_file, ignore_errors, run_result=None):
    try:
        with db_connect.cursor() as cursor:
            cursor.execute(file=input_sql_file, ignoreErrors=ignore_errors)
    except Exception as e:
        if run_result is None:
            return False
        else:
            run_result.put(False)
    if run_result is None:
        return True
    else:
        run_result.put(True)
           
# Python exit wrapper function
def exit(ok=True):
    if ok is True or ok == 0:
        logging.info("================= End: Setup completed successful!] =================")
        sys.exit(0)
    else:
        logging.info("================== End: Setup completed with failure!] ==================")
        sys.exit(1)

if __name__ == "__main__":
    try:
        udaExec = teradata.UdaExec (appName="SETUP", version="1.0", logConsole=True)
        args = setup_argparse()
        dbs_name = args.dbs_name
        num_users = int(args.num_users)
        dbc_password = args.dbc_password
        scriptPath = args.scriptPath
        run_timestamp = args.run_timestamp
        ignore_error = args.ignore_error
        con_method = "odbc"
        stage_queries_file = os.path.join(scriptPath, "sql", "setup_stage.txt")
        setup_queries_file = os.path.join(scriptPath, "sql", "setup_ddl.txt")
        setup_insert_select_file = os.path.join(scriptPath, "sql", "setup_insert_select.txt")
        
        # Set logs variables
        setup_log_path = os.path.join(scriptPath, "output", dbs_name, run_timestamp, "latest")
        failedtask = os.path.join(scriptPath, "output", dbs_name, run_timestamp, "failed")
        passed_dir = os.path.join(scriptPath, "output", dbs_name, run_timestamp, "passed")
        setup_log_name = os.path.join(setup_log_path, "setup.log")
        setup_ignore_errors = tdtestpy.get_ignore_errors(common_error) + ignore_error

        
        # dump python log to demo_log_path        
        fh = logging.FileHandler(setup_log_name, mode="a", encoding="utf8")
        fh.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
        fh.setLevel(logging.DEBUG)
        root = logging.getLogger()
        root.addHandler(fh) 
                
        logging.info("================== Main Setup Starts ==================")
        setup_con = udaExec.connect(method=con_method, system=dbs_name, username= "dbc", password= dbc_password)
                
        source_db = "sit_pdm"
        dbaccess_instance = tdtestpy.DBSaccess (setup_con)

        # Check see if sit_pdm exist and exit if it is not.
        if not dbaccess_instance.is_database_exist (source_db):
            logging.error("SIT_PDM does not exists, please run SIT_SEA setup first before running setup for this test")
            tdtestpy.copy_file (setup_log_name, failedtask)
            exit(1)
        
        # Check see if DBC has enough space to run setup based on number of users provided.
        sit_pdm_current_perm = dbaccess_instance.get_db_current_perm (source_db)
        # Number of user plus one for stage database.
        total_perm_required = (sit_pdm_current_perm * 3) * (num_users + 1)
        dbc_free_perm = dbaccess_instance.get_db_free_perm ("dbc")
        if dbc_free_perm < total_perm_required:
            logging.error ("DBC does not have enough space to run setup for %s users" % (num_users))
            logging.info ("DBC Free perm is: %s" % (dbc_free_perm))
            logging.info ("Sit PDM current perm is: %s" % (sit_pdm_current_perm))
            logging.info ("Total perm required is equal sit_pdm_current_perm * num_users is: %s" % (total_perm_required))
            logging.info ("So please lower num_users and try again")
            tdtestpy.copy_file (setup_log_name, failedtask)
            exit(1)
        
        # Create stage user and begin query logging.
        logging.info("Start create stage user and loading data from sit_pdm")
        stage_user = "sit_ldi_pll_stage"
        perm = sit_pdm_current_perm * 3
        with setup_con.cursor() as cursor:
            cursor.execute("create user %s as perm = %s, password = %s" % (stage_user, perm, stage_user), ignoreErrors=setup_ignore_errors)
            cursor.execute("grant all on sit_pdm to %s with grant option" % (stage_user))
            cursor.execute("BEGIN QUERY LOGGING WITH SQL, STEPINFO, XMLPLAN, LOCK=100, FEATUREINFO ON %s" % (stage_user))
            
        # Create ALL other users and begin query logging.
        logging.info("Start create users and begin query logging")
        with setup_con.cursor() as cursor:
            user_id = 0
            while user_id < num_users:
                user_id += 1
                cursor.execute("create user sit_ldi_pll_user%s as perm = %s, password = sit_ldi_pll_user%s" % \
                               (user_id, perm, user_id), ignoreErrors=setup_ignore_errors)
                cursor.execute("grant all on %s to sit_ldi_pll_user%s with grant option" % (stage_user, user_id))
                cursor.execute("BEGIN QUERY LOGGING WITH SQL, STEPINFO, XMLPLAN, LOCK=100, FEATUREINFO ON sit_ldi_pll_user%s" % (user_id))
               
                
        # Create DDL for sit_stage and move data from SIT_PDM over
        with udaExec.connect(method=con_method, system=dbs_name, username=stage_user, password=stage_user) as setup_stage_con:
            logging.info ("Create DDL for sit_stage and move data from SIT_PDM over")
            if not run_sql_file(setup_stage_con, stage_queries_file, setup_ignore_errors):
                tdtestpy.copy_file (setup_log_name, failedtask)
                exit(1)
            
        """
        # Create DDL for ALL users one by one.
        user_id = 0
        while user_id < num_users:
            user_id += 1
            user_name = "sit_ldi_pll_user" + str(user_id)
            with udaExec.connect(method=con_method, system=dbs_name, username=user_name, password=user_name) as ddl_con:
                logging.info ("Create DDL for user: %s started" % (user_name))
                if not run_sql_file(ddl_con, setup_queries_file, setup_ignore_errors):
                    tdtestpy.copy_file (setup_log_name, failedtask)
                    exit(1)
                logging.info ("Created DDL for user %s completed successful" % (user_name))
                logging.info ("Insert data from stage database to user: %s started" % (user_name))
                if not run_sql_file(ddl_con, setup_insert_select_file, setup_ignore_errors):
                    tdtestpy.copy_file (setup_log_name, failedtask)
                    exit(1)
                logging.info ("Insert data from stage database to user %s completed successful" % (user_name))
        """        
        # Create DDL for ALL users in parallel        
        logging.info ("Create DDL for ALL users in parallel")
        if not run_sql_file_MultipleThreads(setup_queries_file, num_users, setup_ignore_errors):
            exit(1)
         
        # Insert data from stage database to ALL users in parallel
        logging.info ("Insert data from stage database to ALL users in parallel")
        if not run_sql_file_MultipleThreads(setup_insert_select_file, num_users, setup_ignore_errors):
            tdtestpy.copy_file (setup_log_name, failedtask)
            exit(1)    
        
        # Copy logs to passed if nothing wrong
        tdtestpy.copy_file (setup_log_name, passed_dir)
               
    except Exception as e:
        logging.error(traceback.format_exc())
        tdtestpy.copy_file (setup_log_name, failedtask)
        exit(1)
        
    exit(0)
