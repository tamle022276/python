#!/usr/bin/python3
# Author: tl151006
# File: ldi_and_pll_validate_result.py
# Date Published: 04/11/2016
# Purpose: Run Validate Result for LDI and PLL test
# Usage: python ldi_and_pll_validate_result.py --database_name=db_name --user_name=db_user --user_password=db_password --ignore_error=error_1,error_2,error_n
# ignore_error can none to many, it separate by comma and it is optional
# Example 1 with 2 ignore errors: python using_common_codes.py --database_name=hela --user_name=dbc --user_password=dbc --ignore_error=3822,3807
import sys
import os
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
import decimal
import threading, queue
import multiprocessing
import pickle
import json
os_user_name = getpass.getuser()
os_type = platform.system()
#if os_user_name == "tomcat":
#sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'common'))
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
    parser.add_argument("--iteration", required=True, help="Iteration Number of this run")
    parser.add_argument("--threadNum", required=True, help="threadNum Number of this run")
    parser.add_argument("--user_name", required=True, help="User name")
    parser.add_argument("--dbc_password", required=True, help="DBC password")
    parser.add_argument("--scriptPath", required=True, help="Get current Jmeter test plan path")
    parser.add_argument("--run_timestamp", required=True, help="Get current run time")
    parser.add_argument("--update_control_file", required=False, default="false", help="Update Control File?")
    parser.add_argument("--ignore_error", required=False, default=[],
            help="Error number should be ignored. Must be integers separated by commas.", action=IgnoreErrorAction)

    return parser.parse_args()

 
                                   
# Python exit wrapper function
def exit(ok=True):
    if ok is True or ok == 0:
        logging.info("================= End: Validate Result Success!] =================")
        sys.exit(0)
    else:
        logging.info("================== End: Validate Result Failed, Please Check Out ERROR Messages Above!] ==================")
        sys.exit(1)

