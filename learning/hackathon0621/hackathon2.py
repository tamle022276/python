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
import ast

# Check and validate input parameters
def setup_argparse():
    
    parser = argparse.ArgumentParser(description="### setup.py ###")
    parser.add_argument("--dbs_name", required=True, help="System name")
    parser.add_argument("--user_name", required=True, help="user_name")
    parser.add_argument("--user_password", required=True, help="user_password")

    return parser.parse_args()

def get_key (db_con):
    with db_con.cursor() as cursor:
        cursor.execute("select Signature, BackTraceText, VersionInfo from \
                        hack15.scanhistory_source \
                        where cast(LogTime as date FORMAT 'YYYY-MM-DD') > '2016-06-01' \
                        and Signature <> '' sample 1")
        results = cursor.fetchone()
        signature = results[0]
        backtrace = []
        versioninfo = results[2]  
        backtrace.append(results[1])
        

        versioninfo = versioninfo.strip()
        versionlist = versioninfo.split(',')
        versiondict = {}
        for i in versionlist:
            key = i.split(':')[0]
            value = i.split(':')[1]
            versiondict[key] = value
                
        
    return signature, backtrace, versiondict

def get_package (db_con, dr_num):
    with db_con.cursor() as cursor:
        cursor.execute("sel unique package_name, package_number from darts.scs \
                            where change_app_code = 'DR' \
                            and change_number = %s \
                            order by 1, 2" % (dr_num))
        results = cursor.fetchall()
        
        #versionstring = ''
        package_number = []
        for row in results:
            package_name = row[0]
            #versionstring += row[1] + ', '
            package_number.append( row[1])
            
    
        return package_name, package_number
                        
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
        
        report_time = time.strftime("%Y-%m-%d-%H-%M")
        
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
        #aws_con = udaExec.connect(method=con_method, system="tdmpp02.teradatalabs.net", username="hack15user", password="daedalusclass268")
        
        sql = """LOCK ROW FOR ACCESS
                SELECT DISTINCT PC.Change_Number (title 'DR')
                  , PC.Priority_Code (title 'Pri.')
                  , CAST(PC.Abstract AS CHAR(100))
                  , PC.PC_Overall_Status_Code (title 'Status')
                 /* , CASE WHEN PC.Blocker_Flag = 'Y' THEN 'BLOCKER' ELSE '       ' END */
                  , CAST(PC_Summary.PC_Detail_Status_Description AS VARCHAR(40))(title 'Detail Status')
                  , PC.Created_DateTime (title 'Creation Date')
                  , PC.Last_Change_Datetime (title 'Last Update')
                FROM darts.pc
                
                JOIN DARTS.PC_Summary
                ON PC.change_app_code = PC_Summary.Change_App_Code
                AND PC.Change_Number = PC_Summary.Change_Number
                AND PC.PC_Detail_Status_Code = PC_Summary.PC_Detail_Status_Code
                
                JOIN (
                SELECT member_app_code
                , member_number
                , rrm.change_app_code
                , rrm.change_number
                , relationship_code
                FROM darts.rrm
                JOIN
                (SELECT change_app_code
                  , change_number
                FROM darts.ctnt
                WHERE TEXT LIKE ALL ( %s )
                ) AS a
                ON rrm.change_app_code = a.change_app_code
                AND rrm.change_number = a.change_number
                WHERE 1=1
                AND rrm.change_app_code = 'DR'
                AND rrm.Relationship_Code = 'RPLBY'
                UNION
                SELECT change_app_code
                , change_number
                , 'DR'
                , change_number
                , ''
                FROM darts.ctnt
                WHERE TEXT LIKE ALL ( %s )
                ) AS a
                ON a.member_number = pc.change_number
                AND a.member_app_code = pc.change_app_code
                
                LEFT JOIN darts.scs
                ON pc.change_app_code = scs.change_app_code
                AND pc.change_number = scs.change_number
                LEFT JOIN DARTS.CRSN
                ON CRSN.Close_Reason_Code = PC.Close_Reason_Code
                LEFT JOIN DARTS.PVC
                  ON PVC.Change_App_Code = PC.Change_App_Code
                  AND PVC.Change_Number = PC.Change_Number
                  AND PVC.Target_For_Flag = 'Y'
                  WHERE
                -- PC.Created_DateTime > '2011-01-01 00:00:00' AND
                  (
                  pc.PC_Overall_Status_Code = 'OPEN' OR
                  pc.PC_Overall_Status_Code = 'WAIT' OR
                  pc.PC_Overall_Status_Code = 'COMPLETE' OR
                  pc.PC_Overall_Status_Code = 'STVTEST' OR
                  pc.PC_Overall_Status_Code = 'BUILD' OR
                  pc.PC_Overall_Status_Code = 'CLOSED' )
                GROUP BY PC.Change_Number
                  , PC.Priority_Code
                  , PC.Change_APp_Code
                  , PC.Abstract
                  , PC.Blocker_Flag
                  , PC.PC_Overall_Status_Code
                  , PC.PC_Detail_Status_Code
                  , PC_Summary.PC_Detail_Status_Description
                  , member_number
                  , a.change_number
                  , PC.Created_DateTime
                  , PC.Last_Change_Datetime
                ORDER BY PC.Created_DateTime desc"""

        signature, backtrace, versiondict = get_key (db_con)
        
        #output_log = os.path.join(test_path, "ebay_" + report_time + ".csv")
        output_log = os.path.join(test_path, "ebay.csv")
               
        with darts_con.cursor() as cursor:
            cursor.execute(sql % (signature, signature))
            num_row = cursor.rowcount
            
            while num_row == 0:
                signature, backtrace, versiondict = get_key (db_con)
                cursor.execute(sql % (signature, signature))
                num_row = cursor.rowcount
                
            columns_description = cursor.description
            
            results = cursor.fetchall()
            
            #delimiter = "|"
            with open(output_log, 'w') as f:
                writer = csv.writer (f)
                #header = ([i[0] for i in columns_description])
                header = ['DR Number', 'Priority', 'Abstract', 'Status', 'Detail Status', 'Creation Date', 'Last Update', 'Package Name', 'Releases Shipped']
                writer.writerows([backtrace])
                #writer.writerows(header)
                writer.writerows([header])
                writer.writerows([])
                writer.writerows([])
                writer.writerows([])
                
                for row in results:
                    #sqlrow = [ str(row[0]) + ", " + str(row[1]) + ", " + row[2] + ", " + row[3] + ", " \
                    #        + row[4] + ", " + row[5].strftime('%d %B %Y') + ", " + row[6].strftime('%d %B %Y') ]
                    
                    package_name, versionstring = get_package (darts_con, str(row[0]))
                    
                    sqlrow = []
                    sqlrow.append(r'=HYPERLINK("https://darts.td.teradata.com:7443/darts/showPC.cfm?Change_App_Code=DR&Change_Number=' \
                                  + str(row[0]) + r'", "' + str(row[0]) + r'")')
                    sqlrow.append(str(row[1]))
                    sqlrow.append(str(row[2]))
                    sqlrow.append(str(row[3]))
                    sqlrow.append(str(row[4]))
                    sqlrow.append(row[5].strftime('%d %B %Y'))
                    sqlrow.append(row[6].strftime('%d %B %Y'))
                    sqlrow.append(package_name)
                    sqlrow.append(versionstring)
                
                    #writer.writerow(sqlrow) 
                    #writer.writerow([sqlrow])
                    writer.writerow(sqlrow)
 
                    print (sqlrow) 
                
            
            """  
            with open(output_log, 'w') as f:
                for row in results:
                    f.write ((row))
                    print (res[0])
                    print (type(row))
                    print (type(res[0]))
            """
            
                    
    except Exception as e:
        logging.error(traceback.format_exc())
        exit(1)
        
    exit(0)
