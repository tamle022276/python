#Sample run: python tpt_python_pipe.py --database_name=hela --user_name=sitq_ldi_pll_user1 --user_password=sitq_ldi_pll_user1
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
#from multiprocessing import Pool
from multiprocessing import Process

udaExec = teradata.UdaExec (appName="Jmeter-Python", version="1.0", logConsole=True)

######################################
repository_database = "hela"
repository_user = "dbc"
repository_pass = "dbc"
test_id = 55555
os_type = platform.system()
main_output_repository = '/common/SIT/test_output' if os_type == "Linux" else 'C:\Temp\\test_output'

tpt_export_file = "tpt_export.tpt"
tpt_load_file = "tpt_load.tpt"

agent_name = socket.gethostname()
get_uuid = uuid.uuid4()
os_user_name = getpass.getuser()
src = os.path.dirname(os.path.realpath(__file__))
run_times = time.strftime("%m%d%y%H%M%S")

# get run_id from repository_db.test_status
def get_run_id():
   with udaExec.connect(method="odbc", system=repository_database, username=repository_user, password=repository_pass) as session:
    with session.cursor() as cursor:
     cursor.execute("select max(run_id) from repository_db.test_status where test_id = %s and database_name = '%s' and run_by = '%s'" % (test_id, database_name, os_user_name))
     res = cursor.fetchone()
   return res[0]

# Start logging into for tracking
def start_tracking(task_name, logs_file, uuid_id):

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


# Run tpt command using subprocess
def run_tpt(tpt_input_file, unique_tpt_job_id, tpt_log, directory_path, database_name, user_name, user_password, dump_file_name):
    subprocess.call(["tbuild", "-f", tpt_input_file, unique_tpt_job_id, "-u", "TdpId='{database_name}', UserName='{user_name}', UserPassword='{user_password}', DirectoryPath='{directory_path}', FileName='{dump_file_name}'".format(database_name=database_name, user_name=user_name, user_password=user_password, directory_path=directory_path, dump_file_name = dump_file_name)], stdout=open(tpt_log, 'w'), stderr=subprocess.STDOUT)

# scan the tpt log and check for terminated message
def check_tpt_log(tpt_logfile):
    with open(tpt_logfile, 'r') as f:
        for line in f.readlines():
            if re.search(r"terminated", line):
                return False
    return True

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

# Copy file function
def copy_file(src, dest, filename):
   shutil.copy(os.path.join(src, filename), os.path.join(dest, filename))


# Delete one file and ignore if it does not exists
def delete_one_file(name_of_file_with_path):
     try:
        os.remove(name_of_file_with_path)
     except OSError as e:
        if e.errno != errno.ENOENT:
            raise

# Python exit wrapper function
def exit(ok=True):
    if ok is True or ok == 0:
        logging.info("================= End: [TPT completed sucess] =================")
        sys.exit(0)
    else:
        logging.info("================== End: [TPT Fail, please investigate logs] ==================")
        sys.exit(1)


