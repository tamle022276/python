#ignore_error can be many, it separate by comma and it is optional
#Sample run 1 with ignore error: python bteq.py --database_name=hela --user_name=dbc --user_password=dbc --ignore_error=3822,3807
#Sample run 2 without ignore error: python bteq.py --database_name=hela --user_name=dbc --user_password=dbc
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

udaExec = teradata.UdaExec (appName="Bteq Python", version="1.0", logConsole=True)

######################################
REPOSITORY_DATABASE = "hela"
REPOSITORY_USER = "dbc"
REPOSITORY_PASS = "dbc"
TEST_NAME = "Bteq Python"
TEST_ID = 33333
TEST_DIR = "bteq_output"
COMMON_ERROR = "2631" #Transaction ABORTed due to deadlock

BTEQ_FILE="bteq_queries.txt"

AGENT_NAME = socket.gethostname()
get_uuid = uuid.uuid4()
src = os.path.dirname(os.path.realpath(__file__))

# create directory if not exists
def ensure_dir(dirname):
    try:
        os.makedirs(dirname)
    except OSError as e:
        if e.errno == errno.EEXIST:
            return
        raise e

# Output name
def setup_log_dir():
    ensure_dir(os.path.join(src, TEST_DIR))
    ensure_dir(os.path.join(src, TEST_DIR, database_name))
    ensure_dir(os.path.join(src, TEST_DIR, database_name, "pass"))
    ensure_dir(os.path.join(src, TEST_DIR, database_name, "fail"))

# parse COMMON_ERROR
def get_common_errors():
    return [int(e.strip()) for e in COMMON_ERROR.split(",") if e.strip()]

# Execute the bteq command using subprocess
def bteq_select(bteq_in, bteq_logfile, database_name, user_name, user_password):
    subprocess.call(["bteq", ".logon", "{}/{},{}".format(database_name, user_name, user_password)], stdin=open(bteq_in), stdout=open(bteq_logfile, 'w'), stderr=subprocess.STDOUT)

# Parse out error numbers from error log file.
def parse_error_nums(logfile):
    errors = []

    with open(logfile, 'r') as f:
        for line in f.readlines():
            m = re.search(r"\*\*\* Failure (\d+)", line)
            if m:
                errors.append(int(m.group(1)))
    return errors

# Dump errors to log
def bteq_log_error_codes(error_codes, error_log):
    with open(error_log, 'w') as f:
        f.writelines([str(code) + "\n" for code in error_codes])

# Check if all errors in log file are ignored errors.
def bteq_has_critical_error(errors, bteq_ignore_errors):
    error_set = set(errors)
    ignore_set = set(bteq_ignore_errors)

    return not error_set.issubset(ignore_set)

# Get DBS Release of target system
def get_dbs_release():
   with udaExec.connect(method="odbc", system=database_name, username=user_name, password=user_password) as session:
    with session.cursor() as cursor:
     cursor.execute("select InfoData from dbc.dbcinfo where InfoKey = 'RELEASE'")
     res = cursor.fetchone()
   return res[0]

# Get PDE Release of target system
def get_pde_version():
   with udaExec.connect(method="odbc", system=database_name, username=user_name, password=user_password) as session:
    with session.cursor() as cursor:
     cursor.execute("select InfoData from dbc.dbcinfo where InfoKey = 'VERSION'")
     res = cursor.fetchone()
   return res[0]


# Start logging into for tracking
def start_tracking(task_name):

    session = udaExec.connect(method="odbc", system=REPOSITORY_DATABASE, username=REPOSITORY_USER, password=REPOSITORY_PASS);

    sql = "insert into repository_db.book_keeping (test_id, test_name, database_name, agent_name, user_name, dbs_release, pde_version, task_name, test_start_time, test_status, run_id) \
        values (?, ?, ?, ?, ?, ?, ?, ?, current_timestamp, 'inprogress', ?)"

    session.execute(sql, (TEST_ID, TEST_NAME, database_name, AGENT_NAME, user_name, dbs_release, pde_version, task_name, run_id))

    session.close()

# Update book keeping with status
def end_tracking(database_name, user_name, user_password, task_name, success=True):
    session = udaExec.connect(method="odbc", system=REPOSITORY_DATABASE, username=REPOSITORY_USER, password=REPOSITORY_PASS)

    sql = "UPDATE repository_db.book_keeping SET test_end_time = current_timestamp, test_status = ? \
            WHERE test_start_time = (select max(test_start_time) from repository_db.book_keeping where test_id = ? and test_name = ? and database_name = ? and user_name = ? and task_name = ? and run_id = ?) and test_name = ? and database_name = ? and user_name = ? and task_name = ? and run_id = ?"

    if success:
        session.execute(sql, ('passed', TEST_ID, TEST_NAME, database_name, user_name, task_name, run_id, TEST_NAME, database_name, user_name, task_name, run_id, ))
    else:
        session.execute(sql, ('failed', TEST_ID, TEST_NAME, database_name, user_name, task_name, run_id, TEST_NAME, database_name, user_name, task_name, run_id, ))

    session.close()

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

