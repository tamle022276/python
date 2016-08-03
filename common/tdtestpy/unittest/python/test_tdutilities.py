import unittest
import argparse
import sys
import os
import teradata
import getpass
os_user_name = getpass.getuser()
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', '..', 'common')) 
import tdtestpy

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

    parser = argparse.ArgumentParser(description="### setup.py ###")
    parser.add_argument("--dbs_name", required=True, help="System name")
    parser.add_argument("--user_name", required=True, help="user_name")
    parser.add_argument("--user_password", required=True, help="user_password")
    parser.add_argument("--ignore_error", required=False, default=[],
            help="Error number should be ignored. Must be integers separated by commas.", action=IgnoreErrorAction)
    parser.add_argument("unittest_args", nargs='*', help="unittest arguments")

    return parser.parse_args()

def create_user ():
    with db_connect.cursor() as cursor:
        try:
            cursor.execute(file=tpt_queries)
            return True
        except Exception as e:
            print ("Unit test failed with this error: %s" % ((e.args[0])))
            return False
        
class RunBTEQTest(unittest.TestCase):
    def test_runbteq(self):
        # Expected to return True.
        run_result1, error_found1 = tdtestpy.run_bteq(bteq_select, bteq_output, dbs_name, user_name, user_password, [3807, 3822])
        self.assertTrue((run_result1), True)
        
        # Expected to return False.
        run_result2, error_found2 = tdtestpy.run_bteq(bteq_select, bteq_output, dbs_name, user_name, user_password)
        self.assertFalse((run_result2), False)
        self.assertIn(3807, error_found2)
        self.assertIn(3822, error_found2)
        
    
    def test_runbteq_parallel(self):
        # Expected to return True.
        self.assertTrue(tdtestpy.run_bteq_parallel(bteq_select, bteq_output, dbs_name, user_name, user_password, [3807, 3822], num_of_jobs=5), True)
        
        # Expected to return False.
        self.assertFalse(tdtestpy.run_bteq_parallel(bteq_select, bteq_output, dbs_name, user_name, user_password, [0000], num_of_jobs=5), False)

    def test_run_tpt(self):    
        # Expected to return True if there is no error
        self.assertTrue(create_user(), True)
        
        # Expected to return True for TPT export
        self.assertTrue(tdtestpy.run_single_tpt(tpt_export, tpt_export_log, tpt_directory, dbs_name, "tdtestpy_unit_test_tpt", \
                                                "tdtestpy_unit_test_tpt", "test.dat", "none"), True)
        
        # Expected to return True for TPT streams
        self.assertTrue(tdtestpy.run_single_tpt(tpt_stream, tpt_stream_log, tpt_directory, dbs_name, "tdtestpy_unit_test_tpt", \
                                                "tdtestpy_unit_test_tpt", "test.dat", "none"), True)
        
        
        # Expected to return False, wrong password
        self.assertFalse(tdtestpy.run_single_tpt(tpt_export, tpt_incorrect_password_log, tpt_directory, dbs_name, "tdtestpy_unit_test_tpt", \
                                                "tdtestpy_unit_test_tpt_wrong_password", "wrong_password.dat", "none"), False)
        
        # Expected to return False, table does not exists
        self.assertFalse(tdtestpy.run_single_tpt(tpt_failed, tpt_failed_log, tpt_directory, dbs_name, "tdtestpy_unit_test_tpt", \
                                                "tdtestpy_unit_test_tpt", "failed.dat", "none"), False)
        
        
        # Expected to return True for TPT export and streams using named pipe
        export_result, stream_result = tdtestpy.run_tpt_named_pipe(tpt_export, tpt_export_pipe_log, tpt_stream, tpt_stream_pipe_log, \
                                                                   tpt_directory, dbs_name, "tdtestpy_unit_test_tpt", "tdtestpy_unit_test_tpt", \
                                                                   "test_pipe.dat", "none")
        self.assertTrue((export_result), True)
        self.assertTrue((stream_result), True)
        
        # Expected to return False for TPT export and True for streams using named pipe
        export_result2, stream_result2 = tdtestpy.run_tpt_named_pipe(tpt_failed, tpt_export_pipe_log_failed, tpt_stream, tpt_stream_pipe_log_no_row, \
                                                                   tpt_directory, dbs_name, "tdtestpy_unit_test_tpt", "tdtestpy_unit_test_tpt", \
                                                                   "test_pipe.dat", "none")
        self.assertFalse((export_result2), False)
        self.assertTrue((stream_result2), True)
        

        
                         
if __name__ == '__main__':
    args = setup_argparse()
        
    dbs_name = args.dbs_name
    user_name = args.user_name
    user_password = args.user_password
    ignore_error = args.ignore_error
    
    bteq_select = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', "sql", "bteq_select.txt")
    tpt_queries = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', "sql", "tpt_data.txt")
    tpt_export = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', "tpt", "export.tpt")
    tpt_export_log = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', "tpt", "export_out.log")
    tpt_stream = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', "tpt", "stream.tpt")
    tpt_failed = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', "tpt", "export_no_table.tpt")
    tpt_failed_log = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', "tpt", "failed_out.log")
    tpt_stream_log = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', "tpt", "stream_out.log")
    tpt_incorrect_password_log = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', "tpt", "incorrect_password_out.log")
    tpt_export_pipe_log = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', "tpt", "export_pipe_out.log")
    tpt_stream_pipe_log = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', "tpt", "stream_pipe_out.log")
    tpt_export_pipe_log_failed = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', "tpt", "export_pipe_failed_out.log")
    tpt_stream_pipe_log_no_row = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', "tpt", "stream_pipe_no_row_out.log")
    tpt_export_pipe_log_incorrect_pass = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', "tpt", "export_pipe_incorrect_pass_out.log")
    tpt_stream_pipe_log_incorrect_pass = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', "tpt", "stream_pipe_incorrect_pass_out.log")
      
    tpt_named_pipe = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', "tpt", "test_pipe.dat")
    tpt_directory = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', "tpt")
    
    bteq_output = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', "bteq_output.txt")
    tdtestpy.delete_one_file(bteq_output)

    udaExec = teradata.UdaExec (appName="tdtestpy", version="1.0", logConsole=True)
    db_connect = udaExec.connect(method="odbc", system=dbs_name, username=user_name, password=user_password)
    dbc_instance = tdtestpy.DBSaccess (db_connect)
    
    # Clean up test database before start unit testing just in case it failed prior run 
    dbc_instance.drop_user("tdtestpy_unit_test_tpt")  

    #http://stackoverflow.com/questions/1029891/python-unittest-is-there-a-way-to-pass-command-line-options-to-the-app
    sys.argv[1:] = args.unittest_args
    unittest.main()