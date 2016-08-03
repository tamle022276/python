# Author: tl151006
# File: test_python.py
# Date Published: 04/22/2016
# Purpose: Pythong testing
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
import pickle
import glob

os_user_name = getpass.getuser()
os_type = platform.system()
working_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(working_dir, '..', 'common')) 
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
    parser.add_argument("--dbsName", required=True, help="System name")
    parser.add_argument("--user_name", required=True, help="user_name")
    parser.add_argument("--user_password", required=True, help="user_password")
    parser.add_argument("--ignore_error", required=False, default=[],
            help="Error number should be ignored. Must be integers separated by commas.", action=IgnoreErrorAction)

    return parser.parse_args()

def run_sql_file (db_connect, sql_queries, ignore_errors=None):
    if ignore_errors is None:
        ignore_errors = [0000]
    with db_connect.cursor() as cursor:
        try:
            cursor.execute(file=sql_queries, ignoreErrors=ignore_errors)
            return True
        except Exception as e:
            print ("Test failed with error: %s" % ((e.args[0])))
            return False

class Tail_Logs (object):
    
    def __init__(self, logs_directory, logs_extension, num_lines = 10, interval = 10):
        self.logs_directory = logs_directory
        self.logs_extension = logs_extension
        self.num_lines = num_lines
        self.interval = interval
        
    def get_tail_file (self):
        tail_logs = os.path.join(self.logs_directory, self.logs_extension)
        original_list = []
        new_list = []       
        for file in glob.glob("/qd0047/jenkins/jobs/CI-TestDev/jobs/tqst_ldi_pll/workspace/tqst_ldi_pll/output/snorri/2016-06-08-16-18/latest/*.log"):
            fname = (file + "|" + time.ctime(os.path.getmtime(file)))
            new_list.append( fname )
            
        tail_list = list(set(new_list) - set(original_list))
        
        for i in tail_list:
            tail_file = i.split('|')[0]
            last_update = i.split('|')[1]
            
            tail_messages = self.tail(tail_file, self.num_lines)
            logging.info("Tail File: %s" % (tail_file))
            logging.info("Last Updated On: %s" % (last_update))
            logging.info("Here are the last %s lines" % (self.num_lines))
            for each_line in tail_messages:
                print (each_line)
            logging.info("############################### Tail end for this file #########################################\n \n \n")

    
    def tail(self, file, n, offset=None):
        with open (file, "r") as f:
            avg_line_length = 74
            to_read = n + (offset or 0)
            while 1:
                try:
                    f.seek(-(avg_line_length * to_read), 2)
                except IOError:
                    # woops.  apparently file is smaller than what we want
                    # to step back, go to the beginning instead
                    f.seek(0)
                pos = f.tell()
                lines = f.read().splitlines()
                if len(lines) >= to_read or pos == 0:
                    return lines[-to_read:offset and -offset or None]
                avg_line_length *= 1.3
        
