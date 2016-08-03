#!/usr/bin/python3
# Author: tl151006
# File: pll_tables_write.py
# Date Published: 05/13/2016
# Purpose: Run DML on PLL tables
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
import random
os_user_name = getpass.getuser()
os_type = platform.system()
#if os_user_name == "tomcat":
#    sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'common'))
#else:
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', '..', 'common')) 
import tdtestpy

common_error = "2631, 2641" #Transaction ABORTed due to deadlock and restructured

# Group 1
def run_dml_transaction1(dbs_name, user_name, ignore_errors, run_result=None):
    try:
        with udaExec.connect(method="odbc", system=dbs_name, username=user_name, password=user_name) as db_connect:
            with db_connect.cursor() as cursor:
                
                # SALES_TRANSACTION_PLL table
                cursor.execute("delete SALES_TRANSACTION_PLL where TRAN_DATE between '1970-01-01' and '1980-01-01'", ignoreErrors=ignore_errors)
                
                logging.info ("TPT export for sale_trans_pll started")
                if not tdtestpy.run_single_tpt(sale_trans_pll_export_file, sale_trans_pll_export_log, directory_path, \
                                       dbs_name, user_name, user_name, sale_trans_pll_data_file, tracelevel):
                    msg = "TPT export for sale_trans_pll failed, please review " + sale_trans_pll_export_log
                    logging.info ("TPT export for sale_trans_pll completed with failure")
                    tdtestpy.copy_file (sale_trans_pll_export_log, faileddir)
                    
                    if run_result is None:
                        return msg
                    else:
                        run_result.put(msg)
                            
                logging.info ("TPT export for sale_trans_pll completed successful")
                tdtestpy.copy_file (sale_trans_pll_export_log, passed_dir)
                
                logging.info ("TPT stream for sale_trans_pll started")
                if not tdtestpy.run_single_tpt(sale_trans_pll_stream_file, sale_trans_pll_stream_log, directory_path, \
                                       dbs_name, user_name, user_name, sale_trans_pll_data_file, tracelevel):
                    msg = "TPT stream for sale_trans_pll failed, please review " + sale_trans_pll_stream_log
                    logging.info ("TPT stream for sale_trans_pll completed with failure")
                    tdtestpy.copy_file (sale_trans_pll_stream_log, faileddir)
                                        
                    if run_result is None:
                        return msg
                    else:
                        run_result.put(msg)
                        
                    
                logging.info ("TPT stream for sale_trans_pll completed successful")
                tdtestpy.copy_file (sale_trans_pll_stream_log, passed_dir)
                
                # Delete data file if TPT export and stream ran successful
                tdtestpy.delete_one_file (sale_trans_pll_data_file_full_path)
                
                     
                # SALES_TRANSACTION_LINE_PLL table
                cursor.execute("update SALES_TRANSACTION_LINE_PLL set TRAN_LINE_DATE = current_date, UNIT_COST_AMT = 12.10 \
                where LOCATION < 50", ignoreErrors=ignore_errors)
                cursor.execute("delete SALES_TRANSACTION_LINE_PLL where LOCATION < 50", ignoreErrors=ignore_errors) 
                cursor.execute("insert into SALES_TRANSACTION_LINE_PLL select * from sit_ldi_pll_stage.SALES_TRANSACTION_LINE_PLL \
                where LOCATION < 50", ignoreErrors=ignore_errors)
                
                # PARTY_PLL table
                cursor.execute("delete PARTY_PLL where PARTY_STATE BETWEEN 'A' AND 'B'", ignoreErrors=ignore_errors) 
                cursor.execute("insert into PARTY_PLL select * from sit_ldi_pll_stage.PARTY_PLL \
                where PARTY_STATE BETWEEN 'A' AND 'B'", ignoreErrors=ignore_errors)
                
                # LOCATION_PLL table
                cursor.execute("delete LOCATION_PLL where LOCATION_EFFECTIVE_DT < '1980-01-01'", ignoreErrors=ignore_errors)
                cursor.execute("insert into LOCATION_PLL select * from sit_ldi_pll_stage.LOCATION_PLL \
                where LOCATION_EFFECTIVE_DT < '1980-01-01'", ignoreErrors=ignore_errors) 
                    
    except Exception as e:
        if run_result is None:
            return str(e)
        else:
            run_result.put(str(e))
    if run_result is None:
        return True
    else:
        run_result.put(True)
        
        
