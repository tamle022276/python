#!/usr/bin/python3
# Author: tl151006
# File: ldi_tables_write.py
# Date Published: 04/5/2016
# Purpose: Run DML on LDI tables
# Usage: python ldi_tables_write.py --database_name=db_name --user_name=db_user --user_password=db_password --ignore_error=error_1,error_2,error_n
# ignore_error can none to many, it separate by comma and it is optional
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

# Function will runs DML statements and TPT export/stream for ITEM_INVENTORY_PLAN_LDI table
def run_dml_item_inventory_plan(dbs_name, user_name, ignore_errors, run_result=None):
    try:
        with udaExec.connect(method="odbc", system=dbs_name, username=user_name, password=user_name) as db_connect:
            with db_connect.cursor() as cursor:
                # Run end isolated loading just in case prior run failed
                item_inv_plan_eil = user_name.strip() + "_ITEM_INV_PLAN_LDI"
                cursor.execute("END ISOLATED LOADING FOR QUERY_BAND 'LDILoadGroup=%s;'" % (item_inv_plan_eil), ignoreErrors=[9887])
                
                # Delete so we can use TPT streams to load it back
                cursor.execute("delete ITEM_INVENTORY_PLAN_LDI where ITEM_INVENTORY_PLAN_DT < '1970-11-28'", ignoreErrors=ignore_errors) 
                
                logging.info ("TPT export for ITEM_INVENTORY_PLAN_LDI started")
                if not tdtestpy.run_single_tpt(item_inventory_plan_export_file, item_inventory_plan_export_log, directory_path, \
                                       dbs_name, user_name, user_name, item_inventory_plan_data_file, tracelevel):
                    msg = "TPT export for ITEM_INVENTORY_PLAN_LDI failed, please review " + item_inventory_plan_export_log
                    logging.info ("TPT export for ITEM_INVENTORY_PLAN_LDI completed with failure")
                    tdtestpy.copy_file (item_inventory_plan_export_log, faileddir)
                    
                    if run_result is None:
                        return msg
                    else:
                        run_result.put(msg)
                    
                logging.info ("TPT export for ITEM_INVENTORY_PLAN_LDI completed successful")
                tdtestpy.copy_file (item_inventory_plan_export_log, passed_dir)
                
                logging.info ("TPT stream for ITEM_INVENTORY_PLAN_LDI started")
                if not tdtestpy.run_single_tpt(item_inventory_plan_stream_file, item_inventory_plan_stream_log, directory_path, \
                                       dbs_name, user_name, user_name, item_inventory_plan_data_file, tracelevel):
                    msg = "TPT stream for ITEM_INVENTORY_PLAN_LDI failed, please review " + item_inventory_plan_stream_log
                    logging.info ("TPT stream for ITEM_INVENTORY_PLAN_LDI completed with failure")
                    tdtestpy.copy_file (item_inventory_plan_stream_log, faileddir)
                    
                    if run_result is None:
                        return msg
                    else:
                        run_result.put(msg)
                    
                logging.info ("TPT stream for ITEM_INVENTORY_PLAN_LDI completed successful")
                tdtestpy.copy_file (item_inventory_plan_stream_log, passed_dir)
                
                # Delete data file if TPT export and stream ran successful
                tdtestpy.delete_one_file (item_inventory_plan_data_file_full_path)
                
                cursor.execute("Select ITEM_INVENTORY_PLAN_DT, LOCATION_ID, ITEM_ID from ITEM_INVENTORY_PLAN_LDI sample 100")
                result_set = cursor.fetchall()
                index_combo_list = []               
                for row in result_set:
                    # Created sublist
                    combo_id = [row["ITEM_INVENTORY_PLAN_DT"], row["LOCATION_ID"], row["ITEM_ID"]]
                    # Append sublist to main list
                    index_combo_list.append(combo_id)
                # Extract sublist from main list and replace index 
                for index_combo in index_combo_list:
                    cursor.execute("update ITEM_INVENTORY_PLAN_LDI set PLAN_ON_HAND_QTY = 0 \
                                where ITEM_INVENTORY_PLAN_DT = '%s' and LOCATION_ID = %s and ITEM_ID = '%s'" % (index_combo[0], \
                                                                               index_combo[1], index_combo[2]), ignoreErrors=ignore_errors)
                    cursor.execute("delete ITEM_INVENTORY_PLAN_LDI \
                                where ITEM_INVENTORY_PLAN_DT = '%s' and LOCATION_ID = %s and ITEM_ID = '%s'" % (index_combo[0], \
                                                                               index_combo[1], index_combo[2]), ignoreErrors=ignore_errors)
                
                # Trim down main list to 20 elements
                new_index_combo_list = index_combo_list[0:20]
                              
                for new_index_combo in new_index_combo_list:
                    cursor.execute("insert into ITEM_INVENTORY_PLAN_LDI select * from sit_ldi_pll_stage.ITEM_INVENTORY_PLAN_LDI \
                                where ITEM_INVENTORY_PLAN_DT = '%s' and LOCATION_ID = %s and ITEM_ID = '%s'" % (new_index_combo[0], \
                                                                               new_index_combo[1], new_index_combo[2]), ignoreErrors=ignore_errors)
                    
                    cursor.execute("update ITEM_INVENTORY_PLAN_LDI set PLAN_ON_HAND_RETAIL_AMT = PLAN_ON_HAND_QTY \
                                where ITEM_INVENTORY_PLAN_DT = '%s' and LOCATION_ID = %s and ITEM_ID = '%s'" % (new_index_combo[0], \
                                                                               new_index_combo[1], new_index_combo[2]), ignoreErrors=ignore_errors)

                    
                cursor.execute("MERGE into ITEM_INVENTORY_PLAN_LDI as t1 \
                using sit_ldi_pll_stage.ITEM_INVENTORY_PLAN_LDI as t2 \
                on t1.ITEM_INVENTORY_PLAN_DT = t2.ITEM_INVENTORY_PLAN_DT \
                and t1.LOCATION_ID = t2.LOCATION_ID \
                and t1.ITEM_ID = t2.ITEM_ID \
                WHEN MATCHED THEN \
                UPDATE SET PLAN_ON_HAND_RETAIL_AMT = t2.PLAN_ON_HAND_RETAIL_AMT \
                WHEN NOT MATCHED THEN \
                insert (ITEM_INVENTORY_PLAN_DT, LOCATION_ID, ITEM_ID, PLAN_ON_HAND_QTY, PLAN_ON_HAND_RETAIL_AMT) \
                values (t2.ITEM_INVENTORY_PLAN_DT, t2.LOCATION_ID, t2.ITEM_ID, t2.PLAN_ON_HAND_QTY, \
                t2.PLAN_ON_HAND_RETAIL_AMT)", ignoreErrors=ignore_errors)
                
                # Remove logically deleted rows to free up space
                cursor.execute("END ISOLATED LOADING FOR QUERY_BAND 'LDILoadGroup=%s;'" % (item_inv_plan_eil), ignoreErrors=[9887])
                cursor.execute("ALTER TABLE ITEM_INVENTORY_PLAN_LDI RELEASE DELETED ROWS AND RESET LOAD IDENTITY", ignoreErrors=ignore_errors)
            
    except Exception as e:
        if run_result is None:
            return str(e)
        else:
            run_result.put(str(e))
    if run_result is None:
        return True
    else:
        run_result.put(True)
        
        
