# Author: tl151006

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
import string
import csv

# Check and validate input parameters
def setup_argparse():
    
    parser = argparse.ArgumentParser(description="### setup.py ###")
    parser.add_argument("--dbs_name", required=True, help="System name")
    parser.add_argument("--user_name", required=True, help="user_name")
    parser.add_argument("--user_password", required=True, help="user_password")

    return parser.parse_args()
                   
               
# Python exit wrapper function
def exit(ok=True):
    if ok is True or ok == 0:
        logging.info("================= End: Test Success!] =================")
        sys.exit(0)
    else:
        logging.info("================== End: Test Failed!] ==================")
        sys.exit(1)

if __name__ == "__main__":


    try:
        udaExec = teradata.UdaExec (appName="Hackathon0621", version="1.0", logConsole=True)
        
        args = setup_argparse()
        
        dbs_name = args.dbs_name
        user_name = args.user_name
        user_password = args.user_password
        con_method = "odbc"
        
        # Set logs variables
        test_path = os.path.dirname(os.path.realpath(__file__))
        test_log_name = os.path.join(test_path, "python_out.log")
        
        # dump python log to demo_log_path        
        fh = logging.FileHandler(test_log_name, mode="w", encoding="utf8")
        fh.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
        fh.setLevel(logging.DEBUG)
        root = logging.getLogger()
        root.addHandler(fh) 
        
        db_con = udaExec.connect(method=con_method, system=dbs_name, username=user_name, password=user_password)
        darts_con = udaExec.connect(method=con_method, system="biggulp", username="sit_admin", password="sit_admin")

                
        with db_con.cursor() as cursor:
            cursor.execute("select top 1 Signature, BackTraceText, VersionInfo from \
                            hack15.scanhistory_source \
                            where cast(LogTime as date FORMAT 'YYYY-MM-DD') > '2016-06-01' and Signature <> ''")
            results = cursor.fetchone()
            #signature = results[0]
            #backtrace = []
            versioninfo = results[2]
            
            #backtrace.append(results[1])

            
            #print (signature)
            #print (backtrace)
            print (versioninfo)
            versioninfo = versioninfo.strip()
            versionlist = versioninfo.split(',')
            versiondict = {}
            for i in versionlist:
                key = i.split(':')[0]
                value = i.split(':')[1]
                versiondict[key] = value
            #print (versiondict)
            
            """
            with open("key.txt", 'w') as f:
                f.write (signature + "\n")
                f.write (str(backtrace))
                f.write ("\n" + "\n" + "\n")
                f.write (results[1])
            """

        with darts_con.cursor() as cur:
            cur.execute("sel unique package_name, package_number from darts.scs \
                            where change_app_code = 'DR' \
                            and change_number = 171322 \
                            order by 1, 2")
            results = cur.fetchall()
            #print (versiondict['TDBMS'])
            #print ([row[1] for row in results])
            versionerror = False
            versionstring = ''
            for row in results:
                if (row[0]=='OPNPDE'):
                    row[0]='PDE'
                #print (versiondict[row[0]])
                versionstring += row[1] + ', '
                if (row[1]>versiondict[row[0]].strip()):
                    versionerror = True
            print (versionerror)
            print (versionstring[:-2])      
        
    except Exception as e:
        logging.error(traceback.format_exc())
        exit(1)
        
    exit(0)
