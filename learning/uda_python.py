#ignore_error can be many, it separate by comma and it is optional
#Sample run 1 with ignore error: python uda_python.py --database_name=hela --user_name=dbc --user_password=dbc --ignore_error=3822,3807
#Sample run 2 without ignore error: python uda_python.py --database_name=hela --user_name=dbc --user_password=dbc

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

# Define variables
udaExec = teradata.UdaExec (appName="UDA_Python", version="1.0", logConsole=True)
os_user_name = getpass.getuser()
get_uuid = uuid.uuid4()
agent_name = socket.gethostname()
os_type = platform.system()
main_output_repository = '/common/SIT/test_output' if os_type == "Linux" else 'C:\Temp\\test_output'

repository_database = "hela"
repository_user = "dbc"
repository_pass = "dbc"
test_id = 55555
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

    parser = argparse.ArgumentParser(description="### bteq.PY ###")
    parser.add_argument("--database_name", required=True, help="System name")
    parser.add_argument("--user_name", required=True, help="User name")
    parser.add_argument("--user_password", required=True, help="User password")
    parser.add_argument("--ignore_error", required=False, default=[],
            help="Error number should be ignored. Must be integers separated by commas.", action=IgnoreErrorAction)

    return parser.parse_args()

# get run_id from repository_db.test_status
def get_run_id():
   with udaExec.connect(method="odbc", system=repository_database, username=repository_user, password=repository_pass) as session:
    with session.cursor() as cursor:
     cursor.execute("select max(run_id) from repository_db.test_status where test_id = %s and database_name = '%s' and run_by = '%s'" % (test_id, database_name, os_user_name))
     res = cursor.fetchone()
   return res[0]

# Start logging into for tracking
def start_tracking(task_name, logs_file):

    session = udaExec.connect(method="odbc", system=repository_database, username=repository_user, password=repository_pass);

    sql = "insert into repository_db.book_keeping (run_id, uuid_id, task_name, task_start_time, task_status, log_file) \
        values (?, ?, ?, current_timestamp, 'inprogress', ?)"

    session.execute(sql, (run_id, uuid_id, task_name, logs_file))

    session.close()

# Run sql file and standalone queries
def run_sql(): 
   session = udaExec.connect(method="odbc", system=database_name, username=user_name, password=user_password, queryBands=additional_query_bands);
      
   for row in  session.execute("SELECT GetQueryBand()"):
     print(row)

   session.execute(file="uda_queries.txt", ignoreErrors=udaexe_ignore_errors)
   session.execute("select * from dbc.dbcinf", ignoreErrors=udaexe_ignore_errors)
   session.execute("select current_timestam", ignoreErrors=udaexe_ignore_errors)

# Update book keeping with status
def end_tracking(uuid_id, success=True):
    session = udaExec.connect(method="odbc", system=repository_database, username=repository_user, password=repository_pass)

    sql = "UPDATE repository_db.book_keeping SET task_end_time = current_timestamp, task_status = ?, task_comments = ?, log_file = ? \
            WHERE task_start_time = (select max(task_start_time) from repository_db.book_keeping where uuid_id = ?) and uuid_id = ?"

    if success:
        session.execute(sql, ('passed', task_comments, log_file, uuid_id, uuid_id, ))
    else:
        session.execute(sql, ('failed', task_comments, log_file, uuid_id, uuid_id, ))

    session.close()


def copy_file(src, dest, filename):
   shutil.copy(os.path.join(src, filename), os.path.join(dest, filename))

# Python exit wrapper function
def exit(ok=True):
    if ok is True or ok == 0:
        logging.info("================= End: [UDA Python Run Sucess] =================")
        sys.exit(0)
    else:
        logging.info("================== End: [UDA Python Run Fail] ==================")
        sys.exit(1)

if __name__ == "__main__":
        # Get variables
        args = setup_argparse()
        database_name = args.database_name
        user_name = args.user_name
        user_password = args.user_password
        ignore_error = args.ignore_error
        udaexe_ignore_errors = get_common_errors() + ignore_error
        ignore_error_set = str(tuple(udaexe_ignore_errors))
        uuid_id = str(get_uuid)
        run_id = get_run_id()
        # Setting up python log
        main_test_output_directory = os.path.join(main_output_repository, 'jmeter_python', database_name, 'test')
        uda_python_log = database_name + "_" + user_name + "_" + uuid_id + "_uda_python_log.txt"
        uda_python_output = os.path.join(main_test_output_directory, "uda")
        main_python_output = os.path.join(uda_python_output, uda_python_log)
        fh = logging.FileHandler(main_python_output, mode="a", encoding="utf8")
        fh.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
        fh.setLevel(logging.DEBUG)
        root = logging.getLogger()
        root.addHandler(fh)
        # Add additional querybands new
        additional_query_bands = {'run_by': os_user_name, 'database_name': database_name, 'python_unique_id': uuid_id}

try:
  logging.info(" UDA Python test variables:")
  logging.info(" * Database Name: %s", database_name)
  logging.info(" * User name: %s", user_name)
  logging.info(" * User Password: %s", user_password)
  logging.info(" * Ignore errors: %s", udaexe_ignore_errors)
  logging.info(" * Python run ID: %s", uuid_id)
  logging.info(" * Python log name: %s", uda_python_log)

  # Start tracking UDA Python
  logging.info("Start tracking UDA Python")
  start_tracking('uda', main_python_output)
  # Run UDA Python
  run_sql()
except teradata.DatabaseError as e:
  task_comments = "Ignore error " + ignore_error_set + " but found error: " + str(e.args[0])
  log_file = os.path.join(uda_python_output, "fail", uda_python_log)
  end_tracking(uuid_id, False)
  logging.error("UDA failed because of this error %d. Please check out this log file: %s" % ((e.args[0]), log_file))
  output_dest = os.path.join(uda_python_output, "fail")
  jenkins_dest = os.path.join(main_output_repository, 'jmeter_python', database_name, 'test', 'all_fail')
  copy_file(uda_python_output, output_dest, uda_python_log)
  copy_file(uda_python_output, jenkins_dest, uda_python_log)
  exit(1)
  raise
else:
  task_comments = "Either there is no error or error found is in ignore list"
  log_file = os.path.join(uda_python_output, "pass", uda_python_log)
  end_tracking(uuid_id, True)
  output_dest = os.path.join(uda_python_output, "pass")
  copy_file(uda_python_output, output_dest, uda_python_log)

exit(0)
