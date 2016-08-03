#!/usr/bin/python3
# File: run_jmeter_from_jenkins.py
# Author: Tam Le
# Author Email: tam.le@teradata.com
# Date Published: 03/15/2016
# Purpose: This program is running jmeter test plan and validate it's results based on samplers output
# Usage: python run_jmeter_from_jenkins.py --database_name=teradata_database --jmeter_test_plan=your_jmeter_test_plan --number_of_loop=1 --duration_in_seconds=30
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
import teradata
import tarfile
python_src = os.path.dirname(os.path.realpath(__file__))
os_user_name = getpass.getuser()
os_type = platform.system()
#if os_user_name == "tomcat":
#    sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'common'))
#else:
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', '..', 'common')) 
import tdtestpy
        

# Run jmeter command using subprocess
"""
def run_jmeter(jmeter_run_file, sampler_output, jmeter_output, jmeter_log, run_test, run_setup, run_cleanup \
                   , dbs_name, num_users, ldi_read_clone, pll_read_clone, \
                   all_read_clone, ldi_write, pll_write, validate_results, dbc_password, node_password, tpt_trace_level, update_control_file, run_timestamp):
    subprocess.call(["/usr/bin/jmeter", "-n", "-t", jmeter_run_file, "-l", sampler_output, "-j", jmeter_output
                     , "-Jrun_test={run_test}".format(run_test=run_test)
                     , "-Jrun_setup={run_setup}".format(run_setup=run_setup) 
                     , "-Jrun_cleanup={run_cleanup}".format(run_cleanup=run_cleanup) 
                     , "-Jdbs_name={dbs_name}".format(dbs_name=dbs_name)  
                     , "-Jnum_users={num_users}".format(num_users=num_users) 
                     , "-Jldi_read_clone={ldi_read_clone}".format(ldi_read_clone=ldi_read_clone) 
                     , "-Jpll_read_clone={pll_read_clone}".format(pll_read_clone=pll_read_clone) 
                     , "-Jall_read_clone={all_read_clone}".format(all_read_clone=all_read_clone) 
                     , "-Jldi_write={ldi_write}".format(ldi_write=ldi_write) 
                     , "-Jpll_write={pll_write}".format(pll_write=pll_write) 
                     , "-Jvalidate_results={validate_results}".format(validate_results=validate_results) 
                     , "-Jdbc_password={dbc_password}".format(dbc_password=dbc_password)
                     , "-Jnode_password={node_password}".format(node_password=node_password)
                     , "-Jtpt_trace_level={tpt_trace_level}".format(tpt_trace_level=tpt_trace_level)
                     , "-Jupdate_control_file={update_control_file}".format(update_control_file=update_control_file) 
                     , "-Jrun_timestamp={run_timestamp}".format(run_timestamp=run_timestamp)
                    ], stdout=open(jmeter_log, 'w'), stderr=subprocess.STDOUT)
"""
def run_jmeter(jmeter_run_file, sampler_output, jmeter_output, jmeter_log, properties_file):
    subprocess.call(["/usr/bin/jmeter", "-n", "-t", jmeter_run_file, "-l" , sampler_output \
        , "-j", jmeter_output, "-q", properties_file] \
        , stdout=open(jmeter_log, 'w'), stderr=subprocess.STDOUT)

# scan for error from all files in a directory
def check_error_from_all_file_in_directory(path_of_error_logs, what_to_scan):
   files = glob.glob(path_of_error_logs)
   for fname in files:
     try:
        with open(fname) as f:
           for line in f:
              if what_to_scan in line:
                  #print_after_error = line.split("ERROR -", 1)[1]
                  #print ("Scan file Name: %s. Found Message:%s" % (fname, print_after_error))
                  print ("File Name: %s. Found Message:%s" % (fname, line))
                  break
     except IOError as exc:
        if exc.errno != errno.EISDIR: # Do not fail if a directory is found, just ignore it.
            raise # Propagate other kinds of IOError.


def delete_directory(name_of_dir):
     try:
        shutil.rmtree(name_of_dir)
     except OSError as e:
        if e.errno != errno.ENOENT:
            raise
        
        
# Python exit wrapper function
def exit(ok=True):
    if ok is True or ok == 0:
        logging.info("================= End: [LDI and PLL test completed Successful] =================")
        sys.exit(0)
    else:
        logging.info("================= End: [Test failed, please checkout log file here: %s] =================" % (failedtask))
        sys.exit(1)

        
def setup_argparse():
    parser = argparse.ArgumentParser(description="### run_jmeter_from_jenkins.py ###")
    parser.add_argument("--jmeter_prop_file", required=True, help="jmeter_prop_file Test Plan")
    return parser.parse_args()