# Create function that runs DML statements for ITEM_INVENTORY_LDI table
def run_dml_transaction2(dbs_name, user_name, ignore_errors, run_result=None):
    try:
        with udaExec.connect(method="odbc", system=dbs_name, username=user_name, password=user_name) as db_connect:
            with db_connect.cursor() as cursor:
                # SALES_TRANSACTION_PLL table
                cursor.execute("update SALES_TRANSACTION_PLL set TRANS_YEAR = '2016', TRAN_TYPE_CD = 'T' \
                where TRAN_DATE between '1980-02-01' and '1990-01-01'", ignoreErrors=ignore_errors) 
                cursor.execute("delete SALES_TRANSACTION_PLL where TRAN_DATE between '1980-02-01' and '1990-01-01'", ignoreErrors=ignore_errors)
                cursor.execute("insert into SALES_TRANSACTION_PLL select * from sit_ldi_pll_stage.SALES_TRANSACTION_PLL \
                where TRAN_DATE between '1980-02-01' and '1990-01-01'", ignoreErrors=ignore_errors)
                
                
                # SALES_TRANSACTION_LINE_PLL table
                cursor.execute("delete SALES_TRANSACTION_LINE_PLL where LOCATION > 480", ignoreErrors=ignore_errors)
                
                logging.info ("TPT export for sale_trans_line_pll started")
                if not tdtestpy.run_single_tpt(sale_trans_line_pll_export_file, sale_trans_line_pll_export_log, directory_path, \
                                       dbs_name, user_name, user_name, sale_trans_line_pll_data_file, tracelevel):
                    msg = "TPT export for sale_trans_line_pll failed, please review " + sale_trans_line_pll_export_log
                    logging.info ("TPT export for sale_trans_line_pll completed with failure")
                    tdtestpy.copy_file (sale_trans_line_pll_export_log, faileddir)
                    
                    if run_result is None:
                        return msg
                    else:
                        run_result.put(msg)
                    
                    
                logging.info ("TPT export for sale_trans_line_pll completed successful")
                tdtestpy.copy_file (sale_trans_line_pll_export_log, passed_dir)
                
                logging.info ("TPT stream for sale_trans_line_pll started")
                if not tdtestpy.run_single_tpt(sale_trans_line_pll_stream_file, sale_trans_line_pll_stream_log, directory_path, \
                                       dbs_name, user_name, user_name, sale_trans_line_pll_data_file, tracelevel):
                    msg = "TPT stream for sale_trans_line_pll failed, please review " + sale_trans_line_pll_stream_log
                    logging.info ("TPT stream for sale_trans_line_pll completed with failure")
                    tdtestpy.copy_file (sale_trans_line_pll_stream_log, faileddir)
                    
                    if run_result is None:
                        return msg
                    else:
                        run_result.put(msg)
                                        
                logging.info ("TPT stream for sale_trans_line_pll completed successful")
                tdtestpy.copy_file (sale_trans_line_pll_stream_log, passed_dir)
                # Delete data file if TPT export and stream ran successful
                tdtestpy.delete_one_file (sale_trans_line_pll_data_file_full_path)
                
                # PARTY_PLL table
                cursor.execute("delete PARTY_PLL where PARTY_STATE BETWEEN 'C' AND 'K' \
                and PARTY_START_DT < '2012-01-01'", ignoreErrors=ignore_errors)
                cursor.execute("update PARTY_PLL set PARTY_START_DT = '2016-01-01' \
                where PARTY_STATE BETWEEN 'C' AND 'K'", ignoreErrors=ignore_errors) 
                cursor.execute("MERGE into PARTY_PLL as t1 \
                using (select * from sit_ldi_pll_stage.PARTY_PLL where PARTY_STATE BETWEEN 'C' AND 'K') as t2  \
                on t1.PARTY_ID = t2.PARTY_ID \
                and t1.PARTY_STATE = t2.PARTY_STATE \
                and t1.PARTY_CITY = t2.PARTY_CITY \
                WHEN MATCHED THEN \
                UPDATE SET PARTY_START_DT = t2.PARTY_START_DT \
                WHEN NOT MATCHED THEN \
                insert (PARTY_ID, PARTY_TYPE_CD, PARTY_FIRSTNAME, PARTY_LASTNAME, PARTY_STREET_ADDRESS, \
                PARTY_CITY, PARTY_STATE, PARTY_ZIP, PARTY_INFO_SOURCE_TYPE_CD, PARTY_START_DT, \
                PARTY_FIRST_PURCHASE_DT, LOCATION_POINT, ACTIVE_AREA, ACTIVE_LINES, KEY_LINE, KEY_POINTS, ALL_RELATED_GEO) \
                values (t2.PARTY_ID, t2.PARTY_TYPE_CD, t2.PARTY_FIRSTNAME, t2.PARTY_LASTNAME, t2.PARTY_STREET_ADDRESS, \
                t2.PARTY_CITY, t2.PARTY_STATE, t2.PARTY_ZIP, t2.PARTY_INFO_SOURCE_TYPE_CD, t2.PARTY_START_DT, \
                t2.PARTY_FIRST_PURCHASE_DT, t2.LOCATION_POINT, t2.ACTIVE_AREA, t2.ACTIVE_LINES, t2.KEY_LINE, \
                t2.KEY_POINTS, t2.ALL_RELATED_GEO)", ignoreErrors=ignore_errors)
                
                # LOCATION_PLL table
                cursor.execute("update LOCATION_PLL set CHAIN_CD = 'This is test' \
                where LOCATION_EFFECTIVE_DT between '1980-02-01' and '1990-01-01'", ignoreErrors=ignore_errors)
                cursor.execute("delete LOCATION_PLL where LOCATION_EFFECTIVE_DT between '1980-02-01' and '1990-01-01'", ignoreErrors=ignore_errors)               
                cursor.execute("insert into LOCATION_PLL select * from sit_ldi_pll_stage.LOCATION_PLL \
                where LOCATION_EFFECTIVE_DT between '1980-02-01' and '1990-01-01'", ignoreErrors=ignore_errors) 
                
                
                
                
    except Exception as e:
        if run_result is None:
            return str(e)
        else:
            run_result.put(str(e))
    if run_result is None:
        return True
    else:
        run_result.put(True)
        
