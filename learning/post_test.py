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

udaExec = teradata.UdaExec (appName="UDA-Python", version="1.0", logConsole=False)

repository_database = "hela"
repository_user = "dbc"
repository_pass = "dbc"
test_name = "Jmeter Python"
test_id = 55555

agent_name = socket.gethostname()
src = os.path.dirname(os.path.realpath(__file__))
os_user_name = getpass.getuser()
get_uuid = uuid.uuid4()
os_type = platform.system()
main_output_repository = '/common/SIT/test_output' if os_type == "Linux" else 'C:\Temp\\test_output'

# get run_id from repository_db.test_status
def get_run_id():
   with udaExec.connect(method="odbc", system=repository_database, username=repository_user, password=repository_pass) as session:
    with session.cursor() as cursor:
     cursor.execute("select max(run_id) from repository_db.test_status where test_id = %s and database_name = '%s' and run_by = '%s'" % (test_id, database_name, os_user_name))
     res = cursor.fetchone()
   return res[0]

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

def end_test_tracking(run_id):
    session = udaExec.connect(method="odbc", system=repository_database, username=repository_user, password=repository_pass)
    cursor = session.cursor()
    sql = "select count (*) from repository_db.book_keeping where run_id = ? and task_status =  'failed' and task_start_time >= (select max(test_start_time) from repository_db.test_status where run_id = ?)"
    cursor.execute(sql, (run_id, run_id,))
    if cursor.fetchone()[0] == 0:
      cursor.execute("UPDATE repository_db.test_status SET test_end_time = current_timestamp, test_status = 'passed' where run_id = %s" % (run_id))
    else:
      cursor.execute("UPDATE repository_db.test_status SET test_end_time = current_timestamp, test_status = 'failed' where run_id = %s" % (run_id))
      logging.info("Test completed but some tasks failed, please check the output")
      exit(1)

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
        run_id = get_run_id()
        uuid_id = str(get_uuid)
        uda_python_log = database_name + "_" + user_name + "_" + uuid_id + "_python_pretest_log.txt"
        uda_python_output = os.path.join(main_output_repository, 'jmeter_python', database_name, 'post_test')
        main_python_output = os.path.join(uda_python_output, uda_python_log)
        fh = logging.FileHandler(main_python_output, mode="a", encoding="utf8")
        fh.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
        fh.setLevel(logging.DEBUG)
        root = logging.getLogger()
        root.addHandler(fh)

try:

  # Start tracking UDA Python
  logging.info("Start post-test")
  end_test_tracking(run_id)
except teradata.DatabaseError:
  exit(1)
  raise
else:
  exit(0)

