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
            cursor.execute(file=sql_queries)
            return True
        except Exception as e:
            print ("Unit test failed with this error: %s" % ((e.args[0])))
            return False
        

class OSUtilitiesTest(unittest.TestCase):
    def test_scan_a_file(self):
        # Expected to return True
        self.assertTrue(tdtestpy.scan_a_file(file_scan, "logging"), True)
        # Expected to return False
        self.assertFalse(tdtestpy.scan_a_file(file_scan, "nologging"), False)
    
    def test_scan_files_extension(self):    
        # Expected to return True
        self.assertTrue(tdtestpy.scan_files_extension(file_extension, "database"), True)
        # Expected to return False
        self.assertFalse(tdtestpy.scan_files_extension(file_extension, "nologging"), False)
        
    def test_tarfile_archive(self):    
        # Expected to return True
        self.assertTrue(tdtestpy.tarfile_archive("sql_file", archive_dir), True)

    def test_convert_a_template(self):    
        # Expected to return True
        self.assertTrue(tdtestpy.convert_a_template(orig_file, new_file, "add this at the end sql_file"), True)
        # Expected to return False
        self.assertFalse(tdtestpy.convert_a_template(orig_file, new_file, ["123" , "wrong format"]), False)
    
    def test_get_full_line_if_string_match(self):    
        # Expected to return True
        self.assertEqual(tdtestpy.get_full_line_if_string_match(file_scan, "logging"), "begin query logging on tdtestpy_unit_test;")
        # Expected to return False
        self.assertFalse(tdtestpy.get_full_line_if_string_match(file_scan, "nologging"), False)
        
    def test_get_ignore_errors(self):    
        # Expected Equal
        self.assertEqual(tdtestpy.get_ignore_errors("3610, 3807"), [3610, 3807])
        # Expected Not Equal
        self.assertNotEqual (tdtestpy.get_ignore_errors("3610, 3807"), [0000, 3807])
    
    def test_compare_results(self):    
        # Expected to return True
        self.assertTrue(tdtestpy.compare_results("1", "1"), True)
        self.assertTrue(tdtestpy.compare_results(100, 100), True)
        self.assertTrue(tdtestpy.compare_results("one", "one"), True)
        # Expected to return False
        self.assertFalse(tdtestpy.compare_results("1", "one"), False)
        self.assertFalse(tdtestpy.compare_results("apple", "orange"), False)
        self.assertFalse(tdtestpy.compare_results(1, "1"), False)
        self.assertFalse(tdtestpy.compare_results(10, 100), False)
                        
if __name__ == '__main__':
    args = setup_argparse()
        
    dbs_name = args.dbs_name
    user_name = args.user_name
    user_password = args.user_password
    ignore_error = args.ignore_error
    
    udaExec = teradata.UdaExec (appName="tdtestpy", version="1.0", logConsole=True)
    db_connect = udaExec.connect(method="odbc", system=dbs_name, username=user_name, password=user_password)
    
    file_scan = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', "sql", "create_user.txt")
    file_extension = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', "sql", "*.txt")
    archive_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', "sql")
    archive_failed = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', "sql123")
    orig_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', "sql", "create_user.txt")
    new_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', "sql", "create_user_new.txt")

    #http://stackoverflow.com/questions/1029891/python-unittest-is-there-a-way-to-pass-command-line-options-to-the-app
    sys.argv[1:] = args.unittest_args
    unittest.main()