# Create function that runs DML statements for RETURN_TRANSACTION_LINE_LDI table
def run_dml_transaction3(dbs_name, user_name, ignore_errors, run_result=None):
    try:
        with udaExec.connect(method="odbc", system=dbs_name, username=user_name, password=user_name) as db_connect:
            with db_connect.cursor() as cursor:
                # SALES_TRANSACTION_PLL table
                cursor.execute("update SALES_TRANSACTION_PLL set VISIT_ID = 123, TRAN_STATUS_CD = 'T' \
                where TRAN_DATE between '1990-02-01' and '2000-01-01'", ignoreErrors=ignore_errors)  
                cursor.execute("delete SALES_TRANSACTION_PLL where TRAN_DATE between '1990-02-01' and '2000-01-01'", ignoreErrors=ignore_errors)
                cursor.execute("insert into SALES_TRANSACTION_PLL select * from sit_ldi_pll_stage.SALES_TRANSACTION_PLL \
                where TRAN_DATE between '1990-02-01' and '2000-01-01'", ignoreErrors=ignore_errors)
                
                
                # SALES_TRANSACTION_LINE_PLL table
                cursor.execute("update SALES_TRANSACTION_LINE_PLL set TRAN_LINE_DATE = '2016-05-11', UNIT_COST_AMT = 13.10 \
                where LOCATION between 210 and 240", ignoreErrors=ignore_errors)
                cursor.execute("delete SALES_TRANSACTION_LINE_PLL where LOCATION between 210 and 240", ignoreErrors=ignore_errors) 
                cursor.execute("insert into SALES_TRANSACTION_LINE_PLL select * from sit_ldi_pll_stage.SALES_TRANSACTION_LINE_PLL \
                where LOCATION between 210 and 240", ignoreErrors=ignore_errors)
                
                # PARTY_PLL table
                cursor.execute("update PARTY_PLL set PARTY_START_DT = '2015-01-01' \
                where PARTY_STATE BETWEEN 'L' AND 'M'", ignoreErrors=ignore_errors) 
                cursor.execute("MERGE into PARTY_PLL as t1 \
                using (select * from sit_ldi_pll_stage.PARTY_PLL where PARTY_STATE BETWEEN 'L' AND 'M') as t2  \
                on t1.PARTY_ID = t2.PARTY_ID \
                and t1.PARTY_STATE = t2.PARTY_STATE \
                and t1.PARTY_CITY = t2.PARTY_CITY \
                WHEN MATCHED THEN \
                UPDATE SET PARTY_START_DT = t2.PARTY_START_DT \
                WHEN NOT MATCHED THEN \
                insert (PARTY_ID, PARTY_TYPE_CD, PARTY_FIRSTNAME, PARTY_LASTNAME, PARTY_STREET_ADDRESS, \
                PARTY_CITY, PARTY_STATE, PARTY_ZIP, PARTY_INFO_SOURCE_TYPE_CD, PARTY_START_DT, \
                PARTY_FIRST_PURCHASE_DT, LOCATION_POINT, ACTIVE_AREA, ACTIVE_LINES, KEY_LINE, KEY_POINTS, ALL_RELATED_GEO) \
                values (t2.PARTY_ID, t2.PARTY_TYPE_CD, t2.PARTY_FIRSTNAME, t2.PARTY_LASTNAME, t2.PARTY_STREET_ADDRESS, \
                t2.PARTY_CITY, t2.PARTY_STATE, t2.PARTY_ZIP, t2.PARTY_INFO_SOURCE_TYPE_CD, t2.PARTY_START_DT, \
                t2.PARTY_FIRST_PURCHASE_DT, t2.LOCATION_POINT, t2.ACTIVE_AREA, t2.ACTIVE_LINES, t2.KEY_LINE, \
                t2.KEY_POINTS, t2.ALL_RELATED_GEO)", ignoreErrors=ignore_errors)
                
                # LOCATION_PLL table
                cursor.execute("delete LOCATION_PLL where LOCATION_EFFECTIVE_DT > '2000-02-01'", ignoreErrors=ignore_errors)
                
                logging.info ("TPT export for location_pll started")
                if not tdtestpy.run_single_tpt(location_pll_export_file, location_pll_export_log, directory_path, \
                                       dbs_name, user_name, user_name, location_pll_data_file, tracelevel):
                    msg = "TPT export for location_pll failed, please review " + location_pll_export_log
                    logging.info ("TPT export for location_pll completed with failure")
                    tdtestpy.copy_file (location_pll_export_log, faileddir)
                    
                    if run_result is None:
                        return msg
                    else:
                        run_result.put(msg)
                     
                logging.info ("TPT export for location_pll completed successful")
                tdtestpy.copy_file (location_pll_export_log, passed_dir)
                
                logging.info ("TPT stream for location_pll started")
                if not tdtestpy.run_single_tpt(location_pll_stream_file, location_pll_stream_log, directory_path, \
                                       dbs_name, user_name, user_name, location_pll_data_file, tracelevel):
                    msg = "TPT stream for location_pll failed, please review " + location_pll_stream_log
                    logging.info ("TPT stream for location_pll completed with failure")
                    tdtestpy.copy_file (location_pll_stream_log, faileddir)
                    
                    if run_result is None:
                        return msg
                    else:
                        run_result.put(msg)
                    
                logging.info ("TPT stream for location_pll completed successful")
                tdtestpy.copy_file (location_pll_stream_log, passed_dir)
                
                # Delete data file if TPT export and stream ran successful
                tdtestpy.delete_one_file (location_pll_data_file_full_path)
                
                
    except Exception as e:
        if run_result is None:
            return str(e)
        else:
            run_result.put(str(e))
    if run_result is None:
        return True
    else:
        run_result.put(True)