# Move log file to correct path
def move_file(src, dest, filename):
   shutil.move(os.path.join(src, filename), os.path.join(dest, filename))

# Python exit wrapper function
def exit(ok=True):
    if ok is True or ok == 0:
        logging.info("================= End: [Bteq Run Sucess: Let Go Have A Beer!] =================")
        sys.exit(0)
    else:
        logging.info("================== End: [Bteq Run Fail: This is why Bob says Python sucks!] ==================")
        sys.exit(1)

if __name__ == "__main__":


    try:
        args = setup_argparse()

        database_name = args.database_name
        user_name = args.user_name
        user_password = args.user_password
        ignore_error = args.ignore_error
        run_id = str(get_uuid)
        dbs_release = get_dbs_release()
        pde_version = get_pde_version()

        # Setup output directory
        setup_log_dir()

        # dump python log file to choosing directory for easy access
        bteq_python_log = database_name + "_" + user_name + "_" + str(get_uuid) + "_python_log.txt"
        bteq_python_output = os.path.join(src, TEST_DIR, database_name)
        main_bteq_python_output = os.path.join(bteq_python_output, bteq_python_log)
        fh = logging.FileHandler(main_bteq_python_output, mode="a", encoding="utf8")
        fh.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
        fh.setLevel(logging.DEBUG)
        root = logging.getLogger()
        root.addHandler(fh) 

        BTEQ_ERROR_CODES_LOG = database_name + "_" + user_name + "_" + str(get_uuid) + "_bteq_test_error.txt"
        BTEQ_IGNORE_ERRORS_LOG = database_name + "_" + user_name + "_" + str(get_uuid) + "_bteq_ignore_error.txt"

        BTEQ_QUERY_BAND = "DatabaseName=" + database_name + ";Version=" + pde_version + ";python_unique_id=" + run_id +";"

        logging.info("User Input Variables:")
        logging.info(" * Database Name: %s", database_name)
        logging.info(" * User name: %s", user_name)
        logging.info(" * User Password: %s", user_password)
        logging.info(" * Ignore errors: %s", ignore_error)
        logging.info(" * Bteq error codes log: %s", BTEQ_ERROR_CODES_LOG)
        logging.info(" * Bteq ignore error codes log: %s", BTEQ_IGNORE_ERRORS_LOG)
        logging.info(" * Bteq Query band is: %s", BTEQ_QUERY_BAND)


        # Create bteq log
        bteq_logfile_name = database_name + "_" + user_name + "_" + str(get_uuid) + "_bteq_output.txt"
        main_bteq_output = os.path.join(bteq_python_output, bteq_logfile_name)

        logging.info("Run bteq command:")
        logging.info(" * bteq input file: %s", BTEQ_FILE)
        logging.info(" * bteq log file: %s", bteq_logfile_name)

        # Start tracking bteq
        start_tracking('bteq_select')
        # Run bteq file
        bteq_select(BTEQ_FILE, main_bteq_output, database_name, user_name, user_password)

        # Check if there are errors that cannot be ignored in fst log file.
        bteq_error_codes_log = os.path.join(bteq_python_output, BTEQ_ERROR_CODES_LOG)
        logging.info("Parse error codes from bteq log file and save it to: %s", bteq_error_codes_log)
        bteq_errors_found = parse_error_nums(main_bteq_output)
        logging.info("Here is the bteq errors found: %s", bteq_errors_found)
        bteq_log_error_codes(bteq_errors_found, bteq_error_codes_log)

        bteq_ignore_codes_log = os.path.join(bteq_python_output, BTEQ_IGNORE_ERRORS_LOG)
        logging.info("All bteq ignore-error (including COMMON_ERROR) save to file: %s", bteq_ignore_codes_log)
        bteq_ignore_errors = get_common_errors() + ignore_error
        logging.info("Here is the bteq ignore errors: %s", bteq_ignore_errors)
        bteq_log_error_codes(bteq_ignore_errors, bteq_ignore_codes_log)

        if bteq_has_critical_error(bteq_errors_found, bteq_ignore_errors):
            logging.error("Bteq log file have some errors cannot be ignored. Please check bteq log file: %s" % (main_bteq_output, ))
            end_tracking(database_name, user_name, user_password, 'bteq_select', False)
            output_dest = os.path.join(bteq_python_output, "fail")
            move_file(bteq_python_output, output_dest, bteq_logfile_name)
            move_file(bteq_python_output, output_dest, BTEQ_ERROR_CODES_LOG)
            move_file(bteq_python_output, output_dest, BTEQ_IGNORE_ERRORS_LOG)
            exit(1)
        else:
            end_tracking(database_name, user_name, user_password, 'bteq_select', True)
            output_dest = os.path.join(bteq_python_output, "pass")
            move_file(bteq_python_output, output_dest, bteq_logfile_name)
            move_file(bteq_python_output, output_dest, BTEQ_ERROR_CODES_LOG)
            move_file(bteq_python_output, output_dest, BTEQ_IGNORE_ERRORS_LOG)

    except Exception as e:
        logging.error(traceback.format_exc())
        exit(1)

    exit(0)
