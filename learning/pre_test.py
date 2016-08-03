#Sample: python pre_test.py --database_name=hela --user_name=dbc --user_password=dbc

import sys
import os
import shutil
import time
import re
import argparse
import teradata
import errno
import subprocess
import traceback
import logging
import socket
import zipfile
import uuid
import getpass
import platform

# Test variables
udaExec = teradata.UdaExec (appName="Jmeter-Python", version="1.0", logConsole=True)

os_type = platform.system()
# main_output_repository = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', '..', 'test_output'))
main_output_repository = '/common/SIT/test_output' if os_type == "Linux" else 'C:\Temp\\test_output'
os_user_name = getpass.getuser()
agent_name = socket.gethostname()
get_uuid = uuid.uuid4()
python_src = os.path.dirname(os.path.realpath(__file__))

repository_database = "hela"
repository_user = "dbc"
repository_pass = "dbc"
test_name = "Jmeter Python"
test_output_directory = "jmeter_python"

test_id = 55555

# create directory if not exists
def ensure_dir(dirname):
    try:
        os.makedirs(dirname)
    except OSError as e:
        if e.errno == errno.EEXIST:
            return
        raise e

# Create logs output directory
def setup_log_dir():
    ensure_dir(os.path.join(main_output_repository, test_output_directory, database_name, "pre_test"))
    ensure_dir(os.path.join(main_output_repository, test_output_directory, database_name, "post_test"))
    ensure_dir(os.path.join(main_output_repository, test_output_directory, database_name, "test", "bteq", "pass"))
    ensure_dir(os.path.join(main_output_repository, test_output_directory, database_name, "test", "uda", "pass"))
    ensure_dir(os.path.join(main_output_repository, test_output_directory, database_name, "test", "tpt", "pass"))
    ensure_dir(os.path.join(main_output_repository, test_output_directory, database_name, "test", "bteq", "fail"))
    ensure_dir(os.path.join(main_output_repository, test_output_directory, database_name, "test", "uda", "fail"))
    ensure_dir(os.path.join(main_output_repository, test_output_directory, database_name, "test", "tpt", "fail"))
    ensure_dir(os.path.join(main_output_repository, test_output_directory, database_name, "test", "tpt", "data_file"))
    ensure_dir(os.path.join(main_output_repository, test_output_directory, database_name, "test", "all_fail"))
    
# Delete all output in a directory
def delete_all_files_in_directory(what_path):
    for the_file in os.listdir(what_path):
     file_path = os.path.join(what_path, the_file)
     try:
        if os.path.isfile(file_path):
            os.unlink(file_path)
        #If you also want to remove subdirectories, uncomment the elif statement. 
        #elif os.path.isdir(file_path): shutil.rmtree(file_path) 
     except OSError as e:
        raise e
        
# Delete all files with extension
def delete_all_files_with_extension(path_of_logs, end_with_what):
     try:
        filelist = [ f for f in os.listdir(path_of_logs) if f.endswith(end_with_what) ]
        for f in filelist:
            os.remove(f)
     except OSError as e:
        if e.errno != errno.ENOENT:
            raise
    

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

    parser = argparse.ArgumentParser(description="### bteq.PY ###")
    parser.add_argument("--database_name", required=True, help="System name")
    parser.add_argument("--user_name", required=True, help="User name")
    parser.add_argument("--user_password", required=True, help="User password")
    parser.add_argument("--ignore_error", required=False, default=[],
            help="Error number should be ignored. Must be integers separated by commas.", action=IgnoreErrorAction)

    return parser.parse_args()

# Get DBS Version of test system
def get_dbs_release():
   with udaExec.connect(method="odbc", system=database_name, username=user_name, password=user_password) as session:
    with session.cursor() as cursor:
     cursor.execute("select InfoData from dbc.dbcinfo where InfoKey = 'RELEASE'")
     res = cursor.fetchone()
   return res[0]

# Get PDE Release of test system
def get_pde_version():
   with udaExec.connect(method="odbc", system=database_name, username=user_name, password=user_password) as session:
    with session.cursor() as cursor:
     cursor.execute("select InfoData from dbc.dbcinfo where InfoKey = 'VERSION'")
     res = cursor.fetchone()
   return res[0]

# Start logging into for tracking
def start_test_tracking(test_id, test_name, database_name, agent_name, dbs_release, pde_version, run_by):

    session = udaExec.connect(method="odbc", system=repository_database, username=repository_user, password=repository_pass);

    sql = "insert into repository_db.test_status(run_id, test_id, test_name, database_name, agent_name, dbs_release, pde_version, test_start_time, test_status, run_by) \
        values ((SELECT (COALESCE(MAX(run_id), 0) + 1) FROM repository_db.test_status), ?, ?, ?, ?, ?, ?, current_timestamp, 'inprogress', ?)"

    session.execute(sql, (test_id, test_name, database_name, agent_name, dbs_release, pde_version, run_by))

    session.close()

# Python exit wrapper function
def exit(ok=True):
    if ok is True or ok == 0:
        logging.info("================= End: [Pretest Completed: Pass!] =================")
        sys.exit(0)
    else:
        logging.info("================== End: [Pretest Completed: Failed!] ==================")
        sys.exit(1)

if __name__ == "__main__":
        args = setup_argparse()
        database_name = args.database_name
        user_name = args.user_name
        user_password = args.user_password
        dbs_release = get_dbs_release()
        pde_version = get_pde_version()
        uuid_id = str(get_uuid)
        what_path = os.path.join(main_output_repository, test_output_directory, database_name, "test", "all_fail")

        # Setup output directory
        setup_log_dir()
        
        # delete log that use by jenkins for scanning errors
        delete_all_files_in_directory(what_path)
        delete_all_files_with_extension(python_src, ".log")

        uda_python_log = database_name + "_" + user_name + "_" + uuid_id + "_python_pretest_log.txt"
        uda_python_output = os.path.join(main_output_repository, test_output_directory, database_name, "pre_test")
        main_python_output = os.path.join(uda_python_output, uda_python_log)
        fh = logging.FileHandler(main_python_output, mode="a", encoding="utf8")
        fh.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
        fh.setLevel(logging.DEBUG)
        root = logging.getLogger()
        root.addHandler(fh)

try:

  # Start tracking UDA Python
  logging.info("Start test tracking UDA Python")
  start_test_tracking(test_id, test_name, database_name, agent_name, dbs_release, pde_version, os_user_name)
except teradata.DatabaseError:
  exit(1)
  raise
else:
  exit(0)