# Create function that runs DML statements for item_ldi table 
def run_dml_transaction4(dbs_name, user_name, ignore_errors, run_result=None):
    try:
        with udaExec.connect(method="odbc", system=dbs_name, username=user_name, password=user_name) as db_connect:
            with db_connect.cursor() as cursor:
                # SALES_TRANSACTION_PLL table
                cursor.execute("insert into SALES_TRANSACTION_PLL select * from sit_ldi_pll_stage.SALES_TRANSACTION_PLL \
                where TRAN_DATE > '2010-01-01'", ignoreErrors=ignore_errors) 
                cursor.execute("update SALES_TRANSACTION_PLL set VISIT_ID = 123, TRAN_STATUS_CD = 'T' \
                where TRAN_DATE > '2010-01-01'", ignoreErrors=ignore_errors)
                cursor.execute("delete SALES_TRANSACTION_PLL where TRAN_DATE > '2010-01-01'", ignoreErrors=ignore_errors)
                cursor.execute("insert into SALES_TRANSACTION_PLL select * from sit_ldi_pll_stage.SALES_TRANSACTION_PLL \
                where TRAN_DATE > '2010-01-01'", ignoreErrors=ignore_errors) 
                
                
                # SALES_TRANSACTION_LINE_PLL table
                cursor.execute("delete SALES_TRANSACTION_LINE_PLL where LOCATION between 331 and 350", ignoreErrors=ignore_errors) 
                cursor.execute("insert into SALES_TRANSACTION_LINE_PLL select * from sit_ldi_pll_stage.SALES_TRANSACTION_LINE_PLL \
                where LOCATION between 331 and 350", ignoreErrors=ignore_errors)
                
                # PARTY_PLL table
                cursor.execute("delete PARTY_PLL where PARTY_STATE = 'N'", ignoreErrors=ignore_errors)
                logging.info ("TPT export for party_pll started")
                if not tdtestpy.run_single_tpt(party_pll_export_file, party_pll_export_log, directory_path, \
                                       dbs_name, user_name, user_name, party_pll_data_file, tracelevel):
                    msg = "TPT export for party_pll failed, please review " + party_pll_export_log
                    logging.info ("TPT export for party_pll completed with failure")
                    tdtestpy.copy_file (party_pll_export_log, faileddir)
                    
                    if run_result is None:
                        return msg
                    else:
                        run_result.put(msg)
                    
                logging.info ("TPT export for party_pll completed successful")
                tdtestpy.copy_file (party_pll_export_log, passed_dir)
                
                logging.info ("TPT stream for party_pll started")
                if not tdtestpy.run_single_tpt(party_pll_stream_file, party_pll_stream_log, directory_path, \
                                       dbs_name, user_name, user_name, party_pll_data_file, tracelevel):
                    msg = "TPT stream for party_pll failed, please review " + party_pll_stream_log
                    logging.info ("TPT stream for party_pll completed with failure")
                    tdtestpy.copy_file (party_pll_stream_log, faileddir)
                    
                    if run_result is None:
                        return msg
                    else:
                        run_result.put(msg)
                    
                logging.info ("TPT stream for party_pll completed successful")
                tdtestpy.copy_file (party_pll_stream_log, passed_dir)
                
                # Delete data file if TPT export and stream ran successful
                tdtestpy.delete_one_file (party_pll_data_file_full_path)
                
                cursor.execute("MERGE into PARTY_PLL as t1 \
                using (select * from sit_ldi_pll_stage.PARTY_PLL where PARTY_STATE in ('N', 'O', 'P', 'S', 'T', 'W')) as t2  \
                on t1.PARTY_ID = t2.PARTY_ID \
                and t1.PARTY_STATE = t2.PARTY_STATE \
                and t1.PARTY_CITY = t2.PARTY_CITY \
                WHEN MATCHED THEN \
                UPDATE SET LOCATION_POINT = t2.LOCATION_POINT, ACTIVE_AREA = t2.ACTIVE_AREA, ACTIVE_LINES = t2.ACTIVE_LINES,\
                KEY_LINE = t2.KEY_LINE, KEY_POINTS = t2.KEY_POINTS, ALL_RELATED_GEO = t2.ALL_RELATED_GEO \
                WHEN NOT MATCHED THEN \
                insert (PARTY_ID, PARTY_TYPE_CD, PARTY_FIRSTNAME, PARTY_LASTNAME, PARTY_STREET_ADDRESS, \
                PARTY_CITY, PARTY_STATE, PARTY_ZIP, PARTY_INFO_SOURCE_TYPE_CD, PARTY_START_DT, \
                PARTY_FIRST_PURCHASE_DT, LOCATION_POINT, ACTIVE_AREA, ACTIVE_LINES, KEY_LINE, KEY_POINTS, ALL_RELATED_GEO) \
                values (t2.PARTY_ID, t2.PARTY_TYPE_CD, t2.PARTY_FIRSTNAME, t2.PARTY_LASTNAME, t2.PARTY_STREET_ADDRESS, \
                t2.PARTY_CITY, t2.PARTY_STATE, t2.PARTY_ZIP, t2.PARTY_INFO_SOURCE_TYPE_CD, t2.PARTY_START_DT, \
                t2.PARTY_FIRST_PURCHASE_DT, t2.LOCATION_POINT, t2.ACTIVE_AREA, t2.ACTIVE_LINES, t2.KEY_LINE, \
                t2.KEY_POINTS, t2.ALL_RELATED_GEO)", ignoreErrors=ignore_errors) 
                
                # LOCATION_PLL table
                cursor.execute("update LOCATION_PLL set CHANNEL_CD = '12345',  CHAIN_CD = 'ABCD', DISTRICT_CD = '456789' \
                where LOCATION_EFFECTIVE_DT between '1990-02-01' and '2000-01-01'", ignoreErrors=ignore_errors)
                cursor.execute("delete LOCATION_PLL where LOCATION_EFFECTIVE_DT between '1990-02-01' and '2000-01-01'", ignoreErrors=ignore_errors)               
                cursor.execute("insert into LOCATION_PLL select * from sit_ldi_pll_stage.LOCATION_PLL \
                where LOCATION_EFFECTIVE_DT between '1990-02-01' and '2000-01-01'", ignoreErrors=ignore_errors)
                
                
    except Exception as e:
        if run_result is None:
            return str(e)
        else:
            run_result.put(str(e))
    if run_result is None:
        return True
    else:
        run_result.put(True)  

