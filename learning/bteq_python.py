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
import getpass
import platform

udaExec = teradata.UdaExec (appName="Jmeter-Python", version="1.0", logConsole=True)


######################################
repository_database = "hela"
repository_user = "dbc"
repository_pass = "dbc"
test_id = 55555
common_error = "2631" #Transaction ABORTed due to deadlock

bteq_file="bteq_queries.txt"
get_uuid = uuid.uuid4()
os_user_name = getpass.getuser()
os_type = platform.system()
main_output_repository = '/common/SIT/test_output' if os_type == "Linux" else 'C:\Temp\\test_output'

# parse common_error
def get_common_errors():
    return [int(e.strip()) for e in common_error.split(",") if e.strip()]

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

# Check if all errors in log file are ignored errors.
def bteq_has_critical_error(errors, bteq_ignore_errors):
    error_set = set(errors)
    ignore_set = set(bteq_ignore_errors)

    return not error_set.issubset(ignore_set)

# Filter out the error that can not be ignore 
def filter_critical_errors(actual_errors, ignore_errors):
    actual_set = set(actual_errors)
    ignore_set = set(ignore_errors)

    return list(actual_set.difference(ignore_set))


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

    parser = argparse.ArgumentParser(description="### bteq_python.py ###")
    parser.add_argument("--database_name", required=True, help="System name")
    parser.add_argument("--user_name", required=True, help="User name")
    parser.add_argument("--user_password", required=True, help="User password")
    parser.add_argument("--ignore_error", required=False, default=[],
            help="Error number should be ignored. Must be integers separated by commas.", action=IgnoreErrorAction)

    return parser.parse_args()

# Copy log file to correct path
def copy_file(src, dest, filename):
   shutil.copy(os.path.join(src, filename), os.path.join(dest, filename))

# Python exit wrapper function
def exit(ok=True):
    if ok is True or ok == 0:
        logging.info("================= End: [Bteq Run Sucess!] =================")
        sys.exit(0)
    else:
        logging.info("================== End: [Bteq Run Fail!] ==================")
        sys.exit(1)

if __name__ == "__main__":


    try:
        args = setup_argparse()

        database_name = args.database_name
        user_name = args.user_name
        user_password = args.user_password
        ignore_error = args.ignore_error
        uuid_id = str(get_uuid)
        run_id = get_run_id()

        # dump python log file to choosing directory for easy access
        bteq_python_log = database_name + "_" + user_name + "_" + str(get_uuid) + "_bteq_python_log.txt"
        bteq_python_output = os.path.join(main_output_repository, 'jmeter_python', database_name, 'test', 'bteq')
        main_bteq_python_output = os.path.join(bteq_python_output, bteq_python_log)
        fh = logging.FileHandler(main_bteq_python_output, mode="a", encoding="utf8")
        fh.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
        fh.setLevel(logging.DEBUG)
        root = logging.getLogger()
        root.addHandler(fh) 

        #BTEQ_QUERY_BAND = "DatabaseName=" + database_name + ";Version=" + pde_version + ";python_unique_id=" + run_id +";"

        logging.info("User Input Variables:")
        logging.info(" * Database Name: %s", database_name)
        logging.info(" * User name: %s", user_name)
        logging.info(" * User Password: %s", user_password)
        logging.info(" * Bteq Ignore errors: %s", ignore_error)


        # Create bteq log
        bteq_logfile_name = database_name + "_" + user_name + "_" + str(get_uuid) + "_bteq_output.txt"
        main_bteq_output = os.path.join(bteq_python_output, bteq_logfile_name)

        logging.info("Run bteq command:")
        logging.info(" * bteq input file: %s", bteq_file)
        logging.info(" * bteq log file: %s", bteq_logfile_name)

        # Start tracking bteq
        start_tracking('bteq', main_bteq_output)
        # Run bteq file
        bteq_select(bteq_file, main_bteq_output, database_name, user_name, user_password)

        # Check if there are errors that cannot be ignored in fst log file.
        bteq_errors_found = parse_error_nums(main_bteq_output)
        logging.info("Here is the bteq errors found: %s", bteq_errors_found)

        bteq_ignore_errors = get_common_errors() + ignore_error
        logging.info("Here is the bteq ignore errors: %s", bteq_ignore_errors)

        # Filter out the error that can not be ignore
        bteq_errors_that_not_ignore = filter_critical_errors(bteq_errors_found, bteq_ignore_errors)


        # Convert errors from list to string for showing
        bteq_ignore_error_set = str(tuple(bteq_ignore_errors))
        bteq_error_found_set = str(tuple(bteq_errors_found))
        bteq_errors_that_not_ignore_set = str(tuple(bteq_errors_that_not_ignore))




        if bteq_has_critical_error(bteq_errors_found, bteq_ignore_errors):
            task_comments = "Bteq error found can not ignore: " + bteq_errors_that_not_ignore_set + " . Ignore list: " + bteq_ignore_error_set + " found list: " + bteq_error_found_set
            log_file = os.path.join(bteq_python_output, "fail", bteq_logfile_name)
            end_tracking(uuid_id, False)
            logging.error("Here is the bteq error(s) found: %s and here is the ignore error list: %s" % (bteq_errors_found, bteq_ignore_errors, ))
            logging.error("Bteq errors found that can not be ignored: %s. Please check out this log file: %s" % (bteq_errors_that_not_ignore, log_file, ))
            output_dest = os.path.join(bteq_python_output, "fail")
            jenkins_dest = os.path.join(main_output_repository, 'jmeter_python', database_name, 'test', 'all_fail')
            copy_file(bteq_python_output, output_dest, bteq_logfile_name)
            copy_file(bteq_python_output, output_dest, bteq_python_log)
            copy_file(bteq_python_output, jenkins_dest, bteq_python_log)
            exit(1)
        else:
            task_comments = "Either there is no bteq error or error found is in ignore list"
            log_file = os.path.join(bteq_python_output, "pass", bteq_logfile_name)
            end_tracking(uuid_id, True)
            output_dest = os.path.join(bteq_python_output, "pass")
            copy_file(bteq_python_output, output_dest, bteq_logfile_name)

    except Exception as e:
        logging.error(traceback.format_exc())
        exit(1)

    exit(0)