if __name__ == "__main__":

    try:
        udaExec = teradata.UdaExec (appName="RUN_JENKINS", version="1.0", logConsole=True)
        args = setup_argparse()
        # Get user input and create dynamic variables
        jmeter_test_plan = "ldi_and_pll_test.jmx"
        jmeter_prop_file = args.jmeter_prop_file
        

        dbs_name = tdtestpy.get_property_value (jmeter_prop_file, "dbs_name")
        run_iteration =  int(tdtestpy.get_property_value (jmeter_prop_file, "run_iteration"))
        run_duration = int(tdtestpy.get_property_value (jmeter_prop_file, "run_duration"))
        run_timestamp = tdtestpy.get_property_value (jmeter_prop_file, "run_timestamp")
        jmeter_scriptPath = os.path.join(python_src, '../')
        failedtask = os.path.join(jmeter_scriptPath, "output", dbs_name, run_timestamp, "failed")
        test_log_path = os.path.join(jmeter_scriptPath, "output", dbs_name, run_timestamp, "latest")

        
        #Create jmter output directory
        tdtestpy.ensure_dir(test_log_path)
        tdtestpy.ensure_dir(failedtask)
        
        
        # dump python log file to choosing directory for easy access
        jmeter_python_log_name = dbs_name + "_" + os.path.splitext(jmeter_test_plan)[0] + "_python.log"
        fh = logging.FileHandler(jmeter_python_log_name, mode="a", encoding="utf8")
        fh.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
        fh.setLevel(logging.DEBUG)
        root = logging.getLogger()
        root.addHandler(fh)
        
        # Convert to new jmeter test plan based on user input of run_iteration or run_duration
        duration_seconds = run_duration * 60
        # if run_iteration and run_duration both 0 then we set default to run 1 iteration
        if (run_iteration == 0 and run_duration == 0):
            old_run_iteration = r'<stringProp name="LoopController.loops">${run_iteration}</stringProp>'
            new_run_iteration = r'<stringProp name="LoopController.loops">1</stringProp>'
            old_run_duration = r'<stringProp name="ThreadGroup.duration">${__property(duration_seconds)}</stringProp>'
            new_run_duration = r'<stringProp name="ThreadGroup.duration">0</stringProp>'
            old_scheduler_enable = '<boolProp name="ThreadGroup.scheduler">true</boolProp>'
            new_scheduler_enable = '<boolProp name="ThreadGroup.scheduler">false</boolProp>'
            need_replace_items = {old_run_iteration:new_run_iteration, old_run_duration:new_run_duration, \
                              old_scheduler_enable:new_scheduler_enable} 
            
        elif (run_iteration > 0 and run_duration >= 0):
            old_run_iteration = r'<stringProp name="LoopController.loops">${run_iteration}</stringProp>'
            new_run_iteration = '<stringProp name="LoopController.loops">' + str(run_iteration) + '</stringProp>'
            old_run_duration = r'<stringProp name="ThreadGroup.duration">${__property(duration_seconds)}</stringProp>'
            new_run_duration = r'<stringProp name="ThreadGroup.duration">0</stringProp>'
            old_scheduler_enable = '<boolProp name="ThreadGroup.scheduler">true</boolProp>'
            new_scheduler_enable = '<boolProp name="ThreadGroup.scheduler">false</boolProp>'
            need_replace_items = {old_run_iteration:new_run_iteration, old_run_duration:new_run_duration, \
                              old_scheduler_enable:new_scheduler_enable}
            
        elif (run_iteration == 0 and run_duration > 0):
            old_run_iteration = r'<stringProp name="LoopController.loops">${run_iteration}</stringProp>'
            new_run_iteration = r'<intProp name="LoopController.loops">-1</intProp>'
            
            old_runDurationseconds = r'<stringProp name="ThreadGroup.duration">${__property(duration_seconds)}</stringProp>'
            new_runDurationseconds = '<stringProp name="ThreadGroup.duration">' + str(duration_seconds) + '</stringProp>'   
            
            #old_scheduler_enable = '<boolProp name="ThreadGroup.scheduler">false</boolProp>'
            #new_scheduler_enable = '<boolProp name="ThreadGroup.scheduler">true</boolProp>'
            
            need_replace_items = {old_run_iteration:new_run_iteration, old_runDurationseconds:new_runDurationseconds} 
        
        else:
            logging.error("sorry, can't figure out what you try to do, please change run_iteration and run_duration")
            exit(1)
 
        
        # Create new test plan
        jmeter_run_file = dbs_name + "_" + jmeter_test_plan
         
        tdtestpy.convert_a_template(jmeter_test_plan, jmeter_run_file, need_replace_items)
        
        #jmeter_output_name = dbs_name + "_" + os.path.splitext(jmeter_test_plan)[0] + "_jmeter_output.txt"
        #jmeter_output_name = os.path.splitext(jmeter_test_plan)[0] + "_jmeter_output.txt"
        jmeter_output_name = "jmeter_output.txt"
        jmeter_output = os.path.join(test_log_path, jmeter_output_name)
        sampler_output_name = "sampler_output.txt"
        sampler_output = os.path.join(test_log_path, sampler_output_name)
        jmeter_log_name = "jmeter_log.txt"
        jmeter_log = os.path.join(test_log_path, jmeter_log_name)

        
        # Start jmeter test plan
        logging.info("Start running jmeter test plan")
        run_jmeter (jmeter_run_file, sampler_output, jmeter_output, jmeter_log, jmeter_prop_file)
        
        logging.info("jmeter test completed")
        
        #logging.info("Start archiving output")
        #tdtestpy.tarfile_archive (full_archive_name, os.path.join(jmeter_scriptPath, "output"))
        #logging.info("Archiving output completed")
        
        # Scan the Jmeter sampler logs
        logging.info("Scanning for failed sampler output, and failure")
        if tdtestpy.scan_a_file(sampler_output, "Uexpected return code"):
            #logging.error("Your LDI and PLL failed, please checkout log file here: %s" % (failedtask))
            #path_of_error_logs = os.path.join(failedtask, '*.log')
            #tdtestpy.scan_files_extension (path_of_error_logs, "failed with error")
            #tarfile_archive (full_archive_name, os.path.join(jmeter_scriptPath, "output"))
            exit(1)
        
    except Exception as e:
        logging.error(traceback.format_exc())
        exit(1)

    exit(0)