# Run all DML functions in parallel        
def run_dml_parallel(dbs_name, user_name, ignore_errors):
    run_dml_transaction1_result = queue.Queue()
    run_dml_transaction2_result = queue.Queue()
    run_dml_transaction3_result = queue.Queue()
    run_dml_transaction4_result = queue.Queue()
            
    t1 = threading.Thread(target=run_dml_transaction1, args=(dbs_name, user_name, ignore_errors, run_dml_transaction1_result))
       
    t2 = threading.Thread(target=run_dml_transaction2, args=(dbs_name, user_name, ignore_errors, run_dml_transaction2_result))
    
    t3 = threading.Thread(target=run_dml_transaction3, args=(dbs_name, user_name, ignore_errors, run_dml_transaction3_result))
    
    t4 = threading.Thread(target=run_dml_transaction4, args=(dbs_name, user_name, ignore_errors, run_dml_transaction4_result))
    
    #t1.daemon = True
    #t2.daemon = True
    #t3.daemon = True
    #t4.daemon = True
    
    t1.start()
    t2.start()
    t3.start()
    t4.start()
    
    t1.join()
    t2.join()
    t3.join()
    t4.join()
    
    return run_dml_transaction1_result.get(), run_dml_transaction2_result.get(), \
        run_dml_transaction3_result.get(), run_dml_transaction4_result.get()


# Reading input arguments function
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
    parser.add_argument("--scriptPath", required=True, help="Get current Jmeter test plan path")
    parser.add_argument("--run_timestamp", required=True, help="Get current run time")
    parser.add_argument("--user_name", required=True, help="User name")
    parser.add_argument("--node_password", required=False, default='Sit4me123!', help="root password")
    parser.add_argument("--tpt_trace_level", required=False, default='none', help="tpt_trace_level")
    parser.add_argument("--ignore_error", required=False, default=[],
            help="Error number should be ignored. Must be integers separated by commas.", action=IgnoreErrorAction)

    return parser.parse_args()
              
# Python exit wrapper function
def exit(ok=True):
    if ok is True or ok == 0:
        logging.info("================= End: PLL Tables Write Success!] =================")
        sys.exit(0)
    else:
        logging.info("================== End: PLL Tables Write Failed, Please see error message above!] ==================")
        sys.exit(1)