def test_cont(db_con):

    sql = "select * from dbc.dbcinf"
    ignore_error = [3807,3808]
    retry_list = [3807]
    numtry = 1
    maxtry = 3
    
    cursor = db_con.cursor()
            
    def run_sql(sql):
            try:
                #with db_con.cursor() as cursor:
                cursor.execute(sql)
            except Exception as e:
                if e.code in ignore_error and e.code in retry_list:
                    return True     
                else:
                    return False, str(e)
                
    while numtry < maxtry:
        print ("try " + str(numtry))
        if not run_sql(sql):
            numtry = maxtry
        else:    
            numtry += 1
            


               
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
        udaExec = teradata.UdaExec (appName="PYTEST", version="1.0", logConsole=True)
        
        args = setup_argparse()
        
        dbsName = args.dbsName
        user_name = args.user_name
        user_password = args.user_password
        ignore_error = args.ignore_error
        con_method = "odbc"
        
        # Set logs variables
        test_path = os.path.dirname(os.path.realpath(__file__))
        test_log_name = os.path.join(test_path, "output", "python_out.log")
        test_ignore_errors = tdtestpy.get_ignore_errors(common_error) + ignore_error
 
        # Sql File  
        create_user_queries = os.path.join(test_path, "create_user.txt")
        test_queries = os.path.join(test_path, "queries1.txt")
        
        # dump python log to demo_log_path        
        fh = logging.FileHandler(test_log_name, mode="w", encoding="utf8")
        fh.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
        fh.setLevel(logging.DEBUG)
        root = logging.getLogger()
        root.addHandler(fh) 
        
        
        dbc_con = udaExec.connect(method=con_method, system=dbsName, username=user_name, password=user_password)
        
        """
        # Testing tail logs
        #get_tail_file ()
        my_tails = Tail_Logs (logs_directory = "/qd0047/jenkins/jobs/CI-TestDev/jobs/tqst_ldi_pll/workspace/tqst_ldi_pll/output/snorri/2016-06-08-16-18/latest", \
                              logs_extension = "*.log")
        
        my_tails.get_tail_file()
        """
        
        
        # Testing for GetSQLResults
        output_file = "test_output.log"
        tdtestpy.delete_one_file(output_file)
        sql = "select * from dbc.dbcinf"
        write_results = tdtestpy.SaveSQLResults (dbc_con, output_file, test_ignore_errors, delimiter = ',', data_only = False, retlimit = 2)
        
        if not write_results.run_sql (sql):
            exit(1)
        
        sql_file = os.path.join(working_dir, "sql.txt")
        
        if not write_results.run_file (sql_file):
            exit(1)
        
        
        #test_cont (dbc_con)
        
        
        """
        
        # Create DB connection
        dbc_con = udaExec.connect(method=con_method, system=dbsName, username=user_name, password=user_password)
        
        # Crate instnace
        dbc_instance = tdtestpy.DBSaccess (dbc_con)
        
        # Main Body
        logging.info("================== Test Start ==================")
       
        logging.info("Drop user")
        dbc_instance.drop_user("python_unit_test")
        
        logging.info("Create user")
        if not run_sql_file (dbc_con, create_user_queries, test_ignore_errors):
            logging.error ("Test Failed")
            exit(1)
        
        
        with udaExec.connect(method=con_method, system=dbsName, username="python_unit_test", password="python_unit_test") as test_con:
            with test_con.cursor() as cursor:
                sql1 = "SELECT * from test1 where c1 < 3"
                sql1_results = []
                cursor.execute (sql1)
                for row in cursor:
                    #sql1row = (str(row[0]) + ", " + str(row[1]) + ", " + row[2])
                    #sql1row = (str(row["c1"]) + ", " + str(row["c2"]) + ", " + row["c3"])
                    #sql1row = (str(row.c1) + ", " + str(row.c2) + ", " + row.c3)
                    sql1row = (", ".join([str(col) for col in row]))
                    sql1_results.append(sql1row) 
        
                print (sql1_results)
                
                sql2 = "SELECT * from test2 where c3 <> 'a'"
                sql2_results = []
                cursor.execute (sql2)
                for row in cursor:
                    sql2row = (", ".join([str(col) for col in row]))
                    sql2_results.append(sql2row) 
                print (sql2_results)
                
                sql3 = "select t1.c1, t1.c2, t1.c3 from test1 t1, test2 t2 where t1.c1 = t2.c1"
                sql3_results = []
                cursor.execute (sql3)
                for row in cursor:
                    sql3row = (", ".join([str(col) for col in row]))
                    sql3_results.append(sql3row) 
                print (sql3_results)
                
                allresults = {}
                allresults["sql1"] = sql1_results
                allresults["sql2"] = sql2_results
                allresults["sql3"] = sql3_results
                print (allresults)
                
                controlfile = os.path.join(test_path, "controlfile.pickle")
                
                
                with open (controlfile, mode='wb') as f:
                    pickle.dump(allresults, f)
                
                
                with open (controlfile, mode='rb') as f:
                    allresults1 = pickle.load(f)
                
                print (allresults1)
                
                expected_sql1_result = sorted(allresults1["sql1"])
                expected_sql2_result = sorted(allresults1["sql2"])
                expected_sql3_result = sorted(allresults1["sql3"])
                
                print (expected_sql1_result)
                print (expected_sql2_result)
                print (expected_sql3_result)
                
                result1 = sorted(sql1_results)
                result2 = sorted(expected_sql1_result)
                
                for rowA, rowB in zip(result1, result2):
                    if rowA != rowB:
                        logging.error ("Row found mismatch")
                        print ("Row from Actual Results %s" % (rowA))
                        print ("Row from Expected Results %s" % (rowB))
                
                for r in zip(result1, result2):
                    print (r)
    
             
        
        with udaExec.connect(method=con_method, system="hela", username="dbc", password="dbc") as dbc_con:
            with dbc_con.cursor() as cursor:
                sql_results = {}
                cursor.execute ("select TableName, TableKind from DBC.Tables where DatabaseName = 'sit_ldi_pll_user1'")
                for row in cursor:
                    sql_results[row[0].strip()] = row[1]
                all_tables = []
                all_views = []
                all_indexes = []
                all_unknown = []
                for k, v in sql_results.items():
                    if v.lower() == 't':
                        all_tables.append(k)
                    elif v.lower() == 'v':
                        all_views.append(k)
                    elif v.lower() == 'i':
                        all_indexes.append(k)
                    else:
                        all_unknown.append(k)
                        
                print (all_tables)
                print (all_views)
                print (all_indexes)
                print (all_unknown)        
                        
        """
        
        
        """
        file = "results_full.txt"
        
        
        with udaExec.connect(method=con_method, system=dbsName, username="python_test", password="python_test") as test_con:
        
            get_results = tdtestpy.GetSQLResults (db_con = test_con, output_file = file, delimiter = ',', data_only = 'n', retlimit = 0)
            
            sql1 = "SELECT * from test1 where c1 < 3"
            sql2 = "select t1.c1, t1.c2, t1.c3 from test1 t1, test2 t2 where t1.c1 = t2.c1"
            sql3 = "select * from dbc.dbcinfo"
            sql4 = "select * from dbc.dbcinfo where InfoKey = '123'"
            sql5 = "select * from dbc.dbcin"
            
            get_results.dump_to_file(sql1)
            get_results.dump_to_file(sql2)
            get_results.dump_to_file(sql3)
            get_results.dump_to_file(sql4)
            get_results.dump_to_file(sql5)
            
        
        
        file = "results_sql.txt"
        with udaExec.connect(method=con_method, system=dbsName, username="python_test", password="python_test") as test_con:
            with test_con.cursor() as cursor:
                sql = "select * from dbc.dbcinfo"
                start_time = time.time()
                cursor.execute (sql)
                elapsed_time = time.time() - start_time
                # cursor.description (contains columns info) is a special attribute of cursor after execute().
                columns_description = cursor.description
                results = cursor.fetchall()
                row = cursor.rowcount
                col = len(columns_description)
                with open(file, 'a') as f:
                    f.write(sql + "\n")
                    f.write(" *** Query completed. %s rows found. %s columns returned.\n" % (row, col))
                    f.write(" *** Total elapsed time was %.3f seconds.\n" % (elapsed_time,))
                    f.write("--------------------------------------------------------------------------------\n")
                    f.write("| ".join([i[0] for i in columns_description]) + "\n")  # column header, e.g: C1 | C2 | C3
                    for row in results:
                        f.write(", ".join([str(c) for c in row]) + "\n")  # every record of table, e.g: f1, f2, f3
                    f.write("\n\n\n")
                  
                sql1 = "SELECT * from test1 where c1 < 3"
                delimiters = '; '
                start_time = time.time()
                cursor.execute (sql1)
                elapsed_time = time.time() - start_time
                # cursor.description (contains columns info) is a special attribute of cursor after execute().
                columns_description = cursor.description
                results = cursor.fetchall()
                #row = len(results)
                row = cursor.rowcount
                col = len(results[0])
                col = len(columns_description)
                with open(file, 'a') as f:
                    f.write(sql1 + "\n")
                    f.write(" *** Query completed. %s rows found. %s columns returned.\n" % (row, col))
                    f.write(" *** Total elapsed time was %.3f seconds.\n" % (elapsed_time,))
                    f.write("--------------------------------------------------------------------------------\n")
                    f.write("| ".join([i[0] for i in columns_description]) + "\n")  # column header, e.g: C1 | C2 | C3
                    for row in results:
                        f.write(delimiters.join([str(c) for c in row]) + "\n")  # every record of table, e.g: f1, f2, f3
                    f.write("\n\n\n")
                    
                    
                sql2 = "select * from dbc.dbcinfo"
                
                start_time = time.time()
                cursor.execute (sql2)
                elapsed_time = time.time() - start_time
                # cursor.description (contains columns info) is a special attribute of cursor after execute().
                columns_description = cursor.description
                results = cursor.fetchall()
                #row = len(results)
                row = cursor.rowcount
                col = len(results[0])
                col = len(columns_description)
                with open(file, 'a') as f:
                    f.write(sql2 + "\n")
                    f.write(" *** Query completed. %s rows found. %s columns returned.\n" % (row, col))
                    f.write(" *** Total elapsed time was %.3f seconds.\n" % (elapsed_time,))
                    f.write("--------------------------------------------------------------------------------\n")
                    f.write("| ".join([i[0] for i in columns_description]) + "\n")  # column header, e.g: C1 | C2 | C3
                    for row in results:
                        f.write(", ".join([str(c) for c in row]) + "\n")  # every record of table, e.g: f1, f2, f3
                    f.write("\n\n\n")
                    
                sql3 = "select t1.c1, t1.c2, t1.c3 from test1 t1, test2 t2 where t1.c1 = t2.c1"
                
                start_time = time.time()
                cursor.execute (sql3)
                elapsed_time = time.time() - start_time
                # cursor.description (contains columns info) is a special attribute of cursor after execute().
                columns_description = cursor.description
                results = cursor.fetchall()
                #row = len(results)
                row = cursor.rowcount
                col = len(results[0])
                col = len(columns_description)
                with open(file, 'a') as f:
                    f.write(sql3 + "\n")
                    f.write(" *** Query completed. %s rows found. %s columns returned.\n" % (row, col))
                    f.write(" *** Total elapsed time was %.3f seconds.\n" % (elapsed_time,))
                    f.write("--------------------------------------------------------------------------------\n")
                    f.write("| ".join([i[0] for i in columns_description]) + "\n")  # column header, e.g: C1 | C2 | C3
                    for row in results:
                        f.write(", ".join([str(c) for c in row]) + "\n")  # every record of table, e.g: f1, f2, f3
                    f.write("\n\n\n")
            """                    
    except Exception as e:
        logging.error(traceback.format_exc())
        exit(1)
        
    exit(0)
