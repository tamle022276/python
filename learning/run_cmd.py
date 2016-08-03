import subprocess
import sys
import logging
import traceback
import argparse
import getpass
import platform
import teradata
import os
import socket
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


def datacheck (hostname, command, output):
    try:
        ssh = subprocess.Popen(["ssh", "-o", "BatchMode=yes", "%s" % hostname, command], shell=False, stdout = open(output, 'w'))
        ssh.wait()
    except Exception as e:
        logging.error(traceback.format_exc())

    if ssh.returncode == 0:
        return True
    else:
        return False


def get_ip_address (dbsName):
    if 'cop1' in dbsName:
        response = os.system("ping -c 1 " + dbsName)
        if response == 0:
            ip_address = socket.gethostbyname(dbsName)
            return ip_address
        else:
            logging.error ("your dbsName: %s is not pingable" % (dbsName))
            exit (1)
    # Any Ip address always has 3 periods
    elif dbsName.count('.') == 3:
        fields = dbsName.replace(".","")
        # Checks if every field is composed by numbers
        if fields.isdigit():
            ip_address = dbsName
            return ip_address
        else:
            logging.error ("your ip address: %s is invalid" % (dbsName))
            exit(1)
    else:
        nodename = dbsName + "cop1"
        ip_address = socket.gethostbyname(nodename)
        return ip_address



# Check and validate input parameters
def setup_argparse():
    parser = argparse.ArgumentParser(description="### datacheck.py ###")
    parser.add_argument("--dbsName", required=True, help="System name")
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
        runScandisk = args.runScandisk
        runCheckTable = args.runCheckTable
        CheckDatabaseName = args.CheckDatabaseName
        CheckTableName = args.CheckTableName
        CheckLevel = args.CheckLevel

        # dump python log to demo_log_path        
        fh = logging.FileHandler("data_check.log", mode="a", encoding="utf8")
        fh.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
        fh.setLevel(logging.DEBUG)
        root = logging.getLogger()
        root.addHandler(fh) 
                
        # Using uda2c DBS functions to test Hela and Monopoly
        logging.info("================== DBS Function Testing ==================")
        #with udaExec.connect(method="odbc", system=dbsName, username= "dbc", password= "dbc") as db_conn:
        #    num_vprocs = uda2c.get_num_vprocs(db_conn)
        scanpass = "vproc responded with no messages or errors"
        #scanpass = str(num_vprocs) + " of " + str(num_vprocs) + " vprocs responded with no messages or errors"
        print (scanpass)
        checkpass = "0 table(s) failed the check"
 
        #nodename = dbsName + "cop1"
        #ipadr = socket.gethostbyname(nodename)
        ipadr = get_ip_address (dbsName)
        hostname = "rot@" + str(ipadr)
        print (hostname)

        output_log = "scan1.txt"
        logging.info ("scandisk started")

        if runScandisk == 'y':
            command = '/usr/pde/bin/cnsrun -utility filer -commands "{enable script} {scandisk} {yes} {quit} " -debug 3 -force'
            if datacheck (hostname, command, output_log):
                if not uda2c.scan_a_file(output_log, scanpass):
                    logging.info("Scandisk completed successfully")
                else:
                    logging.error("Scandisk failed, please checkout log file here: %s" % (output_log))
                    exit(1)
            else:
                logging.error("something not right, check this log %s, if it's empty then check authentication keys" % (output_log))
                exit(1)

    except Exception as e:
        logging.error(traceback.format_exc())
        exit(1)
        
    exit(0)