if __name__ == "__main__":


    try:
        udaExec = teradata.UdaExec (appName="VALIDATE", version="1.0", logConsole=True)
        
        args = setup_argparse()
        
        dbs_name = args.dbs_name
        iteration = args.iteration
        threadNum = args.threadNum
        dbc_password = args.dbc_password
        scriptPath = args.scriptPath
        run_timestamp = args.run_timestamp
        user_name = args.user_name
        ignore_error = args.ignore_error
        update_control_file = args.update_control_file
        con_method = "odbc"
        
        
        # Set logs variables
        loopnum = "L" + iteration
        prior_run_id = int(iteration) - 1
        prior_user = user_name + "_validate_result_loop_" + str(prior_run_id) + ".log"
        testuser = user_name + "_validate_result_loop_" + iteration + ".log"
        validate_result = os.path.join(scriptPath, "output", dbs_name, run_timestamp, "latest")
        faileddir = os.path.join(scriptPath, "output", dbs_name, run_timestamp, "failed")
        passed_dir = os.path.join(scriptPath, "output", dbs_name, run_timestamp, "passed")
        
        test_log_name = os.path.join(validate_result, testuser)
        prior_log_name = os.path.join(validate_result, prior_user)
        validate_result_ignore_errors = tdtestpy.get_ignore_errors(common_error) + ignore_error 
        validate_fail_log = os.path.join(faileddir, "validate_fail_debug.log")
        controldir = os.path.join(scriptPath, "controlfiles")
        confrolname = "original_results.pickle"  
        controlfile = os.path.join(controldir, confrolname)
        fail_count = 0   

        # Remove old debug file
        tdtestpy.delete_one_file(validate_fail_log)
        tdtestpy.delete_one_file(prior_log_name)
              
        # dump python log to demo_log_path        
        fh = logging.FileHandler(test_log_name, mode="a", encoding="utf8")
        fh.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
        fh.setLevel(logging.DEBUG)
        root = logging.getLogger()
        root.addHandler(fh) 
                       
        # Start validate
        logging.info("================== Start validate Test ==================")
            
         
        with udaExec.connect(method="odbc", system=dbs_name, username=user_name, password=user_name) as db_connect:
                    
            validate_job = tdtestpy.SQLValidation (db_connect, controlfile, validate_fail_log)
            fail_count = 0
            # Delete old control file if need to create new, else load control file and assign expected results per each sql and compare. 
            if update_control_file == "true":
                tdtestpy.delete_one_file (controlfile)   
            else:
                allresults = validate_job.load_control_file()
                original_result1 = allresults["LDI_VALIDATE1"]
                original_result2 = allresults["LDI_VALIDATE2"]
                original_result3 = allresults["LDI_VALIDATE3"]
                original_result4 = allresults["LDI_VALIDATE4"]
                original_result5 = allresults["LDI_VALIDATE5"]
                original_result6 = allresults["LDI_VALIDATE6"]
                original_result7 = allresults["LDI_VALIDATE7"]
                original_result8 = allresults["LDI_VALIDATE8"]
                original_result9 = allresults["LDI_VALIDATE9"]
                original_result10 = allresults["LDI_VALIDATE10"]
                original_result11 = allresults["LDI_VALIDATE11"]
                original_result12 = allresults["LDI_VALIDATE12"]
                original_result13 = allresults["LDI_VALIDATE13"]
                original_result14 = allresults["LDI_VALIDATE14"]
                original_result15 = allresults["LDI_VALIDATE15"]
                original_result16 = allresults["LDI_VALIDATE16"]
                original_result17 = allresults["LDI_VALIDATE17"]
                original_result18 = allresults["LDI_VALIDATE18"]
                original_result19 = allresults["LDI_VALIDATE19"]
                original_result20 = allresults["LDI_VALIDATE20"]
                original_result21 = allresults["LDI_VALIDATE21"]
                original_result22 = allresults["LDI_VALIDATE22"]
                original_result23 = allresults["LDI_VALIDATE23"]
                original_result24 = allresults["LDI_VALIDATE24"]
                original_result25 = allresults["LDI_VALIDATE25"]
                original_result26 = allresults["LDI_VALIDATE26"]
                original_result27 = allresults["LDI_VALIDATE27"]
                original_result28 = allresults["LDI_VALIDATE28"]
                original_result29 = allresults["LDI_VALIDATE29"]
                original_result30 = allresults["LDI_VALIDATE30"]
                original_result31 = allresults["LDI_VALIDATE31"]
                original_result32 = allresults["LDI_VALIDATE32"]
                original_result33 = allresults["LDI_VALIDATE33"]
                original_result34 = allresults["LDI_VALIDATE34"]
                original_result35 = allresults["LDI_VALIDATE35"]
                original_result36 = allresults["LDI_VALIDATE36"]
                original_result37 = allresults["LDI_VALIDATE37"]
                original_result38 = allresults["LDI_VALIDATE38"]
                original_result39 = allresults["LDI_VALIDATE39"]
                original_result40 = allresults["LDI_VALIDATE40"]

                
            sql = """SELECT /*LDI_VALIDATE1*/ TOP 956 CHANNEL_0.CHANNEL_CD AS ALIAS_2,
                                CHANNEL_0.CHANNEL_CD AS ALIAS_3
                                FROM CHANNEL_V AS CHANNEL_0, CHANNEL_V AS CHANNEL_V_1
                                WHERE (CHANNEL_0.CHANNEL_CD LIKE 'CHANNEL07%') 
                                GROUP BY CHANNEL_0.CHANNEL_CD"""
            if update_control_file == "true":                  
                validate_job.create_control_file (sql, "LDI_VALIDATE1")
            else:
                if not validate_job.validate_sql_results(sql, original_result1):
                    fail_count += 1

                    
            sql = """SELECT /*LDI_VALIDATE2*/ DIVISION_0.DIVISION_LEVEL AS ALIAS_2, 
                                REGION_1.DIVISION_CD AS ALIAS_3 
                                FROM DIVISION_V AS DIVISION_0, REGION_V AS REGION_1 
                                WHERE (DIVISION_0.DIVISION_CD = REGION_1.DIVISION_CD AND 'q' IS NOT NULL) 
                                WITH KURTOSIS(REGION_1.REGION_MGR_ASSOCIATE_ID), REGR_SLOPE(REGION_1.REGION_MGR_ASSOCIATE_ID, 
                                DIVISION_0.DIVISION_MGR_ASSOCIATE_ID) BY 1 ASC, ALIAS_2 DESC ORDER BY 1"""
                                
            if update_control_file == "true":                  
                validate_job.create_control_file (sql, "LDI_VALIDATE2")
            else:
                if not validate_job.validate_sql_results(sql, original_result2):
                    fail_count += 1
                                
            sql = """SELECT /*LDI_VALIDATE3*/ r.REGION_CD, d.DISTRICT_CD, d.DISTRICT_NAME 
                                FROM DISTRICT_V d, REGION_V r 
                                WHERE d.REGION_CD=r.REGION_CD AND r.REGION_MGR_ASSOCIATE_ID = 100"""
                                
            if update_control_file == "true":                  
                validate_job.create_control_file (sql, "LDI_VALIDATE3")
            else:
                if not validate_job.validate_sql_results(sql, original_result3):
                    fail_count += 1
                    
            
            sql = """SELECT /*LDI_VALIDATE4*/ r.REGION_CD, d.DISTRICT_CD, d.DISTRICT_NAME 
                                FROM DISTRICT_V d, REGION_V r 
                                WHERE d.REGION_CD=r.REGION_CD AND d.DISTRICT_CD IN 
                                ('DIS1400','DIS0006', 'DIS1364', 'DIS1613', 'DIS1178')"""
                                
            if update_control_file == "true":                  
                validate_job.create_control_file (sql, "LDI_VALIDATE4")
            else:
                if not validate_job.validate_sql_results(sql, original_result4):
                    fail_count += 1
            
            sql = """SELECT /*LDI_VALIDATE5*/ TOP 60.367264 PERCENT WITH TIES 9 AS ALIAS_5, 
                                REGR_SXY(BRAND_OWNER_ORG_2.BRAND_PARTY_ID, BRAND_1.BRAND_PARTY_ID) AS ALIAS_6, 
                                MIN(BRAND_1.BRAND_CD) OVER () AS ALIAS_7 
                                FROM BRAND_V  AS BRAND_1 , BRAND_OWNER_ORG_V  AS BRAND_OWNER_ORG_2 
                                WHERE BRAND_OWNER_ORG_2.BRAND_PARTY_ID = BRAND_1.BRAND_PARTY_ID AND BRAND_1.BRAND_CD='BRANDCD0895' 
                                GROUP BY CUBE((BRAND_1.BRAND_PARTY_ID, BRAND_1.BRAND_CD), (BRAND_OWNER_ORG_2.BRAND_PARTY_ID, 
                                BRAND_OWNER_ORG_2.BRAND_PARTY_ID)) ORDER BY ALIAS_5"""
                                          
            if update_control_file == "true":                  
                validate_job.create_control_file (sql, "LDI_VALIDATE5")
            else:
                if not validate_job.validate_sql_results(sql, original_result5):
                    fail_count += 1
            
            
            sql = """SELECT /*LDI_VALIDATE6*/ DISTRICT_4.REGION_CD AS ALIAS_6, MIN(DISTINCT REGION_3.DIVISION_CD) AS ALIAS_8 
                                FROM LOCATION_TYPE_V AS LOCATION_TYPE_V_1, REGION_V  AS REGION_3, 
                                DISTRICT_V AS DISTRICT_4 WHERE REGION_3.REGION_CD = DISTRICT_4.REGION_CD 
                                GROUP BY DISTRICT_4.REGION_CD"""
                                
            if update_control_file == "true":                  
                validate_job.create_control_file (sql, "LDI_VALIDATE6")
            else:
                if not validate_job.validate_sql_results(sql, original_result6):
                    fail_count += 1
            
            sql = """SELECT /*LDI_VALIDATE7*/ COALESCE(8.0, 11.0) AS ALIAS_7, BRAND_0.BRAND_CD AS ALIAS_8 
                                FROM BRAND_V  AS BRAND_0 LEFT OUTER JOIN BRAND_OWNER_ORG_V  AS BRAND_OWNER_ORG_1 ON 
                                BRAND_OWNER_ORG_1.BRAND_PARTY_ID = BRAND_0.BRAND_PARTY_ID 
                                WHERE BRAND_0.BRAND_CD > 'BRANDCD0789' AND BRAND_0.BRAND_CD < 'BRANDCD0952'
                                EXPAND ON PERIOD '(2002-09-20 07:00:01, 2002-09-22 04:00:01)' AS ALIAS_6 BY  
                                ANCHOR SATURDAY AT TIME '14:20:01'"""
             
            if update_control_file == "true":                  
                validate_job.create_control_file (sql, "LDI_VALIDATE7")
            else:
                if not validate_job.validate_sql_results(sql, original_result7):
                    fail_count += 1
                                
            
            sql = """SELECT /*LDI_VALIDATE8*/ 'v' AS ALIAS_3, 12.0 AS ALIAS_4, 
                                13.0 AS ALIAS_5, CHANNEL_1.CHANNEL_CD AS ALIAS_6 
                                FROM CHANNEL_V  AS CHANNEL_1 
                                WHERE CHANNEL_1.CHANNEL_CD > 'CHANNEL0637' AND CHANNEL_1.CHANNEL_CD < 'CHANNEL0645'"""
                                
            if update_control_file == "true":                  
                validate_job.create_control_file (sql, "LDI_VALIDATE8")
            else:
                if not validate_job.validate_sql_results(sql, original_result8):
                    fail_count += 1
                    
            
            sql = """SELECT /*LDI_VALIDATE9*/ REGION_2.DIVISION_CD AS ALIAS_4, 
                                DIVISION_3.DIVISION_LEVEL AS ALIAS_5, REGION_2.REGION_NAME AS ALIAS_6, 
                                DISTRICT_1.DISTRICT_JSON AS ALIAS_7 
                                FROM REGION_V  AS REGION_2, DIVISION_V AS DIVISION_3, DISTRICT_V AS DISTRICT_1 
                                WHERE DIVISION_3.DIVISION_CD = REGION_2.DIVISION_CD 
                                AND REGION_2.REGION_CD = DISTRICT_1.REGION_CD 
                                AND DIVISION_3.DIVISION_LEVEL=0 
                                AND REGION_2.DIVISION_CD = 'DIV100'"""
                    
            if update_control_file == "true":                  
                validate_job.create_control_file (sql, "LDI_VALIDATE9")
            else:
                if not validate_job.validate_sql_results(sql, original_result9):
                    fail_count += 1
            
            
            sql = """SELECT /*LDI_VALIDATE10*/ BRAND_3.BRAND_CD AS ALIAS_5, BRAND_3.BRAND_PARTY_ID AS ALIAS_6 
                                FROM BRAND_OWNER_ORG_V  AS BRAND_OWNER_ORG_2, BRAND_V  AS BRAND_3 
                                WHERE BRAND_OWNER_ORG_2.BRAND_PARTY_ID = BRAND_3.BRAND_PARTY_ID AND 
                                BRAND_3.BRAND_CD > 'BRANDCD091797' AND BRAND_3.BRAND_CD < 'BRANDCD091900' 
                                ORDER BY BRAND_3.BRAND_CD ASC"""
            
            if update_control_file == "true":                  
                validate_job.create_control_file (sql, "LDI_VALIDATE10")
            else:
                if not validate_job.validate_sql_results(sql, original_result10):
                    fail_count += 1
                    
            sql = """SELECT /*LDI_VALIDATE11*/ CASE WHEN 'i' IN ('i', 'z', 'y', 'i', 'o', 'i', 'l') THEN 14 
                                WHEN MAX(DISTINCT DISTRICT_2.REGION_CD) <> 1 THEN 1 
                                END AS ALIAS_4, MIN(DISTINCT DISTRICT_2.REGION_CD) AS ALIAS_5, 
                                4 AS ALIAS_6 
                                FROM REGION_V  AS REGION_0, DIVISION_V  AS DIVISION_1, 
                                DISTRICT_V  AS DISTRICT_2 
                                WHERE REGION_0.REGION_CD = DISTRICT_2.REGION_CD 
                                GROUP BY REGION_0.DIVISION_CD"""
            
            if update_control_file == "true":                  
                validate_job.create_control_file (sql, "LDI_VALIDATE11")
            else:
                if not validate_job.validate_sql_results(sql, original_result11):
                    fail_count += 1
                   
            sql = """SELECT /*LDI_VALIDATE12*/ BRAND_1.BRAND_CD AS ALIAS_4,
                                18 AS ALIAS_5, '005F58B6D0'XB AS ALIAS_6 
                                FROM BRAND_V  AS BRAND_1 
                                WHERE BRAND_1.BRAND_CD > 'BRANDCD0895' AND BRAND_1.BRAND_CD < 'BRANDCD1000'"""
            
            if update_control_file == "true":                  
                validate_job.create_control_file (sql, "LDI_VALIDATE12")
            else:
                if not validate_job.validate_sql_results(sql, original_result12):
                    fail_count += 1
            
            sql = """SELECT /*LDI_VALIDATE13*/ MAX(BRAND_4.BRAND_CD) 
                                OVER (PARTITION BY BRAND_4.MFG ORDER BY BRAND_4.MFG) AS ALIAS_6 
                                FROM BRAND_V  AS BRAND_4 
                                WHERE BRAND_4.MFG > 'MFG066' AND BRAND_4.MFG < 'MFG076'"""
            
            if update_control_file == "true":                  
                validate_job.create_control_file (sql, "LDI_VALIDATE13")
            else:
                if not validate_job.validate_sql_results(sql, original_result13):
                    fail_count += 1
                            
                    
            sql = """SELECT /*LDI_VALIDATE14*/ ON_HAND_QTY, PRODUCT_ID, PLAN_QTY, WEEK_OF_YEAR, QTY_SOLD 
                                FROM ITEM_STORE_SOLD_V 
                                WHERE LOCATION_ID in (select a.LOCATION_ID from LOCATION_PLAN_V a, ITEM_STORE_SOLD_V b 
                                where a.LOCATION_ID = b.LOCATION_ID)  
                                and ON_HAND_QTY in (97744, 63584, 62924, 89844)"""
            
            if update_control_file == "true":                  
                validate_job.create_control_file (sql, "LDI_VALIDATE14")
            else:
                if not validate_job.validate_sql_results(sql, original_result14):
                    fail_count += 1                
                          
            sql = """SELECT /*LDI_VALIDATE15*/ TOP 58.696167 PERCENT WITH TIES COST_1.COST_TOTAL AS ALIAS_3,
              COST_1.COST_CD AS ALIAS_4, ACCOUNT AS ALIAS_5
               FROM COST_V AS COST_1
               WHERE COST_CD = 'COST096' AND COST_DESC IS NOT NULL
             ORDER BY ALIAS_5 ASC"""
            
            if update_control_file == "true":                  
                validate_job.create_control_file (sql, "LDI_VALIDATE15")
            else:
                if not validate_job.validate_sql_results(sql, original_result15):
                    fail_count += 1
                    
            sql = """SELECT /*LDI_VALIDATE16*/ COST_3.COST_CD AS ALIAS_6, 
                                COST_3.COST_TOTAL AS ALIAS_7, COST_3.COST_VALUE AS ALIAS_8 
                                FROM COST_V AS COST_3 
                                WHERE COST_3.COST_CD IN 
                                ('COST076','COST089','COST059','COST045','COST052','COST048','COST079','COST083','COST093','COST019')"""
            
            if update_control_file == "true":                  
                validate_job.create_control_file (sql, "LDI_VALIDATE16")
            else:
                if not validate_job.validate_sql_results(sql, original_result16):
                    fail_count += 1
            
            
            sql = """SELECT /*LDI_VALIDATE17*/ DISTRICT_3.REGION_CD AS ALIAS_4,
            COUNT(BRAND_2.BRAND_PARTY_ID) OVER (PARTITION BY 14.01, 9.01, 8.01 ORDER BY BRAND_2.BRAND_PARTY_ID) AS ALIAS_5, 
            MAX(BRAND_OWNER_ORG_1.BRAND_PARTY_ID) AS ALIAS_6,
              DISTRICT_3.REGION_CD AS ALIAS_8
               FROM ALL_DIVISIONS_V AS ALL_DIVISIONS_V_0, BRAND_OWNER_ORG_V  AS BRAND_OWNER_ORG_1,
                   BRAND_V AS BRAND_2, DISTRICT_V  AS DISTRICT_3
               WHERE BRAND_OWNER_ORG_1.BRAND_PARTY_ID = BRAND_2.BRAND_PARTY_ID AND BRAND_2.BRAND_CD='BRANDCD0441'
               GROUP BY BRAND_2.BRAND_PARTY_ID, DISTRICT_3.REGION_CD"""
            
            if update_control_file == "true":                  
                validate_job.create_control_file (sql, "LDI_VALIDATE17")
            else:
                if not validate_job.validate_sql_results(sql, original_result17):
                    fail_count += 1
            
            sql = """SELECT /*LDI_VALIDATE18*/ DISTRICT_3.REGION_CD AS ALIAS_4,
              COUNT(BRAND_2.BRAND_PARTY_ID) OVER (PARTITION BY 14.01, 9.01, 8.01 ORDER BY BRAND_2.BRAND_PARTY_ID) 
              AS ALIAS_5, MAX(BRAND_OWNER_ORG_1.BRAND_PARTY_ID) AS ALIAS_6,
              DISTRICT_3.REGION_CD AS ALIAS_8
               FROM ALL_DIVISIONS_V AS ALL_DIVISIONS_V_0, BRAND_OWNER_ORG_V  AS BRAND_OWNER_ORG_1,
                   BRAND_V AS BRAND_2, DISTRICT_V  AS DISTRICT_3
               WHERE BRAND_OWNER_ORG_1.BRAND_PARTY_ID = BRAND_2.BRAND_PARTY_ID AND BRAND_2.BRAND_CD='BRANDCD0931'
               GROUP BY BRAND_2.BRAND_PARTY_ID, DISTRICT_3.REGION_CD"""
            
            if update_control_file == "true":                  
                validate_job.create_control_file (sql, "LDI_VALIDATE18")
            else:
                if not validate_job.validate_sql_results(sql, original_result18):
                    fail_count += 1
            
            sql = """SELECT /*LDI_VALIDATE19*/ BRAND_1.BRAND_PARTY_ID AS ALIAS_3,
              MIN(BRAND_OWNER_ORG_2.BRAND_PARTY_ID) AS ALIAS_4, REGR_SLOPE(BRAND_OWNER_ORG_2.BRAND_PARTY_ID, 
              BRAND_OWNER_ORG_2.BRAND_PARTY_ID) AS ALIAS_5,
              BRAND_1.BRAND_CD AS ALIAS_6
               FROM ALL_DIVISIONS_V AS ALL_DIVISIONS_V_0, BRAND_V AS BRAND_1, BRAND_OWNER_ORG_V  AS BRAND_OWNER_ORG_2
               WHERE BRAND_OWNER_ORG_2.BRAND_PARTY_ID = BRAND_1.BRAND_PARTY_ID AND BRAND_1.BRAND_CD='BRANDCD0195'
               GROUP BY CUBE(BRAND_1.BRAND_PARTY_ID, BRAND_OWNER_ORG_2.BRAND_PARTY_ID,
                 BRAND_1.BRAND_CD), CUBE(BRAND_OWNER_ORG_2.BRAND_PARTY_ID,
                   TD_DAY_OF_WEEK(DATE '2003-03-30'))"""
            
            if update_control_file == "true":                  
                validate_job.create_control_file (sql, "LDI_VALIDATE19")
            else:
                if not validate_job.validate_sql_results(sql, original_result19):
                    fail_count += 1
            
            sql = """SELECT /*LDI_VALIDATE20*/ DISTRICT_CD AS ALIAS_1, DISTRICT_NAME AS ALIAS_2, 
                REGION_1.REGION_CD AS ALIAS_3
               FROM DISTRICT_V  AS DISTRICT_0, REGION_V  AS REGION_1
               WHERE DISTRICT_0.REGION_CD = REGION_1.REGION_CD AND REGION_1.REGION_CD = 'REG19'"""
            
            if update_control_file == "true":                  
                validate_job.create_control_file (sql, "LDI_VALIDATE20")
            else:
                if not validate_job.validate_sql_results(sql, original_result20):
                    fail_count += 1
            
            sql = """SELECT /*LDI_VALIDATE21*/ DISTRICT_CD AS ALIAS_1, DISTRICT_NAME AS ALIAS_2, 
                REGION_1.REGION_CD AS ALIAS_3
               FROM DISTRICT_V  AS DISTRICT_0, REGION_V  AS REGION_1
               WHERE DISTRICT_0.REGION_CD = REGION_1.REGION_CD AND DISTRICT_CD = 'DIS0295'"""
            
            if update_control_file == "true":                  
                validate_job.create_control_file (sql, "LDI_VALIDATE21")
            else:
                if not validate_job.validate_sql_results(sql, original_result21):
                    fail_count += 1
                    
            
            sql = """SELECT /*LDI_VALIDATE22*/ REGION_CD AS ALIAS_1, DIVISION_NAME AS ALIAS_2, 
                REGION_1.DIVISION_CD AS ALIAS_3
               FROM DIVISION_V  AS DIVISION_0, REGION_V  AS REGION_1
               WHERE DIVISION_0.DIVISION_CD = REGION_1.DIVISION_CD AND REGION_1.REGION_CD = 'REG07'"""
            
            if update_control_file == "true":                  
                validate_job.create_control_file (sql, "LDI_VALIDATE22")
            else:
                if not validate_job.validate_sql_results(sql, original_result22):
                    fail_count += 1
            
            sql = """SELECT /*LDI_VALIDATE23*/ REGION_CD AS ALIAS_1, DIVISION_NAME AS ALIAS_2, 
                REGION_1.DIVISION_CD AS ALIAS_3
               FROM DIVISION_V  AS DIVISION_0, REGION_V  AS REGION_1
               WHERE DIVISION_0.DIVISION_CD = REGION_1.DIVISION_CD AND REGION_1.DIVISION_CD = 'DIV100'"""
            
            if update_control_file == "true":                  
                validate_job.create_control_file (sql, "LDI_VALIDATE23")
            else:
                if not validate_job.validate_sql_results(sql, original_result23):
                    fail_count += 1
                    
            sql = """SELECT /*LDI_VALIDATE24*/ DIVISION_CD AS ALIAS_1, DIVISION_NAME AS ALIAS_2, 
                ALL_DIVISIONS_1.ALL_DIVISIONS_CD AS ALIAS_3
               FROM DIVISION_V  AS DIVISION_0, ALL_DIVISIONS_V  AS ALL_DIVISIONS_1
               WHERE DIVISION_0.ALL_DIVISIONS_CD = ALL_DIVISIONS_1.ALL_DIVISIONS_CD"""
            
            if update_control_file == "true":                  
                validate_job.create_control_file (sql, "LDI_VALIDATE24")
            else:
                if not validate_job.validate_sql_results(sql, original_result24):
                    fail_count += 1
            
            sql = """SELECT /*LDI_VALIDATE25*/ DIVISION_CD AS ALIAS_1, ALL_DIVISIONS_NAME AS ALIAS_2, 
                ALL_DIVISIONS_1.ALL_DIVISIONS_CD AS ALIAS_3
               FROM DIVISION_V  AS DIVISION_0, ALL_DIVISIONS_V  AS ALL_DIVISIONS_1
               WHERE ALL_DIVISIONS_1.ALL_DIVISIONS_NAME = 'PAUNCH'"""
            
            if update_control_file == "true":                  
                validate_job.create_control_file (sql, "LDI_VALIDATE25")
            else:
                if not validate_job.validate_sql_results(sql, original_result25):
                    fail_count += 1
            
            sql = """SELECT /*LDI_VALIDATE26*/ CAST (BRAND_PARTY_ID AS INT), CAST (MAX(BRAND_PARTY_ID) AS INT)
               FROM BRAND_OWNER_ORG_V  AS BRAND_OWNER_ORG_0
               WHERE BRAND_PARTY_ID IS NOT NULL
              GROUP BY BRAND_PARTY_ID"""
            
            if update_control_file == "true":                  
                validate_job.create_control_file (sql, "LDI_VALIDATE26")
            else:
                if not validate_job.validate_sql_results(sql, original_result26):
                    fail_count += 1
            
            sql = """SELECT /*LDI_VALIDATE27*/ CAST (BRAND_PARTY_ID AS INT), 
                CAST (BRAND_PARTY_ID AS DECIMAL(38,2)), CAST (BRAND_PARTY_ID AS BIGINT)
               FROM BRAND_OWNER_ORG_V  AS BRAND_OWNER_ORG_0
               WHERE BRAND_PARTY_ID IS NOT NULL
              GROUP BY BRAND_PARTY_ID"""
            
            if update_control_file == "true":                  
                validate_job.create_control_file (sql, "LDI_VALIDATE27")
            else:
                if not validate_job.validate_sql_results(sql, original_result27):
                    fail_count += 1
                    
            sql = """SELECT /*LDI_VALIDATE28*/ COST_CD, COST_DESC, COST_GRADE
               FROM COST_V  AS COST_0
               WHERE COST_CD = 'COST041' AND COST_DESC IS NOT NULL"""
               # WHERE COST_CD = 'COST011' AND COST_DESC IS NOT NULL
            
            if update_control_file == "true":                  
                validate_job.create_control_file (sql, "LDI_VALIDATE28")
            else:
                if not validate_job.validate_sql_results(sql, original_result28):
                    fail_count += 1
            
            sql = """SELECT /*LDI_VALIDATE29*/ COST_CD, COST_DESC, COST_GRADE
               FROM COST_V  AS COST_0
               WHERE (COST_CD > 'COST033' AND COST_CD < 'COST045') AND COST_DESC IS NOT NULL"""
            
            if update_control_file == "true":                  
                validate_job.create_control_file (sql, "LDI_VALIDATE29")
            else:
                if not validate_job.validate_sql_results(sql, original_result29):
                    fail_count += 1
            
            sql = """SELECT /*LDI_VALIDATE30*/ PRICE_CHANGE_REASON_CD, PRICE_CHANGE_REASON_DESC, PRICE_CHANGE_LEVEL
               FROM PRICE_CHANGE_REASON_V  AS PRICE_CHANGE_REASON_0
               WHERE (PRICE_CHANGE_REASON_CD > 'CHNGRSN022' AND PRICE_CHANGE_REASON_CD < 'CHNGRSN070')"""
            
            if update_control_file == "true":                  
                validate_job.create_control_file (sql, "LDI_VALIDATE30")
            else:
                if not validate_job.validate_sql_results(sql, original_result30):
                    fail_count += 1
            
            sql = """SELECT /*LDI_VALIDATE31*/ PRICE_CHANGE_REASON_CD, PRICE_CHANGE_REASON_DESC, PRICE_CHANGE_LEVEL
               FROM PRICE_CHANGE_REASON_V  AS PRICE_CHANGE_REASON_0
               WHERE (PRICE_CHANGE_REASON_CD > 'CHNGRSN089' AND PRICE_CHANGE_REASON_CD < 'CHNGRSN100') AND PRICE_CHANGE_LEVEL=2
              ORDER BY 1 DESC"""
            
            if update_control_file == "true":                  
                validate_job.create_control_file (sql, "LDI_VALIDATE31")
            else:
                if not validate_job.validate_sql_results(sql, original_result31):
                    fail_count += 1

            sql = """SELECT /*LDI_VALIDATE32*/ PRICE_CHANGE_REASON_CD, PRICE_CHANGE_REASON_DESC, PRICE_CHANGE_LEVEL
               FROM PRICE_CHANGE_REASON_V  AS PRICE_CHANGE_REASON_0
              WHERE (PRICE_CHANGE_REASON_CD > 'CHNGRSN030' AND PRICE_CHANGE_REASON_CD < 'CHNGRSN070') AND PRICE_CHANGE_LEVEL=1
              ORDER BY 1 DESC"""
            
            if update_control_file == "true":                  
                validate_job.create_control_file (sql, "LDI_VALIDATE32")
            else:
                if not validate_job.validate_sql_results(sql, original_result32):
                    fail_count += 1
            
            sql = """SELECT /*LDI_VALIDATE33*/ PRICE_CHANGE_REASON_CD, PRICE_CHANGE_REASON_DESC, PRICE_CHANGE_LEVEL
               FROM PRICE_CHANGE_REASON_V  AS PRICE_CHANGE_REASON_0
               WHERE (PRICE_CHANGE_REASON_CD > 'CHNGRSN054' AND PRICE_CHANGE_REASON_CD < 'CHNGRSN090') AND PRICE_CHANGE_LEVEL=0
              ORDER BY 1 DESC"""
            
            if update_control_file == "true":                  
                validate_job.create_control_file (sql, "LDI_VALIDATE33")
            else:
                if not validate_job.validate_sql_results(sql, original_result33):
                    fail_count += 1
            
            sql = """SELECT /*LDI_VALIDATE34*/ LOCATION_TYPE_CD, LOCATION_TYPE_DESC, LOCATION_COST
               FROM LOCATION_TYPE_V  AS LOCATION_TYPE_0
               WHERE LOCATION_TYPE_CD='LOCTYP047'"""
            
            if update_control_file == "true":                  
                validate_job.create_control_file (sql, "LDI_VALIDATE34")
            else:
                if not validate_job.validate_sql_results(sql, original_result34):
                    fail_count += 1
            
            sql = """SELECT /*LDI_VALIDATE35*/ CHANNEL_CD, CHANNEL_DESC
               FROM CHANNEL_V  AS CHANNEL_0
               WHERE CHANNEL_CD='CHANNEL002'
              ORDER BY 1 DESC"""
            
            if update_control_file == "true":                  
                validate_job.create_control_file (sql, "LDI_VALIDATE35")
            else:
                if not validate_job.validate_sql_results(sql, original_result35):
                    fail_count += 1
            
            sql = """SELECT /*LDI_VALIDATE36*/ CHANNEL_CD, CHANNEL_DESC
               FROM CHANNEL_V  AS CHANNEL_0
               WHERE CHANNEL_DESC='transferability'
              ORDER BY 1 DESC"""
            
            if update_control_file == "true":                  
                validate_job.create_control_file (sql, "LDI_VALIDATE36")
            else:
                if not validate_job.validate_sql_results(sql, original_result36):
                    fail_count += 1

            
            sql = """SELECT /*LDI_VALIDATE37*/ ROW_NUMBER() OVER (PARTITION BY REGION_2.REGION_MGR_ASSOCIATE_ID 
                ORDER BY REGION_2.REGION_CD, LOCATION_TYPE_0.LOCATION_TYPE_CD) AS ALIAS_3,
              MAX(REGION_2.REGION_NAME) OVER (PARTITION BY REGION_2.REGION_CD,
              DIVISION_1.DIVISION_CD ORDER BY DIVISION_1.DIVISION_CD, REGION_2.REGION_CD, REGION_2.REGION_CD) AS ALIAS_4
               FROM LOCATION_TYPE  AS LOCATION_TYPE_0, DIVISION  AS DIVISION_1, REGION
              AS REGION_2
               WHERE DIVISION_1.DIVISION_CD = REGION_2.DIVISION_CD AND REGION_2.DIVISION_CD = 'DIV002'"""
            
            if update_control_file == "true":                  
                validate_job.create_control_file (sql, "LDI_VALIDATE37")
            else:
                if not validate_job.validate_sql_results(sql, original_result37):
                    fail_count += 1
            
            sql = """SELECT /*LDI_VALIDATE38*/ TOP 630 WITH TIES MIN('000B49E15F'XB) AS ALIAS_2,
              MIN('s') AS ALIAS_3, 9.0 AS ALIAS_4, 17.0 AS ALIAS_5, 't' AS ALIAS_6
               FROM PRICE_CHANGE_REASON_V AS PRICE_CHANGE_REASON_V_0, LOCATION_TYPE_V AS LOCATION_TYPE_V_1
               WHERE (PRICE_CHANGE_REASON_V_0.PRICE_CHANGE_REASON_CD > 'CHNGRSN008' 
               AND PRICE_CHANGE_REASON_V_0.PRICE_CHANGE_REASON_CD < 'CHNGRSN25') AND PRICE_CHANGE_REASON_V_0.PRICE_CHANGE_LEVEL=0
               GROUP BY (DATE '2003-08-01' - DATE '2011-10-06') MONTH(3)"""
            
            if update_control_file == "true":                  
                validate_job.create_control_file (sql, "LDI_VALIDATE38")
            else:
                if not validate_job.validate_sql_results(sql, original_result38):
                    fail_count += 1

            sql = """SELECT /*LDI_VALIDATE39*/ TOP 1.9768894 PERCENT WITH TIES DIVISION_2.DIVISION_CD AS ALIAS_3,
              DIVISION_2.DIVISION_MGR_ASSOCIATE_ID AS ALIAS_4
               FROM REGION_V AS REGION_V_0, (REGION  AS REGION_1 FULL OUTER JOIN DIVISION AS DIVISION_2 
               ON DIVISION_2.DIVISION_CD = REGION_1.DIVISION_CD)
               WHERE DIVISION_2.DIVISION_CD = REGION_1.DIVISION_CD AND REGION_1.REGION_CD = 'REG01'"""
            
            if update_control_file == "true":                  
                validate_job.create_control_file (sql, "LDI_VALIDATE39")
            else:
                if not validate_job.validate_sql_results(sql, original_result39):
                    fail_count += 1
            
            sql = """SELECT /*LDI_VALIDATE40*/ TOP 254 REGION_2.REGION_CD AS ALIAS_4,
              REGION_2.DIVISION_CD AS ALIAS_5
               FROM DIVISION_V AS DIVISION_V_0,
                   REGION_V AS REGION_2
               WHERE DIVISION_V_0.DIVISION_CD = REGION_2.DIVISION_CD 
               AND (REGION_2.REGION_CD > 'REG11' AND REGION_2.REGION_CD < 'REG19')"""
               # AND (REGION_2.REGION_CD > 'REG82' AND REGION_2.REGION_CD < 'REG90')
            
            if update_control_file == "true":                  
                validate_job.create_control_file (sql, "LDI_VALIDATE40")
            else:
                if not validate_job.validate_sql_results(sql, original_result40):
                    fail_count += 1
            
                                                                                                                  
            #sample_control_file = os.path.join(faileddir, "sample_control_file.log")
            #allresults = validate_job.load_control_file()
            #with open(sample_control_file, 'w') as f:
            #    for k, v in allresults.items():
            #        f.write(k + ": ") 
            #        f.write(str(v))
            #        f.write("\n\n")
                        
            #logging.info("sample control file here: %s" % (sample_control_file))
            

        if fail_count != 0:
            tdtestpy.copy_file (test_log_name, faileddir)
            logging.info("Please review fail output file here: %s" % (validate_fail_log))
            tdtestpy.copy_file (test_log_name, faileddir)
            exit(1)

        # Copy logs to passed if nothing wrong
        tdtestpy.copy_file (test_log_name, passed_dir)
        
    except Exception as e:
        logging.error(traceback.format_exc())
        tdtestpy.copy_file (test_log_name, faileddir)
        exit(1)
        
    exit(0)
