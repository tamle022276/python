import subprocess
import sys
import re
import logging
import traceback
import argparse
import getpass
import platform
import teradata
import os
import socket
import paramiko
import time

python_src = os.path.dirname(os.path.realpath(__file__))
os_user_name = getpass.getuser()
os_type = platform.system()
if os_type == "Windows":
    sys.path.append('C:\\Users\\TL151006\\Desktop\\dev\\trunk\\common')
if os_type == "Linux":
    sys.path.append('/qd0056/tl151006/jmeter-svn/common')
if os_user_name == "tomcat":
    sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "common"))
import uda2c


def setup_argparse():
    parser = argparse.ArgumentParser(description="### datacheck.py ###")
    parser.add_argument("--dbsName", required=True, help="System name")
    parser.add_argument("--root_password", required=False, default='Sit4me123!', help="root password")
    parser.add_argument("--dbc_password", required=False, default='dbc', help="dbc password")
    parser.add_argument("--runScandisk", choices=('y', 'n'), required=False, default='n', help="runScandisk must be y or n")
    parser.add_argument("--runCheckTable", choices=('y', 'n'), required=False, default='n', help="CheckTable must be y or n")
    parser.add_argument("--CheckDatabaseName", required=False, help="Name of the database to check")
    parser.add_argument("--CheckTableName", required=False, help="Name of the table to check")
    parser.add_argument("--CheckLevel", choices=('one', 'two', 'three', 'pendingop'), required=False, default='two', help="Checktable level")

    return parser.parse_args()


# Python exit wrapper function
def exit(ok=True):
    if ok is True or ok == 0:
        logging.info("================= End: Data Check Success!] =================")
        sys.exit(0)
    else:
        logging.info("================== End: Data Check Failed!] ==================")
        sys.exit(1)


if __name__ == "__main__":

    try:
        udaExec = teradata.UdaExec (appName="DataCheck", version="1.0", logConsole=True)
        args = setup_argparse()
        dbsName = args.dbsName
        root_password = args.root_password
        dbc_password = args.dbc_password
        runScandisk = args.runScandisk
        runCheckTable = args.runCheckTable
        CheckDatabaseName = args.CheckDatabaseName
        CheckTableName = args.CheckTableName
        CheckLevel = args.CheckLevel
        checktable_log = dbsName + "-checktable-" + time.strftime("%Y-%m-%d-%H-%M") + ".log"
        scandisk_log = dbsName + "-scandisk-" + time.strftime("%Y-%m-%d-%H-%M") + ".log"
        db_conn = udaExec.connect(method="odbc", system=dbsName, username= "dbc", password=dbc_password)

        # dump python log to demo_log_path        
        fh = logging.FileHandler("data_check.log", mode="a", encoding="utf8")
        fh.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
        fh.setLevel(logging.DEBUG)
        root = logging.getLogger()
        root.addHandler(fh) 
       
        if runCheckTable == 'y':
            if uda2c.checktable (dbsName, root_password, CheckDatabaseName, CheckTableName, CheckLevel, checktable_log):
                logging.info("Checktable completed successfully, log file: %s" % (checktable_log))
            else:
                logging.info("Checktable completed with failure, log file: %s" % (checktable_log))
                exit(1)

        if runScandisk == 'y':
            if uda2c.scandisk (dbsName, root_password, db_conn, scandisk_log):
                logging.info("Scandisk completed successfully, log file: %s" % (scandisk_log))
            else:
                logging.info("Scandisk completed with failure, log file: %s" % (scandisk_log))
                exit(1)

    except Exception as e:
        logging.error(traceback.format_exc())
        exit(1)
        
    exit(0)
