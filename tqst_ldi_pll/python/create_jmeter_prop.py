#!/usr/bin/python3
# File: create_jmeter_prop.py
# Author: Tam Le
# Author Email: tam.le@teradata.com
# Date Published: 06/07/2016
# Purpose: This program is creating jmeter properties file
import sys
import os
import time
import argparse
import teradata
import logging
working_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(working_dir, '..', '..', 'common')) 
import tdtestpy
    

# Python exit wrapper function
def exit(ok=True):
    if ok is True or ok == 0:
        logging.info("================= End: [Properties file created successful] =================")
        sys.exit(0)
    else:
        logging.info("================== End: [Properties file created Failed] =================")
        sys.exit(1)

# Arguments passing with command-line  
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
            
    parser = argparse.ArgumentParser(description="### create_jmeter_prop.py ###")
    parser.add_argument("--run_test", choices=('true', 'false'), required=True, help="run_test")
    parser.add_argument("--run_setup", choices=('true', 'false'), required=True, help="run_setup")
    parser.add_argument("--run_cleanup", choices=('true', 'false'), required=True, help="run_cleanup")
    parser.add_argument("--dbs_name", required=True, help="dbs_name")
    parser.add_argument("--run_iteration", required=True, help="run_iteration must be possitive integers.", action=IgnoreErrorAction)
    parser.add_argument("--run_duration", required=True, help="run_duration must be possitive integers.", action=IgnoreErrorAction)
    parser.add_argument("--num_users", required=True, help="num_users must be possitive integers.", action=IgnoreErrorAction)
    parser.add_argument("--ldi_read_clone", required=True, help="ldi_read_clone must be possitive integers.", action=IgnoreErrorAction)
    parser.add_argument("--pll_read_clone", required=True, help="pll_read_clone must be possitive integers.", action=IgnoreErrorAction)
    parser.add_argument("--all_read_clone", required=True, help="all_read_clone must be possitive integers.", action=IgnoreErrorAction)
    parser.add_argument("--ldi_write", choices=('true', 'false'), required=True, help="ldi_write")
    parser.add_argument("--pll_write", choices=('true', 'false'), required=True, help="pll_write")
    parser.add_argument("--validate_results", choices=('true', 'false'), required=True, help="validate_results")
    parser.add_argument("--dbc_password", required=True, help="dbc_password")
    parser.add_argument("--node_password", required=True, help="node_password")
    parser.add_argument("--update_control_file", required=False, default = "false", help="update_control_file")
    parser.add_argument("--tpt_trace_level", choices=('all', 'none'), required=True, help="tpt_trace_level")
    parser.add_argument("--action_on_error", choices=('continue', 'stoptest', 'startnextloop', 'stopthread', 'stoptestnow'), required=True, help="action_on_error")
    return parser.parse_args()


if __name__ == "__main__":
    udaExec = teradata.UdaExec (appName="JMETERPROP", version="1.0", logConsole=True)
    args = setup_argparse()
    run_test = args.run_test
    run_setup = args.run_setup
    run_cleanup = args.run_cleanup
    dbs_name = args.dbs_name
    run_iteration = args.run_iteration
    run_duration = args.run_duration
    num_users = args.num_users
    ldi_read_clone = args.ldi_read_clone
    pll_read_clone = args.pll_read_clone
    all_read_clone = args.all_read_clone
    ldi_write = args.ldi_write
    pll_write = args.pll_write
    validate_results = args.validate_results
    dbc_password = args.dbc_password
    node_password = args.node_password
    update_control_file = args.update_control_file
    tpt_trace_level = args.tpt_trace_level
    action_on_error = args.action_on_error
    
    #run_timestamp = time.strftime("%Y-%m-%d-%H-%M")

    jmeter_prop_name = os.path.join(working_dir, "..", "tqst_ldi_pll.properties")
    
    tdtestpy.delete_one_file (jmeter_prop_name)

    
    # dump python log file to choosing directory for easy access
    create_jmeter_prop_log = os.path.join(working_dir, "create_jmeter_properties.log")
    fh = logging.FileHandler(create_jmeter_prop_log, mode="a", encoding="utf8")
    fh.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
    fh.setLevel(logging.DEBUG)
    root = logging.getLogger()
    root.addHandler(fh)
        
try:
    # Debug info
    logging.info("*************************************DEBUG INFO********************************************")
    logging.info("System Name: %s" % (dbs_name))
    logging.info("Run Test: %s" % (run_test))
    logging.info("Run Setup: %s" % (run_setup))
    logging.info("Run Cleanup: %s" % (run_cleanup))
    logging.info("Run Iteration: %s" % (run_iteration))
    logging.info("Run Duration: %s" % (run_duration))
    logging.info("Num Users: %s" % (num_users))
    logging.info("Num LDI Read Clone: %s" % (ldi_read_clone))
    logging.info("Num PLL Read Clone: %s" % (pll_read_clone))
    logging.info("Num All Read Clone: %s" % (all_read_clone))
    logging.info("LDI Write: %s" % (ldi_write))
    logging.info("PLL Write: %s" % (pll_write))
    logging.info("Validate Results: %s" % (validate_results))
    logging.info("DBC Password: %s" % (dbc_password))
    logging.info("PDN Root Password: %s" % (node_password))
    logging.info("Update Control File: %s" % (update_control_file))
    logging.info("TPT Trace Level: %s" % (tpt_trace_level))
    logging.info("Action On Error: %s" % (action_on_error))
    #logging.info("Run Time: %s" % (run_timestamp))
    
    logging.info("*************************************Started Create Jmeter properties file ****************************************")
    
    with open (jmeter_prop_name, "w") as f:
        f.write ("run_test : " + run_test + "\n")
        f.write ("run_setup : " + run_setup + "\n")
        f.write ("run_cleanup : " + run_cleanup + "\n")
        f.write ("dbs_name : " + dbs_name + "\n")
        f.write ("run_iteration : " + str(run_iteration) + "\n")
        f.write ("run_duration : " + str(run_duration) + "\n")
        f.write ("num_users : " + str(num_users) + "\n")
        f.write ("ldi_read_clone : " + str(ldi_read_clone) + "\n")
        f.write ("pll_read_clone : " + str(pll_read_clone) + "\n")
        f.write ("all_read_clone : " + str(all_read_clone) + "\n")
        f.write ("ldi_write : " + ldi_write + "\n")
        f.write ("pll_write : " + pll_write + "\n")
        f.write ("validate_results : " + validate_results + "\n")
        f.write ("dbc_password : " + dbc_password + "\n")
        f.write ("node_password : " + node_password + "\n")
        f.write ("update_control_file : " + update_control_file + "\n")
        f.write ("tpt_trace_level : " + tpt_trace_level + "\n")
        f.write ("action_on_error : " + action_on_error)
        #f.write ("run_timestamp : " + run_timestamp)

except Exception as e:
    logging.error(traceback.format_exc())
    exit(1)

exit(0)