# Function that runs DML statements and TPT export/stream for ITEM_INVENTORY_LDI table
def run_dml_item_inventory(dbs_name, user_name, location_id_list, ignore_errors, run_result=None):
    try:
        with udaExec.connect(method="odbc", system=dbs_name, username=user_name, password=user_name) as db_connect:
            with db_connect.cursor() as cursor:
                # Run end isolated loading just in case prior run failed
                item_inv_eil = user_name.strip() + "_ITEM_INV_LDI"
                cursor.execute("END ISOLATED LOADING FOR QUERY_BAND 'LDILoadGroup=%s;'" % (item_inv_eil), ignoreErrors=[9887])
                
                cursor.execute("delete ITEM_INVENTORY_LDI \
                                where ITEM_INV_DT < '1975-01-01'", ignoreErrors=ignore_errors)
                logging.info ("TPT export for ITEM_INVENTORY_LDI started")
                if not tdtestpy.run_single_tpt(item_inventory_export_file, item_inventory_export_log, directory_path, \
                                       dbs_name, user_name, user_name, item_inventory_data_file, tracelevel):
                    msg = "TPT export for ITEM_INVENTORY_LDI failed, please review " + item_inventory_export_log
                    logging.info ("TPT export for ITEM_INVENTORY_LDI completed with failure")
                    tdtestpy.copy_file (item_inventory_export_log, faileddir)
                    
                    if run_result is None:
                        return msg
                    else:
                        run_result.put(msg)
                    
                logging.info ("TPT export for ITEM_INVENTORY_LDI completed successful")
                tdtestpy.copy_file (item_inventory_export_log, passed_dir)
                
                logging.info ("TPT stream for ITEM_INVENTORY_LDI started")
                if not tdtestpy.run_single_tpt(item_inventory_stream_file, item_inventory_stream_log, directory_path, \
                                       dbs_name, user_name, user_name, item_inventory_data_file, tracelevel):
                    msg = "TPT stream for ITEM_INVENTORY_LDI failed, please review " + item_inventory_stream_log
                    logging.info ("TPT stream for ITEM_INVENTORY_LDI completed with failure")
                    tdtestpy.copy_file (item_inventory_stream_log, faileddir)
                    
                    if run_result is None:
                        return msg
                    else:
                        run_result.put(msg)
                    
                logging.info ("TPT stream for ITEM_INVENTORY_LDI completed successful")
                tdtestpy.copy_file (item_inventory_stream_log, passed_dir)
                
                # Delete data file if TPT export and stream ran successful
                tdtestpy.delete_one_file (item_inventory_data_file_full_path)
                
                for location_id in location_id_list:
                    cursor.execute("update ITEM_INVENTORY_LDI set ON_HAND_AT_RETAIL_AMT = 10000 \
                                where  LOCATION_ID = %s" % (location_id), ignoreErrors=ignore_errors)
                    cursor.execute("delete ITEM_INVENTORY_LDI \
                                where  LOCATION_ID = %s" % (location_id), ignoreErrors=ignore_errors)
            
                location_id_set = str(tuple(location_id_list))
                cursor.execute("insert into ITEM_INVENTORY_LDI select * from sit_ldi_pll_stage.ITEM_INVENTORY_LDI \
                                where  LOCATION_ID in %s" % (location_id_set), ignoreErrors=ignore_errors)
                
                # Remove logically deleted rows to free up space
                cursor.execute("END ISOLATED LOADING FOR QUERY_BAND 'LDILoadGroup=%s;'" % (item_inv_eil), ignoreErrors=[9887])
                cursor.execute("ALTER TABLE ITEM_INVENTORY_LDI RELEASE DELETED ROWS AND RESET LOAD IDENTITY", ignoreErrors=ignore_errors)
                                
    except Exception as e:
        if run_result is None:
            return str(e)
        else:
            run_result.put(str(e))
    if run_result is None:
        return True
    else:
        run_result.put(True)
        
