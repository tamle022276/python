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
    parser.add_argument("--node_password", required=True, help="node_password")
    parser.add_argument("unittest_args", nargs='*', help="unittest arguments")

    return parser.parse_args()

class DataCheckTest(unittest.TestCase):
    def test_scandisk(self):
        # Expected to return True
        self.assertTrue(datacheck_instance.scandisk(db_connect, scandisk_output), True)
    
    def test_checktable(self):
        # Expected to return True
        self.assertTrue(datacheck_instance.checktable(DatabaseName = "dbc", TableName = "none", CheckLevel = "two", output = checktable_output), True)
        self.assertTrue(datacheck_instance.checktable(DatabaseName = "dbc", TableName = "ErrorMsgs", CheckLevel = "three", output = checktable_output), True)
        
                    
if __name__ == '__main__':
    args = setup_argparse()
        
    dbs_name = args.dbs_name
    user_name = args.user_name
    user_password = args.user_password
    node_password = args.node_password
    
    scandisk_output = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', "scandisk_output.log")
    checktable_output = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', "checktable_output.log")
    
    udaExec = teradata.UdaExec (appName="tdtestpy", version="1.0", logConsole=True)
    db_connect = udaExec.connect(method="odbc", system=dbs_name, username=user_name, password=user_password)
    
    datacheck_instance = tdtestpy.DataCheck (dbs_name, node_password)


    #http://stackoverflow.com/questions/1029891/python-unittest-is-there-a-way-to-pass-command-line-options-to-the-app
    sys.argv[1:] = args.unittest_args
    unittest.main()