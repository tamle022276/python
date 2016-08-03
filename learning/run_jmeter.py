# File: run_jmeter.py
# Author: Tam Le
# Author Email: tam.le@teradata.com
# Date Published: 01/29/2015
# Purpose: This program is running jmeter test plan and validate it's results based on samplers output
# Usage: python run_jmeter.py --database_name=teradata_database --jmeter_test_plan=your_jmeter_test_plan --number_of_loop=1 --duration_in_seconds=30
import sys
import os
import shutil
import time
import re
import argparse
import errno
import subprocess
import traceback
import logging
import socket
import zipfile
import uuid
import getpass
import platform
import glob
python_src = os.path.dirname(os.path.realpath(__file__))
os_user_name = getpass.getuser()
os_type = platform.system()
if os_type == "Windows":
    sys.path.append('C:\\Users\\TL151006\\Desktop\\dev\\trunk\\common')
if os_type == "Linux":
    sys.path.append('jmeter-svn/common')
if os_user_name == "tomcat":
    sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "common"))
import uda2c

main_output_repository = '/common/SIT/test_output' if os_type == "Linux" else 'C:\Temp\\test_output'
test_output_directory = "jmeter_python"

# Run jmeter command using subprocess
def run_jmeter(jmeter_run_file, sampler_output, jmeter_output, jmeter_log):
    subprocess.call(["/usr/bin/jmeter", "-n", "-t", jmeter_run_file, "-l", sampler_output, "-j", jmeter_output], stdout=open(jmeter_log, 'w'), stderr=subprocess.STDOUT)

# Run python command using subprocess
def run_python(python_file, database_name):
    subprocess.call(["python", python_file, "--database_name={database_name}".format(database_name=database_name), "--user_name=dbc", "--user_password=dbc"])

# scan for error from all files in a directory
def check_error_from_all_file_in_directory(path_of_error_logs, what_to_scan):
   files = glob.glob(path_of_error_logs)
   for fname in files:
     try:
        with open(fname) as f:
           for line in f:
              if what_to_scan in line:
                  print_after_error = line.split("ERROR -", 1)[1]
                  print ("Scan file Name: %s. Found Message:%s" % (fname, print_after_error))
                  break
     except IOError as exc:
        if exc.errno != errno.EISDIR: # Do not fail if a directory is found, just ignore it.
            raise # Propagate other kinds of IOError.


# Python exit wrapper function
def exit(ok=True):
    if ok is True or ok == 0:
        logging.info("================= End: [Jmeter completed sucess] =================")
        sys.exit(0)
    else:
        logging.info("================== End: [Jmeter Fail, please investigate logs] ==================")
        sys.exit(1)

def setup_argparse():
    class IgnoreErrorAction(argparse.Action):
        def __init__(self, option_strings, dest, nargs=None, **kwargs):
            if nargs is not None:
                raise ValueError("nargs not allowed")
            super(IgnoreErrorAction, self).__init__(option_strings, dest, **kwargs)

        def __call__(self, parser, namespace, values, option_string=None):
            incoming_nums = []
            for v in values.split(","):
                v = v.strip()
                if not v: continue
                if not v.isdigit():
                    parser.error("Invalid argument values: %s. is not possitive integers" % v)
                incoming_nums.append(int(v))
                if len(incoming_nums) == 1:
                    incoming_nums = incoming_nums[0]
            setattr(namespace, self.dest, incoming_nums)

    parser = argparse.ArgumentParser(description="### run_jmeter.py ###")
    parser.add_argument("--database_name", required=True, help="Database name")
    parser.add_argument("--jmeter_test_plan", required=True, help="Jmeter Test Plan")
    parser.add_argument("--number_of_loop", required=False, default=0, help="Loop must be possitive integers.", action=IgnoreErrorAction)
    parser.add_argument("--duration_in_seconds", required=False, default=0, help="Duration must be possitive integers.", action=IgnoreErrorAction)

    return parser.parse_args()