# Function that runs DML statements and TPT export/stream for RETURN_TRANSACTION_LINE_LDI table
def run_dml_return_trans_line(dbs_name, user_name, TRAN_LINE_STATUS_CD_LIST, ignore_errors, run_result=None):
    try:
        with udaExec.connect(method="odbc", system=dbs_name, username=user_name, password=user_name) as db_connect:
            with db_connect.cursor() as cursor:
                # Run end isolated loading just in case prior run failed
                return_trans_line_eil = user_name.strip() + "_RETURN_TRANS_LINE_LDI"
                cursor.execute("END ISOLATED LOADING FOR QUERY_BAND 'LDILoadGroup=%s;'" % (return_trans_line_eil), ignoreErrors=[9887])
                
                cursor.execute("update RETURN_TRANSACTION_LINE_LDI set TRAN_LINE_STATUS_CD = '%s' \
                                where  TRAN_LINE_STATUS_CD = '%s'" % (TRAN_LINE_STATUS_CD_LIST[0], TRAN_LINE_STATUS_CD_LIST[1]), \
                                ignoreErrors=ignore_errors)
                
                cursor.execute("delete RETURN_TRANSACTION_LINE_LDI \
                                where  TRAN_LINE_STATUS_CD in ('A', 'B')", ignoreErrors=ignore_errors)
                
                logging.info ("TPT export for RETURN_TRANSACTION_LINE_LDI started")
                if not tdtestpy.run_single_tpt(return_transaction_line_export_file, return_transaction_line_export_log, directory_path, \
                                       dbs_name, user_name, user_name, return_transaction_line_data_file, tracelevel):
                    msg = "TPT export for RETURN_TRANSACTION_LINE_LDI failed, please review " + return_transaction_line_export_log
                    logging.info ("TPT export for RETURN_TRANSACTION_LINE_LDI completed with failure")
                    tdtestpy.copy_file (return_transaction_line_export_log, faileddir)
                    
                    if run_result is None:
                        return msg
                    else:
                        run_result.put(msg)
                    
                logging.info ("TPT export for RETURN_TRANSACTION_LINE_LDI completed successful")
                tdtestpy.copy_file (return_transaction_line_export_log, passed_dir)
                
                logging.info ("TPT stream for RETURN_TRANSACTION_LINE_LDI started")
                if not tdtestpy.run_single_tpt(return_transaction_line_stream_file, return_transaction_line_stream_log, directory_path, \
                                       dbs_name, user_name, user_name, return_transaction_line_data_file, tracelevel):
                    msg = "TPT stream for RETURN_TRANSACTION_LINE_LDI failed, please review " + return_transaction_line_stream_log
                    logging.info ("TPT stream for RETURN_TRANSACTION_LINE_LDI completed with failure")
                    tdtestpy.copy_file (return_transaction_line_stream_log, faileddir)
                    
                    if run_result is None:
                        return msg
                    else:
                        run_result.put(msg)
                        
                logging.info ("TPT stream for RETURN_TRANSACTION_LINE_LDI completed successful")
                tdtestpy.copy_file (return_transaction_line_stream_log, passed_dir)
                
                # Delete data file if TPT export and stream ran successful
                tdtestpy.delete_one_file (return_transaction_line_data_file_full_path)
            
                cursor.execute("delete RETURN_TRANSACTION_LINE_LDI \
                                where  TRAN_LINE_STATUS_CD = '%s'" % (TRAN_LINE_STATUS_CD_LIST[0]), ignoreErrors=ignore_errors)
            
                cursor.execute("insert into RETURN_TRANSACTION_LINE_LDI select * from sit_ldi_pll_stage.RETURN_TRANSACTION_LINE_LDI \
                                where TRAN_LINE_STATUS_CD in ('%s', '%s')" % (TRAN_LINE_STATUS_CD_LIST[0], TRAN_LINE_STATUS_CD_LIST[1]), ignoreErrors=ignore_errors)
                
                # Remove logically deleted rows to free up space
                cursor.execute("END ISOLATED LOADING FOR QUERY_BAND 'LDILoadGroup=%s;'" % (return_trans_line_eil), ignoreErrors=[9887])
                cursor.execute("ALTER TABLE RETURN_TRANSACTION_LINE_LDI RELEASE DELETED ROWS AND RESET LOAD IDENTITY", ignoreErrors=ignore_errors)
                
    except Exception as e:
        if run_result is None:
            return str(e)
        else:
            run_result.put(str(e))
    if run_result is None:
        return True
    else:
        run_result.put(True)

