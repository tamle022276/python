# Author: tl151006 (tl151006@teradata.com)
# File: using_common_codes.py
# Date Published: 02/09/2016
# Purpose: Demo of how to reuse Teradata UDA common codes module called uda2c
# Usage: python using_common_codes.py --database_name=db_name --user_name=db_user --user_password=db_password --ignore_error=error_1,error_2,error_n
# ignore_error can none to many, it separate by comma and it is optional
# Example 1 with 2 ignore errors: python using_common_codes.py --database_name=hela --user_name=dbc --user_password=dbc --ignore_error=3822,3807
# Example 2 with 1 ignore error: python using_common_codes.py --database_name=hela --user_name=dbc --user_password=dbc --ignore_error=3822
# Example 3 without ignore error: python using_common_codes.py --database_name=hela --user_name=dbc --user_password=dbc
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
python_src = os.path.dirname(os.path.realpath(__file__))
if os_type == "Windows":
    sys.path.append('C:\\Users\\TL151006\\Desktop\\dev\\trunk\\common')
if os_type == "Linux":
    sys.path.append('/qd0056/tl151006/jmeter-svn/common')
if os_user_name == "tomcat":
    sys.path.append(os.path.join(python_src, "common"))
import uda2c

common_error = "2631" #Transaction ABORTed due to deadlock

# parse common_error
def get_common_errors():
    return [int(e.strip()) for e in common_error.split(",") if e.strip()]

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

    parser = argparse.ArgumentParser(description="### bteq_python.py ###")
    parser.add_argument("--database_name", required=True, help="System name")
    parser.add_argument("--user_name", required=True, help="User name")
    parser.add_argument("--user_password", required=True, help="User password")
    parser.add_argument("--ignore_error", required=False, default=[],
            help="Error number should be ignored. Must be integers separated by commas.", action=IgnoreErrorAction)

    return parser.parse_args()

# Python exit wrapper function
def exit(ok=True):
    if ok is True or ok == 0:
        logging.info("================= End: Demo Sucess!] =================")
        sys.exit(0)
    else:
        logging.info("================== End: Demo Fail!] ==================")
        sys.exit(1)