if __name__ == "__main__":

    try:

        args = setup_argparse()
        # Get user input 
        database_name = args.database_name
        jmeter_test_plan = args.jmeter_test_plan
        number_of_loop = args.number_of_loop
        duration_in_seconds = args.duration_in_seconds

        # dump python log file to choosing directory for easy access
        jmeter_python_log_name = database_name + "_" + os.path.splitext(jmeter_test_plan)[0] + "_python.log"
        fh = logging.FileHandler(jmeter_python_log_name, mode="a", encoding="utf8")
        fh.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
        fh.setLevel(logging.DEBUG)
        root = logging.getLogger()
        root.addHandler(fh)

        # Convert to new variables
        
        if (number_of_loop == 0 and duration_in_seconds == 0):
            new_loop_count = '<stringProp name="Argument.value">${__P(LoopCount,' + '1' + ')}</stringProp>'
            new_duration = '<stringProp name="Argument.value">${__P(Durations,' + '0' + ')}</stringProp>'
            new_scheduler_enable = '<boolProp name="ThreadGroup.scheduler">false</boolProp>'
            old_scheduler_enable = '<boolProp name="ThreadGroup.scheduler">true</boolProp>'
        elif (number_of_loop > 0 and duration_in_seconds >= 0):
            new_loop_count = '<stringProp name="Argument.value">${__P(LoopCount,' + str(number_of_loop) + ')}</stringProp>'
            new_duration = '<stringProp name="Argument.value">${__P(Durations,' + '0' + ')}</stringProp>'
            new_scheduler_enable = '<boolProp name="ThreadGroup.scheduler">false</boolProp>'
            old_scheduler_enable = '<boolProp name="ThreadGroup.scheduler">true</boolProp>'
        elif (number_of_loop == 0 and duration_in_seconds > 0):
            new_loop_count = '<stringProp name="Argument.value">${__P(LoopCount,' + '-1' + ')}</stringProp>'
            new_duration = '<stringProp name="Argument.value">${__P(Durations,' + str(duration_in_seconds) + ')}</stringProp>'
            new_scheduler_enable = '<boolProp name="ThreadGroup.scheduler">true</boolProp>'
            old_scheduler_enable = '<boolProp name="ThreadGroup.scheduler">false</boolProp>'
        else:
            logging.error("sorry, can't figure out what you try to do")
            exit(1)

        new_database = '<stringProp name="Argument.value">${__P(DBname,' + database_name + ')}</stringProp>'
        new_python_dir = '<stringProp name="Argument.value">${__P(PythonDir,' + python_src + ')}</stringProp>'

        # Scan jmeter test plan to get old variables
        if not uda2c.get_full_line_if_string_match(jmeter_test_plan, "__P(Durations,"):
            logging.error('Your string "__P(Durations," is not in %s, please investigate' % (jmeter_test_plan))
            exit(1)
        else:
            old_duration = uda2c.get_full_line_if_string_match(jmeter_test_plan, "__P(Durations,")


        if not uda2c.get_full_line_if_string_match(jmeter_test_plan, "__P(LoopCount,"):
            logging.error('Your string "__P(LoopCount," is not in %s, please investigate' % (jmeter_test_plan))
            exit(1)
        else:
            old_loop_count = uda2c.get_full_line_if_string_match(jmeter_test_plan, "__P(LoopCount,")

        if not uda2c.get_full_line_if_string_match(jmeter_test_plan, "__P(PythonDir,"):
            logging.error('Your string "__P(PythonDir," is not in %s, please investigate' % (jmeter_test_plan))
            exit(1)
        else:
            old_python_dir = uda2c.get_full_line_if_string_match(jmeter_test_plan, "__P(PythonDir,")

        if not uda2c.get_full_line_if_string_match(jmeter_test_plan, "__P(DBname,"):
            logging.error('Your string "__P(DBname," is not in %s, please investigate' % (jmeter_test_plan))
            exit(1)
        else:
            old_database = uda2c.get_full_line_if_string_match(jmeter_test_plan, "__P(DBname,")


        # Replace old with new variables
        need_replace_items = {old_database:new_database, old_python_dir:new_python_dir, old_loop_count:new_loop_count, old_duration:new_duration, old_scheduler_enable:new_scheduler_enable}

        logging.info("Old Database: %s" % (old_database))
        logging.info("New Database: %s" % (new_database))
        logging.info("Old Python Directory: %s" % (old_python_dir))
        logging.info("New Python Directory: %s" % (new_python_dir))
        logging.info("Old Loop Count: %s" % (old_loop_count))
        logging.info("New Loop Count: %s" % (new_loop_count))
        logging.info("Old Duration: %s" % (old_duration))
        logging.info("New Duration: %s" % (new_duration))
        logging.info("Old Scheduler Enable: %s" % (old_scheduler_enable))
        logging.info("New Scheduler Enable: %s" % (new_scheduler_enable))



        path_of_error_logs = os.path.join(main_output_repository, test_output_directory, database_name, 'test', 'all_fail', '*.txt')

        jmeter_run_file = database_name + "_new_" + jmeter_test_plan
        jmeter_output = database_name + "_" + os.path.splitext(jmeter_test_plan)[0] + "_jmeter_output.txt"
        sampler_output = database_name + "_" + os.path.splitext(jmeter_test_plan)[0] + "_sampler_output.txt"
        jmeter_log = database_name + "_" + os.path.splitext(jmeter_test_plan)[0] + "_jmeter_log.txt"

        # Delete ol logs before run
        uda2c.delete_one_file(jmeter_run_file)
        uda2c.delete_one_file(jmeter_output)
        uda2c.delete_one_file(sampler_output)
        uda2c.delete_one_file(jmeter_log)

        # convert jmeter template before run using import common codes
        logging.info("Convert jmeter template to new")
        uda2c.convert_a_template(jmeter_test_plan, jmeter_run_file, need_replace_items)
       
        # Start jmeter test plan
        logging.info("Start running jmeter test plan")
        run_jmeter(jmeter_run_file, sampler_output, jmeter_output, jmeter_log)

        # Scan the tpt export log
        logging.info("Scanning all failed sampler output")
        if not uda2c.scan_a_file(sampler_output, "Uexpected return code"):
            run_python("post_test.py", database_name)
            logging.error("Your Jmeter test failed because we found following message while scan your logs")
            check_error_from_all_file_in_directory(path_of_error_logs, "Please check out this log file")
            exit(1)
        else:
            run_python("post_test.py", database_name)

    except Exception as e:
        logging.error(traceback.format_exc())
        exit(1)

    exit(0)