# Function that runs DML statements and TPT export/stream upsert for item_ldi table 
def run_dml_item(dbs_name, user_name, item_available, ignore_errors, run_result=None):
    try:
        with udaExec.connect(method="odbc", system=dbs_name, username=user_name, password=user_name) as db_connect:
            with db_connect.cursor() as cursor:
                
                # Run end isolated loading just in case prior run failed
                item_eil = user_name.strip() + "_ITEM_LDI"
                cursor.execute("END ISOLATED LOADING FOR QUERY_BAND 'LDILoadGroup=%s;'" % (item_eil), ignoreErrors=[9887])
                
                cursor.execute("delete item_ldi \
                where  ITEM_AVAILABLE = '%s' \
                and ITEM_ID not in (select ITEM_ID from ITEM_INVENTORY_LDI) \
                and ITEM_ID not in (select ITEM_ID from ITEM_INVENTORY_PLAN_LDI) \
                and ITEM_ID not in (select RETURNED_ITEM_ID from RETURN_TRANSACTION_LINE_LDI) \
                and ITEM_ID not in (select ITEM_ID from SALES_TRANSACTION_LINE_PLL) \
                and ITEM_ID not in (select ITEM_ID from ITEM_PRICE_HISTORY)" % (item_available[0]), ignoreErrors=ignore_errors)

                cursor.execute("update item_ldi set ITEM_DESC  = 'Product being recall and taking off store shelves' \
                where ITEM_AVAILABLE = '%s'" % (item_available[0]), ignoreErrors=ignore_errors)
                
                cursor.execute("MERGE into item_ldi as i1 \
                using sit_ldi_pll_stage.item_ldi as i2 \
                on i1.ITEM_ID = i2.ITEM_ID and i1.ITEM_LEVEL = i2.ITEM_LEVEL \
                WHEN MATCHED THEN \
                UPDATE SET ITEM_DESC = i2.ITEM_DESC \
                WHEN NOT MATCHED THEN \
                insert (ITEM_ID, ITEM_NAME, ITEM_LEVEL, ITEM_DESC, ITEM_SUBCLASS_CD, \
                ITEM_TYPE_CD, INVENTORY_IND, VENDOR_PARTY_ID, COMMODITY_CD, BRAND_CD, \
                ITEM_AVAILABLE, PRODUCT_IMEI, ITEM_JSON, ITEM_XML) \
                values (i2.ITEM_ID, i2.ITEM_NAME, i2.ITEM_LEVEL, i2.ITEM_DESC, \
                i2.ITEM_SUBCLASS_CD, i2.ITEM_TYPE_CD, i2.INVENTORY_IND, i2.VENDOR_PARTY_ID, \
                i2.COMMODITY_CD, i2.BRAND_CD, i2.ITEM_AVAILABLE, i2.PRODUCT_IMEI, i2.ITEM_JSON, \
                i2.ITEM_XML)", ignoreErrors=ignore_errors)
                
                cursor.execute("update item_ldi set INVENTORY_IND  = 'HQO' \
                where ITEM_AVAILABLE = ''", ignoreErrors=ignore_errors)
                
                cursor.execute("delete item_ldi \
                where  ITEM_AVAILABLE = '' \
                and ITEM_LEVEL < 15 \
                and ITEM_ID not in (select ITEM_ID from ITEM_INVENTORY_LDI) \
                and ITEM_ID not in (select ITEM_ID from ITEM_INVENTORY_PLAN_LDI) \
                and ITEM_ID not in (select RETURNED_ITEM_ID from RETURN_TRANSACTION_LINE_LDI) \
                and ITEM_ID not in (select ITEM_ID from SALES_TRANSACTION_LINE_PLL) \
                and ITEM_ID not in (select ITEM_ID from ITEM_PRICE_HISTORY)", ignoreErrors=ignore_errors)
                
                logging.info ("TPT export for item_ldi started")
                if not tdtestpy.run_single_tpt(item_ldi_export_file, item_ldi_export_log, directory_path, \
                                       dbs_name, user_name, user_name, item_ldi_data_file, tracelevel):
                    msg = "TPT export for item_ldi failed, please review " + item_ldi_export_log
                    logging.info ("TPT export for item_ldi completed with failure")
                    tdtestpy.copy_file (item_ldi_export_log, faileddir)
                    
                    if run_result is None:
                        return msg
                    else:
                        run_result.put(msg)
                    
                logging.info ("TPT export for item_ldi completed successful")
                tdtestpy.copy_file (item_ldi_export_log, passed_dir)
                
                logging.info ("TPT stream for item_ldi started")
                if not tdtestpy.run_single_tpt(item_ldi_stream_file, item_ldi_stream_log, directory_path, \
                                       dbs_name, user_name, user_name, item_ldi_data_file, tracelevel):
                    msg = "TPT stream for item_ldi failed, please review " + item_ldi_stream_log
                    logging.info ("TPT stream for item_ldi completed with failure")
                    tdtestpy.copy_file (item_ldi_stream_log, faileddir)
                    
                    if run_result is None:
                        return msg
                    else:
                        run_result.put(msg)
                    
                logging.info ("TPT stream for item_ldi completed successful")
                tdtestpy.copy_file (item_ldi_stream_log, passed_dir)
                
                # Delete data file if TPT export and stream ran successful
                tdtestpy.delete_one_file (item_ldi_data_file_full_path)
                
                # Remove logically deleted rows to free up space
                cursor.execute("END ISOLATED LOADING FOR QUERY_BAND 'LDILoadGroup=%s;'" % (item_eil), ignoreErrors=[9887])
                cursor.execute("ALTER TABLE ITEM_INVENTORY_PLAN_LDI RELEASE DELETED ROWS AND RESET LOAD IDENTITY", ignoreErrors=ignore_errors)
                
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
def run_dml_parallel(dbs_name, user_name, TRAN_LINE_STATUS_CD_LIST, item_available, location_id_list, ignore_errors):
    run_dml_return_trans_line_result = queue.Queue()
    run_dml_item_result = queue.Queue()
    run_dml_item_inventory_result = queue.Queue()
    run_dml_item_inventory_plan_result = queue.Queue()
            
    t1 = threading.Thread(target=run_dml_return_trans_line, args=(dbs_name, user_name, TRAN_LINE_STATUS_CD_LIST, ignore_errors, \
                                                             run_dml_return_trans_line_result))
       
    t2 = threading.Thread(target=run_dml_item, args=(dbs_name, user_name, item_available, ignore_errors, run_dml_item_result))
    
    t3 = threading.Thread(target=run_dml_item_inventory, args=(dbs_name, user_name, location_id_list, ignore_errors, run_dml_item_inventory_result))
    
    t4 = threading.Thread(target=run_dml_item_inventory_plan, args=(dbs_name, user_name, ignore_errors, run_dml_item_inventory_plan_result))

    t1.start()
    t2.start()
    t3.start()
    t4.start()
    
    t1.join()
    t2.join()
    t3.join()
    t4.join()
    
    return run_dml_return_trans_line_result.get(), run_dml_item_result.get(), \
        run_dml_item_inventory_result.get(), run_dml_item_inventory_plan_result.get()


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
        logging.info("================= End: LDI Tables Write Success!] =================")
        sys.exit(0)
    else:
        logging.info("================== End: LDI Tables Write Failed, Please see error message above!] ==================")
        sys.exit(1)

