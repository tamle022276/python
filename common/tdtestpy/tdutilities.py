"""
This is common module that run Teradata utilities such as BTEQ, TPT via python subprocess.
Date Published: 05/15/2016
Contributors: tl151006 (tl151006@teradata.com)
"""
import os
import subprocess
import re
import sys
import uuid
import logging
from multiprocessing import Process, Pool
import threading, queue
from .osutilities import copy_file, delete_one_file

def run_bteq(bteq_input_file, bteq_log_file, database_name, user_name, user_password, bteq_ignore_errors="[0000]"):
    """
    Run Teradata Bteq script and check for errors.

    Args:
        bteq_input_file (str): Bteq script with queries
        bteq_log_file (str): Name of file that save the output
        database_name (str): Teradata database that Bteq will connect to
        user_name (str): User that have permission to run queries from bteq_input_file
        user_password (str): Password for user_name
        bteq_ignore_errors (Optional(list([int]))): List of errors that can be ignore

    Returns:
        False and errors if errors found that not in bteq_ignore_errors, True and errors (0000) if successful.

    Raises:
        Raising exception
    """

    database_name = database_name.strip()
    user_name = user_name.strip()
    user_password = user_password.strip()
    
    if database_name and user_name and user_password: # if (database_name, user_name, user_password) not empty 
        subprocess.call(["bteq", ".logon", "{}/{},{}".format(database_name, user_name, user_password)], \
                    stdin=open(bteq_input_file), stdout=open(bteq_log_file, 'w'), stderr=subprocess.STDOUT)
    elif not database_name and not user_name and not user_password: # if (database_name, user_name, user_password) is empty 
        subprocess.call(["bteq"], stdin=open(bteq_input_file), stdout=open(bteq_log_file, 'w'), stderr=subprocess.STDOUT)
    elif database_name and not user_name and not user_password: # if database_name not empty, and (user_name, user_password) is empty 
        subprocess.call(["bteq", ".tdp", "{}".format(database_name)], \
                    stdin=open(bteq_input_file), stdout=open(bteq_log_file, 'w'), stderr=subprocess.STDOUT)
    else:
        logging.error("run_bteq function can not figure out your passing variables")
        sys.exit(1)
                  
    bteq_errors_found = []
    #http://stackoverflow.com/questions/12468179/unicodedecodeerror-utf8-codec-cant-decode-byte-0x9c
    with open(bteq_log_file, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f.readlines():
            m = re.search(r"\*\*\* Failure (\d+)", line)
            m_error = re.search(r"\*\*\* Error (\d+)", line)
            if m:
                bteq_errors_found.append(int(m.group(1)))
            if m_error:
                bteq_errors_found.append(int(m_error.group(1)))
    error_set = set(bteq_errors_found)
    ignore_set = set(bteq_ignore_errors)
    bteq_errors_that_not_ignore = list(error_set.difference(ignore_set))
    if error_set.issubset(ignore_set):
        return True, bteq_errors_that_not_ignore
    else:
        return False, bteq_errors_that_not_ignore

def run_bteq_parallel(bteq_in_file, bteq_log_file, database_name, user_name, user_password, \
                      bteq_ignore_errors, num_of_jobs=1, copy_if_fail=None, copy_to=None):
    """
    Run the same Teradata Bteq script with multiple clones and check for errors.

    Args:
        bteq_input_file (str): Bteq script with queries
        bteq_log_file (str): Name of file that save the output
        database_name (str): Teradata database that Bteq will connect to
        user_name (str): User that have permission to run queries from bteq_input_file
        user_password (str): Password for user_name
        bteq_ignore_errors (Optional(list([int]))): List of errors that can be ignore
        num_of_jobs (int): Number of clone jobs that Teradata Bteq will run in parallel
        copy_if_fail (Optional[str]): The directory that bteq_log_file copy to in case it failed
        copy_to (Optional[str]): The directory that bteq_log_file copy to after it completed successful

    Returns:
        False if errors found not in bteq_ignore_errors, True if successful.

    Raises:
        Raising exception
    """

    def bteq_log_name(i):
        """Creates a unique logfile name with 'i' sequence number."""
        if num_of_jobs==1:
            # if running a single process don't change the name:
            return bteq_log_file
        else:
            return str(i).join(os.path.splitext(bteq_log_file))
            #return bteq_log_file + str(i)
    
    pool = Pool(processes=num_of_jobs)
    results = pool.starmap(run_bteq, [(bteq_in_file, bteq_log_name(i), database_name, user_name, \
                                       user_password, bteq_ignore_errors) for i in range(1, num_of_jobs+1)])
    bteq_pass = bteq_fail = 0
    #https://docs.python.org/2.3/whatsnew/section-enumerate.html
    for i, (bteq_run_result, bteq_errors_that_not_ignore) in enumerate(results, 1):
        
        if bteq_run_result:
            bteq_pass = bteq_pass + 1
            if copy_to is not None:
                copy_file(bteq_log_name(i), copy_to)
        else:
            logging.error("Bteq found that can not be ignored: %s, please check out this log file: %s" \
                          % (bteq_errors_that_not_ignore, bteq_log_name(i)))
            bteq_fail = bteq_fail + 1
            if copy_if_fail is not None:
                copy_file(bteq_log_name(i), copy_if_fail)
    if bteq_fail > 0:
        return False
    else:
        return True    
    
def run_single_tpt(tpt_input_file, tpt_log, directory_path, database_name, user_name, user_password, \
            dump_file_name, tracelevel, run_result=None):
    """
    Run Teradata TPT script and check for errors.

    Args:
        tpt_input_file (str): Teradata TPT script
        tpt_log (str): Name of file that save the output to
        directory_path (str): Working directory where dump data save to and load from
        database_name (str): Teradata database that TPT will connect to
        user_name (str): User that have permission to run TPT script tpt_input_file
        user_password (str): Password for user_name
        dump_file_name (str): Flat file name to TPT will save data to for export or load data for load
        tracelevel (str): TPT trace level use to debugging
        run_result (Optional[str]): Result of the run, this is use if you run TPT in parallel

    Returns:
        False if terminated message found in tpt_log, True if successful.

    Raises:
        Raising exception
    """
#http://stackoverflow.com/questions/7194884/assigning-return-value-of-function-to-a-variable-with-multiprocessing-and-a-pr
    tracelevel = tracelevel.strip() 
    if not tracelevel: # tracelevel is empty
        tracelevel = "none"      
    unique_tpt_job_id = str(uuid.uuid4())
    
    subprocess.call(["tbuild", "-f", tpt_input_file, unique_tpt_job_id, "-u", "TdpId='{database_name}', \
    UserName='{user_name}', UserPassword='{user_password}', DirectoryPath='{directory_path}', \
    FileName='{dump_file_name}', TraceLevel='{tracelevel}'".format(database_name=database_name, user_name=user_name, \
                                                                   user_password=user_password, directory_path=directory_path, \
                                                                   dump_file_name = dump_file_name, tracelevel = tracelevel)], \
                    stdout=open(tpt_log, 'w'), stderr=subprocess.STDOUT)
    with open(tpt_log, 'r') as log_f:
        for line in log_f.readlines():
            if re.search(r"terminated", line):
                if run_result is None:
                    return False
                else:
                    run_result.put(False)
    if run_result is None:
        return True
    else:
        return run_result.put(True)
    
def run_tpt_named_pipe(tpt_export_file, tpt_export_log, tpt_load_file, tpt_load_log, directory_path, database_name, \
                       user_name, user_password, tpt_named_pipe, tracelevel):
    """
    Run Teradata TPT export and load in parallel using named pipe as flat data holder

    Args:
        tpt_export_file (str): Teradata TPT export script that dump data to a named pipe
        tpt_export_log (str): Name of file that save the TPT export output to
        tpt_load_file (str): Teradata TPT load script that load data from a named pipe
        tpt_load_log (str): Name of file that save the TPT load output to
        directory_path (str): Working directory where named pipe will be create
        database_name (str): Teradata database that TPT will connect to
        user_name (str): User that have permission to run TPT script tpt_input_file
        user_password (str): Password for user_name
        tpt_named_pipe (str): Named pipe that TPT will stream data from and to
        tracelevel (str): TPT trace level use to debugging

    Returns:
        TPT result for export and load. False if terminated message found, True if successful.

    Raises:
        Raising exception
    """
    name_pipe_location = os.path.join(directory_path, tpt_named_pipe)
    delete_one_file(name_pipe_location)
    os.mkfifo(name_pipe_location)
            
    tpt_export_result = queue.Queue()
    tpt_load_result = queue.Queue()
    tpt_export = threading.Thread(target=run_single_tpt, args=(tpt_export_file, tpt_export_log, directory_path, database_name, \
                                                    user_name, user_password, tpt_named_pipe, tracelevel, tpt_export_result))
    
    tpt_load = threading.Thread(target=run_single_tpt, args=(tpt_load_file, tpt_load_log, directory_path, database_name, user_name, \
                                                    user_password, tpt_named_pipe, tracelevel, tpt_load_result))
    tpt_export.start()
    tpt_load.start()
    tpt_export.join()
    tpt_load.join()

    tpt_export_result = tpt_export_result.get()
    tpt_load_result = tpt_load_result.get()
            
    return tpt_export_result, tpt_load_result

def run_tpt_sddg (tpt_input_file, tpt_log, dbpid, username, password, tableFullName, tableAlias, run_result=None):
    """
    Run Teradata TPT script that generated by SDDG tool

    Args:
        tpt_input_file (str): Teradata TPT script that generated by SDDG tool
        tpt_log (str): Name of file that save the output to
        dbpid (str): Teradata database that TPT will connect to
        username (str): User that have permission to run TPT script tpt_input_file
        password (str): Password for user_name
        tableFullName (str): Name of table TPT will use to export or load
        tableAlias (str): Alias for tableFullName
        run_result (Optional[str]): Result of the run, this is use if you run TPT in parallel

    Returns:
        False if terminated message found in tpt_log, True if successful.

    Raises:
        Raising exception
    """

    #http://stackoverflow.com/questions/7194884/assigning-return-value-of-function-to-a-variable-with-multiprocessing-and-a-pr     
    #unique_tpt_job_id = os.path.splitext(tpt_input_file)[0] + "_" + str(uuid.uuid4())
    unique_tpt_job_id = str(uuid.uuid4())
    
    subprocess.call(["tbuild", "-f", tpt_input_file, unique_tpt_job_id, "-u", "dbpid='{dbpid}', \
    username='{username}', password='{password}', tableFullName='{tableFullName}', \
    tableAlias='{tableAlias}'".format(dbpid = dbpid, username = username, password = password, \
                                      tableFullName = tableFullName, tableAlias = tableAlias)], \
                    stdout=open(tpt_log, 'w'), stderr=subprocess.STDOUT)
    with open(tpt_log, 'r') as log_f:
        for line in log_f.readlines():
            if re.search(r"terminated", line):
                if run_result is None:
                    return False
                else:
                    run_result.put(False)
    if run_result is None:
        return True
    else:
        return run_result.put(True)
    