if __name__ == "__main__":


    try:
        udaExec = teradata.UdaExec (appName="UDA2C", version="1.0", logConsole=True)
        
        args = setup_argparse()
        
        database_name = args.database_name
        user_name = args.user_name
        user_password = args.user_password
        ignore_error = args.ignore_error
        con_method = "odbc"
        demo_log_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'demo_log')
        demo_log_name = os.path.join(demo_log_path, "using_common_codes_log.txt")
        bteq_ignore_errors = get_common_errors() + ignore_error
        bteq_errorlevel_set = str(tuple(bteq_ignore_errors)) 
        bteq_template_file = "my_bteq_template.txt"
        #bteq_template_file = "my_bteq_full_logon.txt"
        #bteq_template_file = "my_bteq_just_user.txt"
        
        # Using uda2c ensure_dir function to create demo_log_path if it doesn't exist
        uda2c.ensure_dir(demo_log_path)
        
        # Using uda2c delete_one_file function to delete old log if exist
        uda2c.delete_one_file(demo_log_name)
        
        # dump python log to demo_log_path        
        fh = logging.FileHandler(demo_log_name, mode="a", encoding="utf8")
        fh.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
        fh.setLevel(logging.DEBUG)
        root = logging.getLogger()
        root.addHandler(fh) 
                
        # Using uda2c DBS functions to test Hela and Monopoly
        logging.info("================== DBS Function Testing ==================")
        with udaExec.connect(method=con_method, system=database_name, username=user_name, password=user_password) as monopoly_con:
            monopoly_pde = uda2c.get_pde_release(monopoly_con)
            monopoly_dbs = uda2c.get_dbs_release(monopoly_con)
            monopoly_dbc_currentperm = uda2c.get_db_current_perm(monopoly_con, "DBC")
            monopoly_dbc_maxperm = uda2c.get_db_max_perm(monopoly_con, "DBC")
            monopoly_dbc_freeperm = uda2c.get_db_free_perm(monopoly_con, "DBC")
        
        with udaExec.connect(method=con_method, system="hela", username="dbc", password="dbc") as hela_con:
            hela_pde = uda2c.get_pde_release(hela_con)
            hela_dbs = uda2c.get_dbs_release(hela_con)
            hela_sit_pdm_currentperm = uda2c.get_db_current_perm(hela_con, "SIT_PDM")
            hela_sit_pdm_maxperm = uda2c.get_db_max_perm(hela_con, "SIT_PDM")
            hela_return_tran_line_cur_perm = uda2c.get_table_current_perm(hela_con, "SIT_PDM", "RETURN_TRANSACTION_LINE")
            hela_return_tran_line_row_count = uda2c.get_table_row_count(hela_con, "SIT_PDM", "RETURN_TRANSACTION_LINE") 
            hela_sum_of_refund = uda2c.get_sum_of_a_column(hela_con, "UNIT_REFUND_AMT", "SIT_PDM", "RETURN_TRANSACTION_LINE") 
            hela_sum_of_selling = uda2c.get_sum_of_a_column(hela_con, "UNIT_SELLING_PRICE_AMT", "SIT_PDM", "SALES_TRANSACTION_LINE") 
                                   
        logging.info("================== Return Data For Hela ==================")
        logging.info("Hela SIT PDM CURRENT PERM IS: %s MB" % (hela_sit_pdm_currentperm))
        logging.info("Hela SIT PDM MAX PERM IS: %s MB" % (hela_sit_pdm_maxperm))
        logging.info("Hela SIT PDM RETURN_TRANSACTION_LINE CURRENT PERM IS: %s MB" % (hela_return_tran_line_cur_perm))
        logging.info("Hela SIT PDM RETURN_TRANSACTION_LINE NUMBER OF ROWS IS: %s" % (hela_return_tran_line_row_count))
        logging.info("Hela SUM OF UNIT_REFUND_AMT FROM PDM RETURN_TRANSACTION_LINE IS: %s" % (hela_sum_of_refund))
        logging.info("Hela SUM OF UNIT_SELLING_PRICE_AMT FROM PDM SALES_TRANSACTION_LINE IS: %s" % (hela_sum_of_selling))          
        logging.info("Hela PDE Release is: %s" % (hela_pde))
        logging.info("Hela DBS Release is: %s" % (hela_dbs))
        logging.info("================== Return Data For Monopoly ==================")
        logging.info("Monopoly DBC CURRENT PERM IS: %s MB" % (monopoly_dbc_currentperm))
        logging.info("Monopoly DBC MAX PERM IS: %s MB" % (monopoly_dbc_maxperm))
        logging.info("Monopoly DBC Available PERM IS: %s MB" % (monopoly_dbc_freeperm))
        logging.info("Monopoly PDE Release is: %s" % (monopoly_pde))
        logging.info("Monopoly DBS Release is: %s" % (monopoly_dbs))
        
        # Using uda2c utility function compare_two_values to validate results
        logging.info("==================  Using uda2c utility function compare_two_values to validate results ==================")
        # Passing 2 Hard Code Values
        value1 = "Apple"
        value2 = "Orange"
        if uda2c.compare_two_values(value1, value2):
            logging.info("Yes %s is the same as %s" % (value1, value2))
        else:
            logging.info("Wrong Argument: '%s' is not the same as '%s'" % (value1, value2))
        
        # Passing 1 Hard Code To Compare with 1 Dynamic value
        expect_hela_return_tran_line_row_count = 500000
        if uda2c.compare_two_values(hela_return_tran_line_row_count, expect_hela_return_tran_line_row_count):
            logging.info("Test Passed: Expected %s rows, and returns %s rows" % (expect_hela_return_tran_line_row_count, hela_return_tran_line_row_count))
        else:
            logging.info("Test Failed: Expected %s rows, and returns %s rows" % (expect_hela_return_tran_line_row_count, hela_return_tran_line_row_count))
            
        # Passing 2 Dynamic Values Generated From DBS Functions.
        if uda2c.compare_two_values(hela_sum_of_refund, expect_hela_return_tran_line_row_count):
            logging.info("Test Passed: hela_sum_of_refund (%s), is the same as hela_sum_of_selling (%s)" % (hela_sum_of_refund, hela_sum_of_selling))
        else:
            logging.info("Test Failed: hela_sum_of_refund (%s), is not the same as hela_sum_of_selling (%s)" % (hela_sum_of_refund, hela_sum_of_selling))
     
          
        # Using uda2c utility function get_full_line_if_string_match to get full line from a file if string match
        logging.info("==================  Using uda2c utility function get_full_line_if_string_match to get full line from a file if string match ==================")
        if not uda2c.get_full_line_if_string_match(bteq_template_file, "SET ERRORLEVEL"):
            logging.error('Your string "SET ERRORLEVEL" is not in %s, please investigate' % (bteq_template_file))
            exit(1)
        else:
            original_error_level_set = uda2c.get_full_line_if_string_match(bteq_template_file, "SET ERRORLEVEL")
            new_error_level_set = '.SET ERRORLEVEL ' + bteq_errorlevel_set + ' SEVERITY 0' 
            logging.info("original_error_level_set is %s" % (original_error_level_set))
            logging.info("new_error_level_set is %s" % (new_error_level_set))
        
        # Using uda2c utility function convert_a_template to convert original template to new file
        logging.info("==================  Using uda2c utility function convert_my_template to convert original template to new file ==================")
        new_bteq_template_file = database_name + "_new_" + bteq_template_file   
        replace_items =  {original_error_level_set:new_error_level_set}
        uda2c.convert_a_template(bteq_template_file, new_bteq_template_file, replace_items)
        
        # Using uda2c subprocess functions to call bteq and validate results
        logging.info("==================  Using uda2c subprocess functions to call bteq and validate results ==================")
        bteq_log_file = database_name + "_bteq_output.txt"
        bteq_run_result, bteq_errors_that_not_ignore = uda2c.run_bteq(new_bteq_template_file, bteq_log_file, \
                                                                      database_name, user_name, user_password, bteq_ignore_errors)
        #bteq_run_result, bteq_errors_that_not_ignore = uda2c.run_bteq(new_bteq_template_file, bteq_log_file, \
        #                                                              "", "", " ", bteq_ignore_errors)
        #bteq_run_result, bteq_errors_that_not_ignore = uda2c.run_bteq(new_bteq_template_file, bteq_log_file, \
        #                                                              database_name, "", "", bteq_ignore_errors)
        if not bteq_run_result:
            logging.info("Bteq Passed")
        else:
            logging.error("Bteq errors found that can not be ignored: %s, please check out this log file: %s" % (bteq_errors_that_not_ignore, bteq_log_file))
                    
        # Using uda2c subprocess and utility functions to call tpt export, load and validate results
        logging.info("==================  Using uda2c subprocess and utility functions to call tpt export ==================")
        # Shared TPT export and load parameters
        directory_path = os.path.dirname(os.path.realpath(__file__)) # Current directory
        database_name = "hela"
        user_name = "sitq_ldi_pll_user1"
        user_password = "sitq_ldi_pll_user1"
        dump_file_name = "data1.dat"
        tracelevel = "none"
        # TPT export parameters
        tpt_export_file = "tpt_export.tpt"
        export_log = "tpt_export_output.log"
        # TPT load parameters
        tpt_load_file = "tpt_load.tpt"
        load_log = "tpt_load_output.log"
        # Run TPT using flat file on window
        if os_type == "Windows":
            if not uda2c.run_single_tpt(tpt_export_file, export_log, directory_path, database_name, user_name, \
                                 user_password, dump_file_name, tracelevel):
                logging.error("TPT Export Failed: Please check out this log file: %s" % (export_log))
            else:
                logging.info("TPT Export Passed")
            
            logging.info("==================  Using uda2c subprocess and utility functions to call tpt load ==================")

            if not uda2c.run_single_tpt(tpt_load_file, load_log, directory_path, database_name, user_name, \
                                 user_password, dump_file_name, tracelevel):
                logging.error("TPT Load Failed: Please check out this log file: %s" % (load_log))
            else:
                logging.info("TPT Load Passed")   
        
        # Run TPT using named pipe on linux
        if os_type == "Linux":
            tpt_named_pipe = user_name + "_" + "return_trans_line"

            tpt_export_result, tpt_load_result = uda2c.run_tpt_named_pipe(tpt_export_file, export_log, tpt_load_file, \
                                                                          load_log, directory_path, database_name, user_name, \
                                                                          user_password, tpt_named_pipe, tracelevel)
            if not tpt_export_result:
                logging.error("TPT Export Failed: Please check out this log file: %s" % (export_log))
            else:
                logging.info("TPT Export Passed")
            if not tpt_load_result:
                logging.error("TPT Load Failed: Please check out this log file: %s" % (load_log))
            else:
                logging.info("TPT Load Passed")
       
        # Using uda2c utility function scan_files_extension to scan all log files extension for error message 
        logging.info("==================  Using uda2c utility function scan_files_extension to scan all log files extension for error message  ==================")
        path_with_extension = os.path.join(python_src, '*.log')
        what_to_scan = "terminated"
        if not uda2c.scan_files_extension(path_with_extension, what_to_scan):
            logging.error('Test Failed: Found "terminated" message')
        else:
            logging.info('Test Passed: No "terminated" message found')
            
    except Exception as e:
        logging.error(traceback.format_exc())
        exit(1)
        
    exit(0)