if __name__ == "__main__":


    try:
        udaExec = teradata.UdaExec (appName="LDI_WRITE", version="1.0", logConsole=True)
        
        args = setup_argparse()
        
        dbs_name = args.dbs_name
        iteration = args.iteration
        scriptPath = args.scriptPath
        run_timestamp = args.run_timestamp
        ignore_error = args.ignore_error
        user_name = args.user_name
        node_password = args.node_password
        tpt_trace_level = args.tpt_trace_level
        
        ldi_write_ignore_errors = tdtestpy.get_ignore_errors(common_error) + ignore_error
           
        return_trans_status = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', \
                               'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z' ]
        
        location_id = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, \
                       41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, \
                       70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, \
                       110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, \
                       151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, \
                       210, 211, 212, 213, 214, 215, 216, 217, 218, 219, 220, 221, 222, 223, 224, 225, 226, 227, 228, 229, 230, \
                       330, 331, 332, 333, 334, 335, 336, 337, 338, 339, 340, 341, 342, 343, 344, 345, 346, 347, 348, 349, 350, \
                       450, 451, 452, 453, 454, 455, 456, 457, 458, 459, 460, 461, 462, 463, 464, 465, 466, 467, 468, 469, 470
                       ]
        
        item_available = (random.choice(["Y", "N"]))
        
        random_return_trans_status = random.sample(set(return_trans_status), 2)
        
        random_location_id = random.sample(set(location_id), 30)
        
        
        # Set logs variables
        ldi_tables_write = os.path.join(scriptPath, "output", dbs_name, run_timestamp, "latest")
        faileddir = os.path.join(scriptPath, "output", dbs_name, run_timestamp, "failed")
        passed_dir = os.path.join(scriptPath, "output", dbs_name, run_timestamp, "passed")
        
        # Delete old_logs from latest
        prior_run_id = int(str(iteration)) - 1
        
        prior_check_log_name = user_name + "_ldi_write_checktable_" + str(prior_run_id) + ".log"
        old_checktable_log = os.path.join(ldi_tables_write, prior_check_log_name)
        tdtestpy.delete_one_file(old_checktable_log)
        
        
        prior_testuser = user_name + "_ldi_write_loop_" + str(prior_run_id) + ".log"
        old_testuser = os.path.join(ldi_tables_write, prior_testuser)
        tdtestpy.delete_one_file(old_testuser)
        
        prior_iip_export_name = user_name + "_item_inv_plan_ldi_tpt_export_loop_" + str(prior_run_id) + ".log"
        old_iip_export_name = os.path.join(ldi_tables_write, prior_iip_export_name)
        tdtestpy.delete_one_file(old_iip_export_name)
        
        prior_iip_stream_name = user_name + "_item_inv_plan_ldi_tpt_stream_loop_" + str(prior_run_id) + ".log"
        old_iip_stream_name = os.path.join(ldi_tables_write, prior_iip_stream_name)
        tdtestpy.delete_one_file(old_iip_stream_name)
        
        
        prior_ii_export_name = user_name + "_item_inv_ldi_tpt_export_loop_" + str(prior_run_id) + ".log"
        old_ii_export_name = os.path.join(ldi_tables_write, prior_ii_export_name)
        tdtestpy.delete_one_file(old_ii_export_name)
        
        prior_ii_stream_name = user_name + "_item_inv_ldi_tpt_stream_loop_" + str(prior_run_id) + ".log"
        old_ii_stream_name = os.path.join(ldi_tables_write, prior_ii_stream_name)
        tdtestpy.delete_one_file(old_ii_stream_name)
        
        
        prior_rtl_export_name = user_name + "_return_trans_line_ldi_tpt_export_loop_" + str(prior_run_id) + ".log"
        old_rtl_export_name = os.path.join(ldi_tables_write, prior_rtl_export_name)
        tdtestpy.delete_one_file(old_rtl_export_name)
        
        prior_rtl_stream_name = user_name + "_return_trans_line_ldi_tpt_stream_loop_" + str(prior_run_id) + ".log"
        old_rtl_stream_name = os.path.join(ldi_tables_write, prior_rtl_stream_name)
        tdtestpy.delete_one_file(old_rtl_stream_name)
        
        prior_i_export_name = user_name + "_item_ldi_tpt_export_loop_" + str(prior_run_id) + ".log"
        old_i_export_name = os.path.join(ldi_tables_write, prior_i_export_name)
        tdtestpy.delete_one_file(old_i_export_name)
        
        prior_i_stream_name = user_name + "_item_ldi_tpt_stream_loop_" + str(prior_run_id) + ".log"
        old_i_stream_name = os.path.join(ldi_tables_write, prior_i_stream_name)
        tdtestpy.delete_one_file(old_i_stream_name)

        
        
       
                         
        # dump python log to demo_log_path
        testuser = user_name + "_ldi_write_loop_" + iteration + ".log"
        test_log_name = os.path.join(ldi_tables_write, testuser)       
        fh = logging.FileHandler(test_log_name, mode="a", encoding="utf8")
        fh.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
        fh.setLevel(logging.DEBUG)
        root = logging.getLogger()
        root.addHandler(fh) 
        
        
        # Share TPT variables for all LDI tables
        directory_path = ldi_tables_write
        tracelevel = tpt_trace_level
        
        # TPT variables for item_inventory_plan_ldi table
        item_inventory_plan_export_file = os.path.join(scriptPath, "tpt", "item_inventory_plan_ldi_export.tpt")
        item_inventory_plan_stream_file = os.path.join(scriptPath, "tpt", "item_inventory_plan_ldi_stream.tpt")
        
        iip_export_name = user_name + "_item_inv_plan_ldi_tpt_export_loop_" + iteration + ".log"
        iip_stream_name = user_name + "_item_inv_plan_ldi_tpt_stream_loop_" + iteration + ".log"
    
        
        item_inventory_plan_export_log = os.path.join(ldi_tables_write, iip_export_name)
        item_inventory_plan_stream_log = os.path.join(ldi_tables_write, iip_stream_name)
        
        item_inventory_plan_data_file = user_name + "_item_inv_plan_ldi_loop_" + iteration + ".dat"
        item_inventory_plan_data_file_full_path = os.path.join(directory_path, item_inventory_plan_data_file) 
                    
        # TPT variables for item_inventory_ldi table
        item_inventory_export_file = os.path.join(scriptPath, "tpt", "item_inventory_ldi_export.tpt")
        item_inventory_stream_file = os.path.join(scriptPath, "tpt", "item_inventory_ldi_stream.tpt")
        
        ii_export_name = user_name + "_item_inv_ldi_tpt_export_loop_" + iteration + ".log"
        ii_stream_name = user_name + "_item_inv_ldi_tpt_stream_loop_" + iteration + ".log"
        
        item_inventory_export_log = os.path.join(ldi_tables_write, ii_export_name)
        item_inventory_stream_log = os.path.join(ldi_tables_write, ii_stream_name)
        
        item_inventory_data_file = user_name + "_item_inv_ldi_loop_" + iteration + ".dat"
        item_inventory_data_file_full_path = os.path.join(directory_path, item_inventory_data_file) 
        
        
        # TPT variables for return_transaction_line_ldi table
        return_transaction_line_export_file = os.path.join(scriptPath, "tpt", "return_transaction_line_ldi_export.tpt")
        return_transaction_line_stream_file = os.path.join(scriptPath, "tpt", "return_transaction_line_ldi_stream.tpt")
        
        rtl_export_name = user_name + "_return_trans_line_ldi_tpt_export_loop_" + iteration + ".log"
        rtl_stream_name = user_name + "_return_trans_line_ldi_tpt_stream_loop_" + iteration + ".log"
        
        return_transaction_line_export_log = os.path.join(ldi_tables_write, rtl_export_name)
        return_transaction_line_stream_log = os.path.join(ldi_tables_write, rtl_stream_name)
        
        return_transaction_line_data_file = user_name + "_return_trans_line_ldi_loop_" + iteration + ".dat"
        return_transaction_line_data_file_full_path = os.path.join(directory_path, return_transaction_line_data_file) 
        
        
        # TPT variables for item_ldi table
        item_ldi_export_file = os.path.join(scriptPath, "tpt", "item_ldi_export.tpt")
        item_ldi_stream_file = os.path.join(scriptPath, "tpt", "item_ldi_stream_upsert.tpt")
        
        i_export_name = user_name + "_item_ldi_tpt_export_loop_" + iteration + ".log"
        i_stream_name = user_name + "_item_ldi_tpt_stream_loop_" + iteration + ".log"
        
        item_ldi_export_log = os.path.join(ldi_tables_write, i_export_name)
        item_ldi_stream_log = os.path.join(ldi_tables_write, i_stream_name)
        
        item_ldi_data_file = user_name + "_item_ldi_loop_" + iteration + ".dat"
        item_ldi_data_file_full_path = os.path.join(directory_path, item_ldi_data_file) 
                

        
        # Main test body start here
        
        logging.info("================== LDI Tables Write Testing Started ==================")
  
        # Check row count of LDI tables, if they're not the same with stage tables then we reload so we can get accurate count.
        logging.info("Check row count of LDI tables, reload if they are not the same with stage tables")
        with udaExec.connect(method="odbc", system=dbs_name, username=user_name, password=user_name) as db_connect:
            test_user_instance = tdtestpy.DBSaccess (db_connect) 
            stage_database = "sit_ldi_pll_stage"
             
            org_iip_count = test_user_instance.get_table_row_count(user_name, "ITEM_INVENTORY_PLAN_LDI")               
            org_ii_count = test_user_instance.get_table_row_count(user_name, "ITEM_INVENTORY_LDI")
            org_rtl_count = test_user_instance.get_table_row_count(user_name, "RETURN_TRANSACTION_LINE_LDI")
            org_i_count = test_user_instance.get_table_row_count(user_name, "item_ldi")
            
            with db_connect.cursor() as cursor:
                tb_name = "ITEM_INVENTORY_PLAN_LDI"
                stage_db = "sit_ldi_pll_stage"
                if org_iip_count != test_user_instance.get_table_row_count(stage_database, tb_name):
                    item_inv_plan_eil = user_name.strip() + "_ITEM_INV_PLAN_LDI"
                    cursor.execute("END ISOLATED LOADING FOR QUERY_BAND 'LDILoadGroup=%s;'" % (item_inv_plan_eil), ignoreErrors=[9887])
                    cursor.execute("delete %s" % (tb_name))
                    cursor.execute("insert into %s select * from %s.%s" % (tb_name, stage_db, tb_name))
                    org_iip_count = test_user_instance.get_table_row_count(user_name, tb_name)
                    
                tb_name = "ITEM_INVENTORY_LDI"
                if org_ii_count != test_user_instance.get_table_row_count(stage_database, tb_name):
                    item_inv_eil = user_name.strip() + "_ITEM_INV_LDI"
                    cursor.execute("END ISOLATED LOADING FOR QUERY_BAND 'LDILoadGroup=%s;'" % (item_inv_eil), ignoreErrors=[9887])
                    cursor.execute("delete %s" % (tb_name))
                    cursor.execute("insert into %s select * from %s.%s" % (tb_name, stage_db, tb_name))
                    org_ii_count = test_user_instance.get_table_row_count(user_name, tb_name)
                    
                tb_name = "RETURN_TRANSACTION_LINE_LDI"
                if org_rtl_count != test_user_instance.get_table_row_count(stage_database, tb_name):
                    return_trans_line_eil = user_name.strip() + "_RETURN_TRANS_LINE_LDI"
                    cursor.execute("END ISOLATED LOADING FOR QUERY_BAND 'LDILoadGroup=%s;'" % (return_trans_line_eil), ignoreErrors=[9887])
                    cursor.execute("delete %s" % (tb_name))
                    cursor.execute("insert into %s select * from %s.%s" % (tb_name, stage_db, tb_name))
                    org_rtl_count = test_user_instance.get_table_row_count(user_name, tb_name)
                    
                tb_name = "item_ldi"
                if org_i_count != test_user_instance.get_table_row_count(stage_database, tb_name):
                    item_eil = user_name.strip() + "_ITEM_LDI"
                    cursor.execute("END ISOLATED LOADING FOR QUERY_BAND 'LDILoadGroup=%s;'" % (item_eil), ignoreErrors=[9887])
                    cursor.execute("delete %s" % (tb_name))
                    cursor.execute("insert into %s select * from %s.%s" % (tb_name, stage_db, tb_name))
                    org_i_count = test_user_instance.get_table_row_count(user_name, tb_name)
        
        logging.info("Original row counts for ITEM_INVENTORY_PLAN_LDI is: %s" % (org_iip_count))
        logging.info("Original row counts for ITEM_INVENTORY_LDI is: %s" % (org_ii_count))
        logging.info("Original row counts for RETURN_TRANSACTION_LINE_LDI is: %s" % (org_rtl_count))
        logging.info("Original row counts for item_ldi is: %s" % (org_i_count))
        
        # Running all DML in parallel
        logging.info("Running DML on all 4 tables in parallel")
        run_dml_return_trans_line_status, run_dml_item_result_status, run_dml_item_inventory_status, \
        run_dml_item_inventory_plan_status = run_dml_parallel(dbs_name, user_name, random_return_trans_status, \
                                                              item_available, random_location_id, ldi_write_ignore_errors)
        
        # Checking result of each table and mark it as failure if any of them return error.

        
        # debug hang
        print (run_dml_return_trans_line_status)
        print (run_dml_item_result_status)
        print (run_dml_item_inventory_status)
        print (run_dml_item_inventory_plan_status)
            
        failure_count = 0    
        if type(run_dml_return_trans_line_status) is str:
            failure_count += 1
            logging.error ("DML for RETURN_TRANSACTION_LINE_LDI failed due to error %s" % (run_dml_return_trans_line_status))

        if type(run_dml_item_result_status) is str:
            failure_count += 1
            logging.error ("DML for item_ldi failed due to error %s" % (run_dml_item_result_status))

        if type(run_dml_item_inventory_status) is str:
            failure_count += 1
            logging.error ("DML for ITEM_INVENTORY_LDI failed due to error %s" % (run_dml_item_inventory_status))

        if type(run_dml_item_inventory_plan_status) is str:
            failure_count += 1
            logging.error ("DML for ITEM_INVENTORY_PLAN_LDI failed due to error %s" % (run_dml_item_inventory_plan_status))
            
        if failure_count != 0:
            tdtestpy.copy_file (test_log_name, faileddir)
            exit(1)
        
        # Create new row count after DML completed
        with udaExec.connect(method="odbc", system=dbs_name, username=user_name, password=user_name) as db_connect:
            test_user_instance = tdtestpy.DBSaccess (db_connect)
            new_iip_count = test_user_instance.get_table_row_count(user_name, "ITEM_INVENTORY_PLAN_LDI")               
            new_ii_count = test_user_instance.get_table_row_count(user_name, "ITEM_INVENTORY_LDI")
            new_rtl_count = test_user_instance.get_table_row_count(user_name, "RETURN_TRANSACTION_LINE_LDI")
            new_i_count = test_user_instance.get_table_row_count(user_name, "item_ldi")
        
        logging.info("New row counts for ITEM_INVENTORY_PLAN_LDI is: %s" % (new_iip_count))
        logging.info("New row counts for ITEM_INVENTORY_LDI is: %s" % (new_ii_count))
        logging.info("New row counts for RETURN_TRANSACTION_LINE_LDI is: %s" % (new_rtl_count))
        logging.info("New row counts for item_ldi is: %s" % (new_i_count))
        
        # Abort if row mismatch between original and new counts.
        """
        # Will disable compare rows until resubmit deadlock query 
        if not tdtestpy.compare_results (org_iip_count, new_iip_count):
            failure_count += 1
            logging.error ("Row mismatch for ITEM_INVENTORY_PLAN_LDI table. Original rows: %s, New rows: %s" % (org_iip_count, new_iip_count))
            
        if not tdtestpy.compare_results (org_ii_count, new_ii_count):
            failure_count += 1
            logging.error ("Row mismatch for ITEM_INVENTORY_LDI table. Original rows: %s, New rows: %s" % (org_ii_count, new_ii_count))
            
        if not tdtestpy.compare_results (org_rtl_count, new_rtl_count):
            failure_count += 1
            logging.error ("Row mismatch for RETURN_TRANSACTION_LINE_LDI table. Original rows: %s, New rows: %s" % (org_rtl_count, new_rtl_count))
        
        if not tdtestpy.compare_results (org_i_count, new_i_count):
            failure_count += 1
            logging.error ("Row mismatch for item_ldi table. Original rows: %s, New rows: %s" % (org_i_count, new_i_count))
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

            
            CheckTableName = ("ITEM_INVENTORY_PLAN_LDI", "ITEM_INVENTORY_LDI", "RETURN_TRANSACTION_LINE_LDI", "item_ldi")
            CheckLevel = "two"
            check_log_name = user_name + "_ldi_write_checktable_" + iteration + ".log"
            checktable_log = os.path.join(ldi_tables_write, check_log_name)
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