if __name__ == "__main__":


    try:
        udaExec = teradata.UdaExec (appName="PLL_WRITE", version="1.0", logConsole=True)
        
        args = setup_argparse()
        
        dbs_name = args.dbs_name
        iteration = args.iteration
        scriptPath = args.scriptPath
        run_timestamp = args.run_timestamp
        ignore_error = args.ignore_error
        user_name = args.user_name
        node_password = args.node_password
        tpt_trace_level = args.tpt_trace_level
        
        pll_write_ignore_errors = tdtestpy.get_ignore_errors(common_error) + ignore_error
           
        
        # Set logs variables        
        pll_tables_write = os.path.join(scriptPath, "output", dbs_name, run_timestamp, "latest")
        faileddir = os.path.join(scriptPath, "output", dbs_name, run_timestamp, "failed")
        passed_dir = os.path.join(scriptPath, "output", dbs_name, run_timestamp, "passed")
        
        # Delete old_logs from latest
        prior_run_id = int(str(iteration)) - 1

        prior_check_log_name = user_name + "_pll_write_checktable_" + str(prior_run_id) + ".log"
        old_checktable_log = os.path.join(pll_tables_write, prior_check_log_name)
        tdtestpy.delete_one_file(old_checktable_log)
        
        prior_testuser = user_name + "_pll_write_loop_" + str(prior_run_id) + ".log"
        old_testuser_log = os.path.join(pll_tables_write, prior_testuser)
        tdtestpy.delete_one_file(old_testuser_log)

        prior_p_export_name = user_name + "_party_pll_tpt_export_loop_" + str(prior_run_id) + ".log"
        old_p_export_log = os.path.join(pll_tables_write, prior_p_export_name)
        tdtestpy.delete_one_file(old_p_export_log)
        
        prior_p_stream_name = user_name + "_party_pll_tpt_stream_loop_" + str(prior_run_id) + ".log"
        old_p_stream_log = os.path.join(pll_tables_write, prior_p_stream_name)
        tdtestpy.delete_one_file(old_p_stream_log)
        

        prior_l_export_name = user_name + "_location_pll_tpt_export_loop_" + str(prior_run_id) + ".log"
        old_l_export_log = os.path.join(pll_tables_write, prior_l_export_name)
        tdtestpy.delete_one_file(old_l_export_log)
        
        prior_l_stream_name = user_name + "_location_pll_tpt_stream_loop_" + str(prior_run_id) + ".log"
        old_l_stream_log = os.path.join(pll_tables_write, prior_l_stream_name)
        tdtestpy.delete_one_file(old_l_stream_log)
        
        prior_stl_export_name = user_name + "_sale_trans_line_pll_tpt_export_loop_" + str(prior_run_id) + ".log"
        old_stl_export_log = os.path.join(pll_tables_write, prior_stl_export_name)
        tdtestpy.delete_one_file(old_stl_export_log)
        
        prior_stl_stream_name = user_name + "_sale_trans_line_pll_tpt_stream_loop_" + str(prior_run_id) + ".log"
        old_stl_stream_log = os.path.join(pll_tables_write, prior_stl_stream_name)
        tdtestpy.delete_one_file(old_stl_stream_log)

        prior_st_export_name = user_name + "_sale_trans_pll_tpt_export_loop_" + str(prior_run_id) + ".log"
        old_st_export_log = os.path.join(pll_tables_write, prior_st_export_name)
        tdtestpy.delete_one_file(old_st_export_log)
        
        prior_st_stream_name = user_name + "_sale_trans_pll_tpt_stream_loop_" + str(prior_run_id) + ".log"        
        old_st_stream_log = os.path.join(pll_tables_write, prior_st_stream_name)
        tdtestpy.delete_one_file(old_st_stream_log)

 
        # dump python log to demo_log_path
        testuser = user_name + "_pll_write_loop_" + iteration + ".log"
        test_log_name = os.path.join(pll_tables_write, testuser)           
        fh = logging.FileHandler(test_log_name, mode="a", encoding="utf8")
        fh.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
        fh.setLevel(logging.DEBUG)
        root = logging.getLogger()
        root.addHandler(fh) 
        
        # Share TPT variables for all PLL tables
        directory_path = pll_tables_write
        tracelevel = tpt_trace_level
        
        # TPT variables for party_pll table
        party_pll_export_file = os.path.join(scriptPath, "tpt", "party_pll_export.tpt")
        party_pll_stream_file = os.path.join(scriptPath, "tpt", "party_pll_stream_upsert.tpt")
        
        p_export_name = user_name + "_party_pll_tpt_export_loop_" + iteration + ".log"
        p_stream_name = user_name + "_party_pll_tpt_stream_loop_" + iteration + ".log"
        party_pll_export_log = os.path.join(pll_tables_write, p_export_name)
        party_pll_stream_log = os.path.join(pll_tables_write, p_stream_name)
        
        party_pll_data_file = user_name + "_party_pll_loop_" + iteration + ".dat"
        party_pll_data_file_full_path = os.path.join(directory_path, party_pll_data_file) 
        
        # TPT variables for location_pll table
        location_pll_export_file = os.path.join(scriptPath, "tpt", "location_pll_export.tpt")
        location_pll_stream_file = os.path.join(scriptPath, "tpt", "location_pll_stream_upsert.tpt")
        
        l_export_name = user_name + "_location_pll_tpt_export_loop_" + iteration + ".log"
        l_stream_name = user_name + "_location_pll_tpt_stream_loop_" + iteration + ".log"
        
        location_pll_export_log = os.path.join(pll_tables_write, l_export_name)
        location_pll_stream_log = os.path.join(pll_tables_write, l_stream_name)
        
        location_pll_data_file = user_name + "_location_pll_loop_" + iteration + ".dat"
        location_pll_data_file_full_path = os.path.join(directory_path, location_pll_data_file) 
        
        # TPT variables for sale_trans_line_pll table
        sale_trans_line_pll_export_file = os.path.join(scriptPath, "tpt", "sale_trans_line_pll_export.tpt")
        sale_trans_line_pll_stream_file = os.path.join(scriptPath, "tpt", "sale_trans_line_pll_stream.tpt")
        
        stl_export_name = user_name + "_sale_trans_line_pll_tpt_export_loop_" + iteration + ".log"
        stl_stream_name = user_name + "_sale_trans_line_pll_tpt_stream_loop_" + iteration + ".log"
        
        sale_trans_line_pll_export_log = os.path.join(pll_tables_write, stl_export_name)
        sale_trans_line_pll_stream_log = os.path.join(pll_tables_write, stl_stream_name)
        
        sale_trans_line_pll_data_file = user_name + "_sale_trans_line_pll_loop_" + iteration + ".dat"
        sale_trans_line_pll_data_file_full_path = os.path.join(directory_path, sale_trans_line_pll_data_file) 
        
                            
        # TPT variables for sale_trans_pll table
        sale_trans_pll_export_file = os.path.join(scriptPath, "tpt", "sale_trans_pll_export.tpt")
        sale_trans_pll_stream_file = os.path.join(scriptPath, "tpt", "sale_trans_pll_stream.tpt")
        
        st_export_name = user_name + "_sale_trans_pll_tpt_export_loop_" + iteration + ".log"
        st_stream_name = user_name + "_sale_trans_pll_tpt_stream_loop_" + iteration + ".log"
        
        sale_trans_pll_export_log = os.path.join(pll_tables_write, st_export_name)
        sale_trans_pll_stream_log = os.path.join(pll_tables_write, st_stream_name)
        
        sale_trans_pll_data_file = user_name + "_sale_trans_pll_loop_" + iteration + ".dat"
        sale_trans_pll_data_file_full_path = os.path.join(directory_path, sale_trans_pll_data_file)         

        logging.info("================== PLL Tables Write Testing Started ==================")
  
        # Check row count of PLL tables, if they're not the same with stage tables then we reload so we can get accurate count.
        logging.info("Check row count of PLL tables, reload if they are not the same with stage tables")
        with udaExec.connect(method="odbc", system=dbs_name, username=user_name, password=user_name) as db_connect:
            test_user_instance = tdtestpy.DBSaccess (db_connect) 
            stage_database = "sit_ldi_pll_stage"
             
            org_location_count = test_user_instance.get_table_row_count(user_name, "LOCATION_PLL")               
            org_party_count = test_user_instance.get_table_row_count(user_name, "PARTY_PLL")
            org_stl_count = test_user_instance.get_table_row_count(user_name, "SALES_TRANSACTION_LINE_PLL")
            org_st_count = test_user_instance.get_table_row_count(user_name, "SALES_TRANSACTION_PLL")
            
            with db_connect.cursor() as cursor:
                tb_name = "LOCATION_PLL"
                if org_location_count != test_user_instance.get_table_row_count(stage_database, tb_name):
                    cursor.execute("delete %s" % (tb_name))
                    cursor.execute("insert into %s select * from %s.%s" % (tb_name, stage_database, tb_name))
                    org_location_count = test_user_instance.get_table_row_count(user_name, tb_name)
                    
                tb_name = "PARTY_PLL"
                if org_party_count != test_user_instance.get_table_row_count(stage_database, tb_name):
                    cursor.execute("delete %s" % (tb_name))
                    cursor.execute("insert into %s select * from %s.%s" % (tb_name, stage_database, tb_name))
                    org_party_count = test_user_instance.get_table_row_count(user_name, tb_name)
                    
                tb_name = "SALES_TRANSACTION_LINE_PLL"
                if org_stl_count != test_user_instance.get_table_row_count(stage_database, tb_name):
                    cursor.execute("delete %s" % (tb_name))
                    cursor.execute("insert into %s select * from %s.%s" % (tb_name, stage_database, tb_name))
                    org_stl_count = test_user_instance.get_table_row_count(user_name, tb_name)
                    
                tb_name = "SALES_TRANSACTION_PLL"
                if org_st_count != test_user_instance.get_table_row_count(stage_database, tb_name):
                    cursor.execute("delete %s" % (tb_name))
                    cursor.execute("insert into %s select * from %s.%s" % (tb_name, stage_database, tb_name))
                    org_st_count = test_user_instance.get_table_row_count(user_name, tb_name)
        
        logging.info("Original row counts for LOCATION_PLL is: %s" % (org_location_count))
        logging.info("Original row counts for PARTY_PLL is: %s" % (org_party_count))
        logging.info("Original row counts for SALES_TRANSACTION_LINE_PLL is: %s" % (org_stl_count))
        logging.info("Original row counts for SALES_TRANSACTION_PLL is: %s" % (org_st_count))
        
        # Running all DML in parallel
        logging.info("Running DML on all 4 tables in parallel")
        run_dml_transaction1_status, run_dml_transaction2_status, run_dml_transaction3_status, \
        run_dml_transaction4_status = run_dml_parallel(dbs_name, user_name, pll_write_ignore_errors)
        
        # Checking result of each table and mark it as failure if any of them return error.
    
        failure_count = 0    
        if type(run_dml_transaction1_status) is str:
            failure_count += 1
            logging.error ("DML for transaction1 failed due to error %s" % (run_dml_transaction1_status))

        if type(run_dml_transaction2_status) is str:
            failure_count += 1
            logging.error ("DML for transaction2 failed due to error %s" % (run_dml_transaction2_status))

        if type(run_dml_transaction3_status) is str:
            failure_count += 1
            logging.error ("DML for transaction3 failed due to error %s" % (run_dml_transaction3_status))

        if type(run_dml_transaction4_status) is str:
            failure_count += 1
            logging.error ("DML for transaction4 failed due to error %s" % (run_dml_transaction4_status))
            
        if failure_count != 0:
            tdtestpy.copy_file (test_log_name, faileddir)
            exit(1)
        
        # Create new row count after DML completed
        with udaExec.connect(method="odbc", system=dbs_name, username=user_name, password=user_name) as db_connect:
            test_user_instance = tdtestpy.DBSaccess (db_connect)
            new_location_count = test_user_instance.get_table_row_count(user_name, "LOCATION_PLL")               
            new_party_count = test_user_instance.get_table_row_count(user_name, "PARTY_PLL")
            new_stl_count = test_user_instance.get_table_row_count(user_name, "SALES_TRANSACTION_LINE_PLL")
            new_st_count = test_user_instance.get_table_row_count(user_name, "SALES_TRANSACTION_PLL")
        
        logging.info("New row counts for LOCATION_PLL is: %s" % (new_location_count))
        logging.info("New row counts for PARTY_PLL is: %s" % (new_party_count))
        logging.info("New row counts for SALES_TRANSACTION_LINE_PLL is: %s" % (new_stl_count))
        logging.info("New row counts for SALES_TRANSACTION_PLL is: %s" % (new_st_count))
        
        # Abort if row mismatch between original and new counts.
        """
        # Will disable compare rows until resubmit deadlock query 
        if not tdtestpy.compare_results (org_location_count, new_location_count):
            failure_count += 1
            logging.error ("Row mismatch for LOCATION_PLL table. Original rows: %s, New rows: %s" % (org_location_count, new_location_count))
            
        if not tdtestpy.compare_results (org_party_count, new_party_count):
            failure_count += 1
            logging.error ("Row mismatch for PARTY_PLL table. Original rows: %s, New rows: %s" % (org_party_count, new_party_count))
            
        if not tdtestpy.compare_results (org_stl_count, new_stl_count):
            failure_count += 1
            logging.error ("Row mismatch for SALES_TRANSACTION_LINE_PLL table. Original rows: %s, New rows: %s" % (org_stl_count, new_stl_count))
        
        if not tdtestpy.compare_results (org_st_count, new_st_count):
            failure_count += 1
            logging.error ("Row mismatch for SALES_TRANSACTION_PLL table. Original rows: %s, New rows: %s" % (org_st_count, new_st_count))
        if failure_count != 0:
            tdtestpy.copy_file (test_log_name, faileddir)
            exit(1)
        """
            
        # Finally we run checktable if run from linux client only since ssh won't work with window.
        if os_type == "Windows":
            logging.info ("Checktable is not running because SSH does not support Window client yet")
        else:
            # create datacheck class instance from common code tdtestpy 
            datacheck_instance = tdtestpy.DataCheck (dbs_name, node_password)
                        
            CheckTableName = ("SALES_TRANSACTION_PLL", "SALES_TRANSACTION_LINE_PLL", "PARTY_PLL", "LOCATION_PLL")
            CheckLevel = "two"
            check_log_name = user_name + "_pll_write_checktable_" + iteration + ".log"
            checktable_log = os.path.join(pll_tables_write, check_log_name)
            logging.info("Running checktable for user: %s" % (user_name))
            if not datacheck_instance.checktable (user_name, CheckTableName, CheckLevel, checktable_log):                    
                logging.error("Checktable for user %s failed, log file name: %s" % (user_name, checktable_log))
                tdtestpy.copy_file (test_log_name, faileddir)
                tdtestpy.copy_file (checktable_log, faileddir)
                exit(1)
        
        # Copy logs to passed if nothing wrong
        tdtestpy.copy_file (test_log_name, passed_dir)
        tdtestpy.copy_file (checktable_log, passed_dir)
        
    except Exception as e:
        logging.error(traceback.format_exc())
        tdtestpy.copy_file (test_log_name, faileddir)
        exit(1)
           
    exit(0)