if __name__ == "__main__":

    try:
        args = setup_argparse()
        database_name = args.database_name
        user_name = args.user_name
        user_password = args.user_password

        export_uuid_id = str(get_uuid) + "_tpt_export"
        load_uuid_id = str(get_uuid) + "_tpt_load"
        run_id = get_run_id()

        # dump python log file to choosing directory for easy access
        tpt_python_log_name = database_name + "_" + user_name + "_" + run_times + "_tpt_python_log.txt"
        tpt_main_output = os.path.join(main_output_repository, 'jmeter_python', database_name, 'test', 'tpt')
        tpt_python_output = os.path.join(tpt_main_output, tpt_python_log_name)
        fh = logging.FileHandler(tpt_python_output, mode="a", encoding="utf8")
        fh.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
        fh.setLevel(logging.DEBUG)
        root = logging.getLogger()
        root.addHandler(fh) 


        # Create log file for TPT Export
        tpt_export_file = os.path.join(src, tpt_export_file)
        export_log_name = database_name + "_" + user_name + "_" + run_times + "_tpt_export_log.txt"
        tpt_export_log = os.path.join(tpt_main_output, export_log_name)


        # Create log file for TPT load
        tpt_load_file = os.path.join(src, tpt_load_file)
        load_log_name = database_name + "_" + user_name + "_" + run_times + "_tpt_load_log.txt"
        tpt_load_log = os.path.join(tpt_main_output, load_log_name)

	# Join directory path and dump named pipe
        directory_path = os.path.join(tpt_main_output, "data_file")
        dump_file_name = user_name + "_" + "return_trans_line"
        tpt_named_pipe = os.path.join(directory_path, dump_file_name)
        
        # Delete named pipe if it exists and create again
        delete_one_file(tpt_named_pipe)
        os.mkfifo(tpt_named_pipe)

        # Useful info for debugs
        logging.info("Some useful info for debug:")
        logging.info(" * Database Name: %s", database_name)
        logging.info(" * User name: %s", user_name)
        logging.info(" * User Password: %s", user_password)
        logging.info(" * TPT export file: %s", tpt_export_file)
        logging.info(" * TPT export log: %s", tpt_export_log)
        logging.info(" * TPT load file: %s", tpt_load_file)
        logging.info(" * TPT load log: %s", tpt_load_log)


        # Start tracking for tpt export and load
        logging.info("Start TPT tracking")
        start_tracking('tpt_export', tpt_export_log, export_uuid_id)
        start_tracking('tpt_load', tpt_load_log, load_uuid_id)

        # Run tpt export and load in parallel
        logging.info("Start TPT export and load in parallel")
        tpt_rtl_export = Process(target=run_tpt, args=(tpt_export_file, export_uuid_id, tpt_export_log, directory_path, database_name, user_name, user_password, dump_file_name))
        tpt_rtl_load = Process(target=run_tpt, args=(tpt_load_file, load_uuid_id, tpt_load_log, directory_path, database_name, user_name, user_password, dump_file_name))
        tpt_rtl_export.start()
        tpt_rtl_load.start()
        tpt_rtl_export.join()
        tpt_rtl_load.join()
        logging.info("Finished TPT export and load in parallel")

        # Scan the tpt export log for error
        logging.info("Scanning export log...")
        if not check_tpt_log(tpt_export_log):
            task_comments = "we found terminated message in the export log"
            log_file = os.path.join(tpt_main_output, "fail", export_log_name)
            end_tracking(export_uuid_id, False)
            logging.error("TPT export has terminated message. Please check out this log file: %s" % (log_file, ))
            output_dest = os.path.join(tpt_main_output, "fail")
            jenkins_dest = os.path.join(main_output_repository, 'jmeter_python', database_name, 'test', 'all_fail')
            copy_file(tpt_main_output, output_dest, export_log_name)
            copy_file(tpt_main_output, jenkins_dest, tpt_python_log_name)
            exit(1)
        else:
            task_comments = "TPT export ran successful"
            log_file = os.path.join(tpt_main_output, "pass", export_log_name)
            end_tracking(export_uuid_id, True)
            output_dest = os.path.join(tpt_main_output, "pass")
            copy_file(tpt_main_output, output_dest, export_log_name)

        # Scan the tpt load log for error
        logging.info("Scanning load log...")
        if not check_tpt_log(tpt_load_log):
            task_comments = "we found terminated message in the load log"
            log_file = os.path.join(tpt_main_output, "fail", load_log_name)
            end_tracking(load_uuid_id, False)
            logging.error("TPT load has terminated message. Please check out this log file: %s" % (log_file, ))
            output_dest = os.path.join(tpt_main_output, "fail")
            jenkins_dest = os.path.join(main_output_repository, 'jmeter_python', database_name, 'test', 'all_fail')
            copy_file(tpt_main_output, output_dest, load_log_name)
            copy_file(tpt_main_output, jenkins_dest, tpt_python_log_name)
            exit(1)
        else:
            task_comments = "TPT load ran successful"
            log_file = os.path.join(tpt_main_output, "pass", load_log_name)
            end_tracking(load_uuid_id, True)
            output_dest = os.path.join(tpt_main_output, "pass")
            copy_file(tpt_main_output, output_dest, load_log_name)
    except Exception as e:
        logging.error(traceback.format_exc())
        exit(1)

    exit(0)
