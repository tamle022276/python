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
        
class DropUserTest(unittest.TestCase):
    def test_drop_user(self):
        # Expected to return False because user tdtestpy_unit_test does not exist yet so this function didn't do any dropping.
        self.assertFalse(dbc_instance.drop_user("tdtestpy_unit_test"), False)
        # Expected to return True if there is no error
        self.assertTrue(create_user(), True)
        # Expected to return True if create_user function above return True.
        self.assertTrue(dbc_instance.drop_user("tdtestpy_unit_test"), True)
        
class DBAccessTest(unittest.TestCase):  
    """
    get_db_free_perm method test
    """ 
    # Expected message since never012336_unit_test does not exists    
    def test_get_db_free_perm_no_user(self):
        self.assertEqual(dbc_instance.get_db_free_perm("never012336_unit_test"), "never012336_unit_test does not exist")
    # Expected to be greater than 0, this is dynamic so we can't test the exact number 
    def test_get_db_free_perm_dbc(self):
        self.assertGreater(dbc_instance.get_db_free_perm("dbc"), -1)
        
    """
    get_db_current_perm method test
    """     
    # Expected message since never012336_unit_test does not exists    
    def test_get_db_current_perm_no_user(self):
        self.assertEqual(dbc_instance.get_db_current_perm("never012336_unit_test"), "never012336_unit_test does not exist")
    # Expected to be greater than 0, this is dynamic so we can't test the exact number 
    def test_get_db_current_perm_dbc(self):
        self.assertGreater(dbc_instance.get_db_current_perm("dbc"), -1)
    
    """
    get_db_max_perm method test
    """     
    # Expected message since never012336_unit_test does not exists    
    def test_get_db_max_perm_no_user(self):
        self.assertEqual(dbc_instance.get_db_max_perm("never012336_unit_test"), "never012336_unit_test does not exist")
    # Expected to be greater than 0, this is dynamic so we can't test the exact number 
    def test_get_db_max_perm_dbc(self):
        self.assertGreater(dbc_instance.get_db_max_perm("dbc"), -1)
        

class TableAccessTest(unittest.TestCase):
    """
    get_table_current_perm method test
    """   
    # Expected to be greater than 0, this is dynamic so we can't test the exact number    
    def test_get_table_current_perm_accessrights(self):
        self.assertGreater(dbc_instance.get_table_current_perm("dbc", "AccessRights"), -1)
        
    # Testing invalid table, expect error message
    def test_get_table_current_perm_invalid(self):
        self.assertEqual(dbc_instance.get_table_current_perm("dbc123", "asdsdsddf"), "dbc123.asdsdsddf is invalid table")
    
    """
    get_table_row_count method test
    """   
    # Expected exact 3 rows count return.     
    def test_get_table_row_count_exact(self):
        self.assertEqual(dbc_instance.get_table_row_count("dbc", "dbcinfo"), 3)
        
    # Expected exact 3 rows count return but using different method of testing it.
    def test_get_table_row_count_notin(self):
        self.assertNotIn(dbc_instance.get_table_row_count("dbc", "dbcinfo"), (0,1,2,4,5,6,7,8,9,10))
    
    # Expected 3807 table does not exist, test should pass since we are expecting 3807    
    def test_get_table_row_count_raise_error(self):
        with self.assertRaises(Exception) as e:
            dbc_instance.get_table_row_count("dbc", "rere6553434767rer")
        self.assertTrue("3807" in str(e.exception))
    
    # Expected 3802 Database does not exist, test should pass since we are expecting 3802    
    def test_get_table_row_count_raise_error(self):
        with self.assertRaises(Exception) as e:
            dbc_instance.get_table_row_count("dbc123", "rere6553434767rer")
        self.assertTrue("3802" in str(e.exception))
        
    """
    get_sum_of_a_column method test
    """     
    # Expected to be greater than 0, this is dynamic so we can't test the exact number    
    def test_get_sum_of_a_column_from_databasespace(self):
        self.assertGreater(dbc_instance.get_sum_of_a_column("dbc", "DataBaseSpace", "Vproc"), -1)
    
    # Expected error 5628 Column xxx not found 
    def test_get_sum_of_a_column_raise_column_error(self):
        with self.assertRaises(Exception) as e:
            dbc_instance.get_sum_of_a_column("dbc", "DataBaseSpace", "xxx")
        self.assertTrue("5628" in str(e.exception))
    
    # Expected error 3807 table "DataBaseSpace123" does not exist.
    def test_get_sum_of_a_column_raise_table_error(self):
        with self.assertRaises(Exception) as e:
            dbc_instance.get_sum_of_a_column("dbc", "DataBaseSpace123", "Vproc")
        self.assertTrue("3807" in str(e.exception))
    
    # Expected error 3802 Database 'dbc123' does not exist
    def test_get_sum_of_a_column_raise_database_error(self):
        with self.assertRaises(Exception) as e:
            dbc_instance.get_sum_of_a_column("dbc123", "DataBaseSpace", "Vproc")
        self.assertTrue("3802" in str(e.exception))

class IsDatabaseExistTest(unittest.TestCase):
    def test_is_database_exist(self):
        # Expected to return False because database dbc1234567891 does not exist.
        self.assertFalse(dbc_instance.is_database_exist("dbc1234567891"), False)
        # Expected to return True since DBC does exist
        self.assertTrue(dbc_instance.is_database_exist("dbc"), True)

class GetDBCInfoTest(unittest.TestCase):
    """
    get_num_vprocs method test
    """   
    # Expected to be greater than 0, this is dynamic so we can't test the exact number    
    def test_get_num_vprocs(self):
        self.assertGreater(dbc_instance.get_num_vprocs (), -1)
        
    """
    get_pde_release method test
    """   
    # Expected at least one "0" in the string since database is constantly upgrade so it impossible to test for exact release      
    def test_get_pde_release(self):
        self.assertIn("0", dbc_instance.get_pde_release ())
                            
    """
    get_dbs_release method test
    """   
    # Expected at least one "0" in the string since database is constantly upgrade so it impossible to test for exact release      
    def test_get_dbs_release(self):
        self.assertIn("0", dbc_instance.get_dbs_release ())

class SQLValidationTest(unittest.TestCase):
    def test_validate_sql_results(self):
        # Expected to return True because sql1 count and dbcinfo_org count is 3 and vice versa
        self.assertTrue(validate_instance.validate_sql_results(sql1, sql1_org_result), True)
        self.assertTrue(validate_instance.validate_sql_results(sql2, sql2_org_result), True)
        self.assertTrue(validate_instance.validate_sql_results(sql3, sql3_org_result), True)
        
        # Expected to return False because sql2 count is 1 and dbcinfo_org count is 3 and vice versa
        self.assertFalse(validate_instance.validate_sql_results(sql1, sql2_org_result), False)
        self.assertFalse(validate_instance.validate_sql_results(sql2, sql1_org_result), False)
      
        # Delete control file before create
        tdtestpy.delete_one_file(control_file)
        
        # Expected to return True
        self.assertTrue(validate_instance.create_control_file(sql1, "dbcinfo1"), True)
        self.assertTrue(validate_instance.create_control_file(sql2, "dbcinfo2"), True)
        self.assertTrue(validate_instance.create_control_file(sql3, "dbcinfo3"), True)

class SaveSQLResultsTest(unittest.TestCase):
    def test_run_sql(self):
        # Expected to return True
        self.assertTrue(save_results_instance.run_sql(sql1), True)
        self.assertTrue(save_results_instance.run_sql(sql2), True)
        self.assertTrue(save_results_instance.run_sql(sql3), True)
        # Expected to return False
        self.assertFalse(save_results_instance.run_sql(sql4), False)
        
        # Expected to return True
        tdtestpy.delete_one_file(save_result_output)
        self.assertTrue(save_results_instance.run_file(save_result_queries), True)

                    
if __name__ == '__main__':
    args = setup_argparse()
        
    dbs_name = args.dbs_name
    user_name = args.user_name
    user_password = args.user_password
    ignore_error = args.ignore_error
    
    sql_queries = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', "sql", "create_user.txt")
    control_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', "controlfile", "original_results.pickle")
    save_result_queries = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', "sql", "save_results.txt")
    save_result_output = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', "results_output.txt")
    tdtestpy.delete_one_file(save_result_output)

    udaExec = teradata.UdaExec (appName="tdtestpy", version="1.0", logConsole=True)
    db_connect = udaExec.connect(method="odbc", system=dbs_name, username=user_name, password=user_password)
    
    dbc_instance = tdtestpy.DBSaccess (db_connect)
    validate_instance = tdtestpy.SQLValidation (db_connect, control_file)
    allresults = validate_instance.load_control_file()
    sql1_org_result = allresults["dbcinfo1"]
    sql2_org_result = allresults["dbcinfo2"]
    sql3_org_result = allresults["dbcinfo3"]
    
    sql1 = "select count(*) from dbc.dbcinfo"
    sql2 = "select count(*) from dbc.dbcinfo where InfoKey = 'RELEASE'"
    sql3 = "select InfoKey from dbc.dbcinfo"
    sql4 = "select count(*) from dbc.dbcinf"
    
    save_results_instance = tdtestpy.SaveSQLResults (db_con = db_connect, output_file = save_result_output)
    # Clean up test database before start unit testing just in case it failed prior run 
    dbc_instance.drop_user("tdtestpy_unit_test")   

    #http://stackoverflow.com/questions/1029891/python-unittest-is-there-a-way-to-pass-command-line-options-to-the-app
    sys.argv[1:] = args.unittest_args
    unittest.main()