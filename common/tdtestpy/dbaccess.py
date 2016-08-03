"""
This is common module that use to access to the Teradata database and execute queries.
Date Published: 05/15/2016
Contributors: tl151006 (tl151006@teradata.com)
"""

import logging
import pickle
import time
import os

class DBSaccess (object):
    """
    This class help access to the database and run common queries.

    Args:
        db_con (str): This is the connection string login to the database.

    Example Creating an Instance:
        db_con = udaExec.connect(method="odbc", system="my_db", username= "abc", password="abc")
        my_db_access = tdtestpy.DBSaccess (dbc_con)

    Example Running Method After Instance Created:
        my_db_access.drop_user (target_user)

    Available Methods:
        drop_user
        get_db_free_perm
        get_db_current_perm
        get_db_max_perm
        get_table_current_perm
        get_table_row_count
        get_sum_of_a_column
        is_database_exist
        get_num_vprocs
        get_pde_release
        get_dbs_release
    """
    def __init__(self, db_con):
        """
        db_con (str): This is the connection string login to the database.

        """
        self.db_con = db_con
          
    # Drop user(s) or database(s) with and without join indexes, return True if no error occurred.
    def drop_user(self, target_user):
        """
        This method will drop join indexes, end query logging and drop user.
 
        Args:
            target_user (str): User that need to be drop

        Returns:
            True if target_user exist and drop successful, False otherwise.

        Raises:
            Raising exception

        """

        try:
            with self.db_con.cursor() as cursor:
                cursor.execute("select UserName from dbc.users where UserName = '%s'" % (target_user))
                user_list = [item[0] for item in cursor.fetchall()]
                if len(user_list) == 0:
                    logging.info ("Database/user %s name does not exist" % (target_user))
                    return False
                else:
                    #for user_name in user_list:
                    
                    cursor.execute("release lock %s, override" % (target_user), ignoreErrors=[2631])
                    # Get all join indexes and drop them first
                    cursor.execute("select distinct JoinIdxName from dbc.JoinIndicesV where DataBaseName = \
                                    '%s'" % (target_user))
                    indexes_list = [item[0] for item in cursor.fetchall()]
                    for index_name in indexes_list:
                        cursor.execute("drop join index %s.%s" % (target_user, index_name), ignoreErrors=[2631])          
                
                    cursor.execute("SELECT AbortSessions (1, '%s', 0, 'Y', 'Y')" % (target_user))
                    # Ignore 9262 Cannot END QUERY LOGGING as no rule exists and datanase does not exist
                    cursor.execute("end query logging on %s" % (target_user), ignoreErrors=[9262, 3802])
                    cursor.execute("delete user %s" % (target_user), ignoreErrors=[2631])
                    cursor.execute("drop user %s" % (target_user), ignoreErrors=[2631])
            return True
        except Exception as e:
            raise
        
    # Get free perm space of user or database and return it to user.
    def get_db_free_perm(self, target_user):
        """
        Get free perm space of a user or database

        Args:
            target_user (str): User that need to check free perm space

        Returns:
            Free perm (int) if target_user exist, otherwise return message "target_user does not exist"

        Raises:
            Raising exception

        """

        try:
            with self.db_con.cursor() as cursor:
                cursor.execute("select CAST(sum(maxperm) as bigint) - CAST(max(currentperm) * (HASHAMP()+1) as bigint) from dbc.diskspace \
                                where  databasename = '%s' group by databasename" % (target_user))
                
                res = cursor.fetchone()
                if res is not None:
                    free_perm = res[0]
                    return free_perm
                else:
                    msg = target_user + " does not exist"
                    return msg
        except Exception as e:
            raise
        
    # Get currentperm of a database includes wasted perm due to skew in the dbc.diskspace, cast it to bigint.
    def get_db_current_perm(self, target_user):
        """
        Get current perm space of a user or database

        Args:
            target_user (str): User that need to check for current perm

        Returns:
            Current perm (int) if target_user exist, otherwise return message "target_user does not exist"

        Raises:
            Raising exception

        """

        try:
            with self.db_con.cursor() as cursor:
                cursor.execute("select CAST(max(currentperm) * (HASHAMP()+1) as bigint) from dbc.diskspace \
                                where  databasename = '%s' group by databasename" % (target_user))
                res = cursor.fetchone()
                if res is not None:
                    current_perm = res[0]
                    return current_perm
                else:
                    msg = target_user + " does not exist"
                    return msg
        except Exception as e:
            raise
 
    # Get maxperm of a database in the dbc.diskspace cast it to bigint.
    def get_db_max_perm(self, target_user):
        """
        Get max perm space of a user or database

        Args:
            target_user (str): User that need to check for max perm

        Returns:
            Max perm (int) if target_user exist, otherwise return message "target_user does not exist"

        Raises:
            Raising exception
        """

        try:
            with self.db_con.cursor() as cursor:
                cursor.execute("select CAST(sum(maxperm) as bigint) from dbc.diskspace \
                                where  databasename = '%s' group by databasename" % (target_user))
                res = cursor.fetchone()
                if res is not None:
                    max_perm = res[0]
                    return max_perm
                else:
                    msg = target_user + " does not exist"
                    return msg
        except Exception as e:
            raise
            
    # Get current perm of a table includes wasted perm due to skew, covert it to bigint.
    def get_table_current_perm(self, target_user, target_table):
        """
        Get current perm of a table

        Args:
            target_user (str): User name that table belong to
            target_table (str): Table that need to check for current perm

        Returns:
            Table current perm (int) if successful, otherwise message "target_user.target_table is invalid table"

        Raises:
            Raising exception
        """

        try:
            with self.db_con.cursor() as cursor:
                cursor.execute("select CAST(max(currentperm) * (HASHAMP()+1) as bigint) from DBC.TABLESIZE \
                                where DATABASENAME = '%s' and TABLENAME = '%s'" % (target_user, target_table))
                res = cursor.fetchone()
                if res[0] is not None:
                    return res[0]
                else:
                    msg = target_user + "." + target_table + " is invalid table"
                    return msg
        except Exception as e:
            raise
 
    # Get row count of a table.
    def get_table_row_count(self, target_user, target_table):
        """
        Get row count of a table

        Args:
            target_user (str): User name that table belong to
            target_table (str): Table that need to check for row count

        Returns:
            Row count (int) if table exist, otherwise error 3807 "table does not exist" will raise

        Raises:
            Raising exception
        """

        try:
            with self.db_con.cursor() as cursor:
                cursor.execute("select count(*) from %s.%s" % (target_user, target_table))
                res = cursor.fetchone()
                return res[0]
        except Exception as e:
            raise

    # Get sum of a column from a table, cast it to decimal(38,2) to avoid numeric over flow.
    def get_sum_of_a_column(self, target_user, target_table, target_column):
        """
        Get sum of a table column

        Args:
            target_user (str): User name that table belong to
            target_table (str): Table that column belong to
            target_column (str): Column that need to get sum of.

        Returns:
            Sum of a column (int) if column exist, otherwise error 5628 "Column not found" will raise

        Raises:
            Raising exception when column, table, or database does not exist.
        """

        try:
            with self.db_con.cursor() as cursor:
                cursor.execute("select sum(cast(%s as decimal(38,2))) (FORMAT 'zzzzzzzzzzzzzzzzzzzzzzzzzz9.99') \
                                from %s.%s" % (target_column, target_user, target_table))
                res = cursor.fetchone()
                return res[0]
        except Exception as e:
            raise
 
    # Check to see if database is exist in dbc.Databases, return True if exist, else return False
    def is_database_exist(self, target_user):
        """
        Check see if a database or user exist in the database

        Args:
            target_user (str): User that need to check

        Returns:
            True if target_user exist, False otherwise.

        Raises:
            Raising exception

        """

        try:
            with self.db_con.cursor() as cursor:
                cursor.execute("select count(*) from dbc.Databases where DatabaseName = '%s'" % (target_user))
                res = cursor.fetchone()
                check_pdm = int(res[0])
                if check_pdm != 0: 
                    return True
                else:
                    return False
        except Exception as e:
            raise
        
    # Get number of vprocs or amps of a system.
    def get_num_vprocs(self):
        """
        Get number of vprocs of a teradata system

        Returns:
            Number of vprocs (int) if method ran successful, otherwise raise error.

        Raises:
            Raising exception
        """

        try:
            with self.db_con.cursor() as cursor:
                cursor.execute("sel hashamp()+1")
                res = cursor.fetchone()
                return res[0]
        except Exception as e:
            raise
    
    # Get PDE Release of the database.
    def get_pde_release(self):
        """
        Get current running version of Teradata PDE

        Returns:
            PDE version (str) if method ran successful, otherwise raise error.

        Raises:
            Raising exception
        """

        try:
            with self.db_con.cursor() as cursor:
                cursor.execute("select InfoData from dbc.dbcinfo where InfoKey = 'VERSION'")
                res = cursor.fetchone()
                return res[0]
        except Exception as e:
            raise

   
    # Get DBS Release of the database.
    def get_dbs_release(self):
        """
        Get current running version of Teradata DBS

        Returns:
            DBS version (str) if method ran successful, otherwise raise error.

        Raises:
            Raising exception
        """

        try:
            with self.db_con.cursor() as cursor:
                cursor.execute("select InfoData from dbc.dbcinfo where InfoKey = 'RELEASE'")
                res = cursor.fetchone()
                return res[0]
        except Exception as e:
            raise
 
# Function Name: SQLValidation
# Purpose: Compare 2 values and return True if match, else return False

class SQLValidation (object):
    """
    This class help stored, retrieved sql results to/from control file and compare with new results.

    Args:
        db_con (str): This is the connection string login to the database.
        controlfile (str): Name of the control file
        send_fail_output_to (Optional[str]): File name to write debug info to in case validate failed

    Example Creating an Instance:
        db_con = udaExec.connect(method="odbc", system="my_db", username= "abc", password="abc")
        controlfile = "my_control_file.pickle"
        send_fail_output_to = "/tmp/validate_fail_debug.log"
        validate_job = tdtestpy.SQLValidation (db_con, controlfile, send_fail_output_to)

    Example Running Method After Instance Created:
        my_db_access.drop_user (target_user)
        validate_job.validate_sql_results (sql, original_result)

    Available Methods:
        validate_sql_results
        create_control_file
        load_control_file
    """

    def __init__(self, db_con, controlfile, send_fail_output_to=None):
        self.db_con = db_con
        self.controlfile = controlfile
        self.send_fail_output_to = send_fail_output_to
                  
    def validate_sql_results (self, sql, expected_result):
        """
        Get sql results from current run, retrieved original results from control file and compare the two.

        Args:
            sql (str): sql that need to compare results with original results
            expected_result (List[str]): Original results in a list file. 

        Returns:
            True if both results match, otherwise return False

        Raises:
            Raising exception
        """

        if type(expected_result) is not list:
            logging.error ("Expected result must be in list format")
            return False
        try:
            with self.db_con.cursor() as cursor:
                cursor.execute(sql)
                actual_results = []
                for row in cursor:
                    newrow = (", ".join([str(self.ordered(col)) for col in row]))
                    actual_results.append(newrow)         
        except Exception as e:
                raise
            
        result1 = sorted(actual_results)
        result2 = sorted(expected_result)
    
        if len(result1) != len(result2):
            if self.send_fail_output_to is not None:
                logging.error (("Rows count of two results are not the same, check out log here %s" % (self.send_fail_output_to)))
                with open(self.send_fail_output_to, 'a', encoding='utf-8', errors='ignore') as f:
                    f.write("################ Rows count of two results are not the same ###################\n") 
                    f.write("Here is the sql...\n")
                    f.write(sql + "\n")
                    f.write("*************** Actual Results has %s rows ***************\n" % (len(result1)))
                    for r in result1:
                        f.write(r + "\n")
                    f.write("*************** Expected Results has %s rows ***************\n" % (len(result2)))
                    for r in result2:
                        f.write(r + "\n")
                    f.write("################################################################################\n\n\n\n\n")  
            else:
                logging.error ("Rows count of two results are not the same!!!")
                logging.info ("*************** Actual Results has %s rows ***************" % (len(result1)))
                logging.info ("*************** Expected Results has %s rows ***************" % (len(result2)))
            return False
        else:
            for rowA, rowB in zip(result1, result2):
                if rowA != rowB:
                    if self.send_fail_output_to is not None:
                        logging.error (("Row found mismatch, check out log here %s" % (self.send_fail_output_to)))
                        with open(self.send_fail_output_to, 'a', encoding='utf-8', errors='ignore') as f:
                            f.write("################################ Row found mismatch ################################\n")
                            f.write("Here is the sql...\n")
                            f.write(sql + "\n")
                            f.write("Row from Actual Results  : %s \n" % (rowA))
                            f.write("Row from Expected Results: %s \n" % (rowB))
                            f.write("################## ALL rows from Actual Results #######################\n") 
                            for r in result1:
                                f.write(r + "\n")
                            f.write("################## ALL rows from Expected Results #######################\n") 
                            for r in result2:
                                f.write(r + "\n")
                            f.write("################################################################################\n\n\n\n\n") 
                    else:
                        logging.error ("Row found mismatch")
                        print ("Row from Actual Results %s" % (rowA))
                        print ("Row from Expected Results %s" % (rowB))
                    return False            
        return True
    
    def create_control_file (self, sql, sql_name):
        """
        Capture original sql results and stored it in the control file.

        Args:
            sql (str): sql that need to stored results in control file
            sql_name (str): A unique name for above sql.
        
        Returns:
            True if control file created successful, otherwise raise exception
            
        Raises:
            Raising exception
        """

        try:
            with self.db_con.cursor() as cursor:
                cursor.execute(sql)
                original_results = []
                for row in cursor:
                    newrow = (", ".join([str(self.ordered(col)) for col in row]))
                    original_results.append(newrow)         
         
            sqlresults = {}
            sqlresults[sql_name] = original_results
            with open (self.controlfile, mode='ab') as f:
                pickle.dump(sqlresults, f)
                return True
            return False
        
        except Exception as e:
                raise
            
    def load_control_file (self):
        """
        Retrieved all sql results from control file and load them in the dictionary

        Returns:
            Dictionary with all results set.

        Raises:
            Raising exception
        """

        with open (self.controlfile, mode='rb') as f:
            allresults = {}
            while True:
                try:
                    allresults.update(pickle.load(f))
                except EOFError:
                    break
        return allresults
                                                      
                
    def ordered(self, obj):
        """
        Put the dictionary, json elements in order from a-z

        Returns:
            ordered dictionary, json

        Raises:
            Raising exception
        """

        if isinstance(obj, dict):
            return sorted((k, self.ordered(v)) for k, v in obj.items())
        if isinstance(obj, list):
            return sorted(self.ordered(x) for x in obj)
        else:
            return obj

# Function Name: SaveSQLResults
# Purpose: Print sql results set to a file

class SaveSQLResults (object):
    """
    Get sql results and save it to a file with user preferences

    Args:
        db_con (str): This is the connection string login to the database.
        output_file (str): Name if file to save results
        ignore_errors (Optional[list]): Ignored errors list
        delimiter (Optional[str]): Columns separate by this delimiter, default is comma
        data_only (Optional[str]): Save data only with no columns header
        retlimit (Optional[int]): max number of rows will be save per each sql.


    Example Creating an Instance:
        db_con = udaExec.connect(method="odbc", system="my_db", username= "abc", password="abc")
        output_file = "my_results.txt"
        ignore_errors = [2631, 3807] 
        delimiter = "|"
        data_only = "true"
        retlimit = 100

        my_sql_results = tdtestpy.SaveSQLResults (db_con, output_file, ignore_errors, delimiter, data_only, retlimit)

    Example Running Single SQL Method After Instance Created:
        sql = "select * from dbc.dbcinfo"
        my_sql_results.run_my_sql (sql)
    
    Example Running SQL File Method After Instance Created:
        sql_file = "queries.txt"
        my_sql_results.run_my_file (sql_file)
    """

    def __init__(self, db_con, output_file, ignore_errors = [0], delimiter = ',', data_only = False, retlimit = 0):
        self.db_con = db_con
        self.output_file = output_file
        self.ignore_errors = ignore_errors
        self.delimiter = delimiter
        self.retlimit = retlimit
        
        if data_only is True:
            self.data_only = True
        elif data_only is False:
            self.data_only = False
        else:    
            if data_only.lower() == "true":
                self.data_only = True
            elif data_only.lower() == "false":
                self.data_only = False
            else:
                logging.error ("data_only must be True or False, you input: %s" % (data_only))
                exit(1)
                  
    def run_sql (self, sql):
        """
        Run sql, capture results set and save it to a file

        Args:
            sql (str): sql that need to save results to a file

        Returns:
            True if successful, otherwise False

        Raises:
            Raising exception

        """
        try:
            start_time = time.time()
            with self.db_con.cursor() as cursor:
                
                cursor.execute (sql, ignoreErrors = self.ignore_errors)
                elapsed_time = time.time() - start_time
                num_row = cursor.rowcount
                columns_description = cursor.description
                if self.retlimit == 0:
                    results = cursor.fetchall()
                else:
                    results = cursor.fetchmany(self.retlimit)

                logging.error (columns_description)
                logging.error (num_row)
                
                # If sql return error that in ignore list
                if columns_description is None:
                    with open(self.output_file, 'a') as f:
                        f.write(sql + "\n")
                        f.write(" *** Query Failed, error returns found in ignored list %s \n" % (self.ignore_errors))
                        f.write(" *** Total elapsed time was %.3f seconds.\n" % (elapsed_time,))
                        f.write("--------------------------------------------------------------------------------\n")
                        f.write("\n\n\n")
                else:          
                    with open(self.output_file, 'a') as f:
                        num_col = len(columns_description)
                        
                        if self.data_only:
                            for row in results:
                                f.write(self.delimiter.join([str(c) for c in row]) + "\n")  # every record of table, e.g: f1, f2, f3
                        else:
                            f.write(sql + "\n")
                            if num_row == 0:
                                f.write(" *** Query completed. No rows found.\n")
                                f.write(" *** Total elapsed time was %.3f seconds.\n" % (elapsed_time,))
                                f.write("--------------------------------------------------------------------------------\n")
                            else:
                                f.write(" *** Query completed. %s rows found. %s columns returned.\n" % (num_row, num_col))
                                f.write(" *** Total elapsed time was %.3f seconds.\n" % (elapsed_time,))
                                f.write("--------------------------------------------------------------------------------\n")
                                f.write("| ".join([i[0] for i in columns_description]) + "\n")  # column header, index[0] is column name
                                for row in results:
                                    f.write(self.delimiter.join([str(c) for c in row]) + "\n")  # every record of table, e.g: f1, f2, f3
                                if self.retlimit != 0 and self.retlimit < num_row:
                                    f.write(" *** Warning: RetLimit exceeded, query returns %s rows, but showing %s rows." % (num_row, self.retlimit))
                            f.write("\n\n\n")
                return True
                       
        except Exception as e:
            with open(self.output_file, 'a') as f:
                elapsed_time = time.time() - start_time
                f.write(sql + "\n")
                f.write(" *** Query failed with error: " + str(e) + "\n")
                f.write(" *** Total elapsed time was %.3f seconds.\n" % (elapsed_time,))
                f.write("--------------------------------------------------------------------------------\n")
            return False
            #raise
    
    def run_file (self, sql_file):
        """
        Run sql, capture results set and save it to a file

        Args:
            sql_file (str): A file that contains many queries separate by semicolon (;)

        Returns:
            True if each sql from file successful, otherwise False

        Raises:
            Raising exception

        """
        try:
               
            read_file = open(sql_file, 'r')
            all_queries = read_file.read()
            read_file.close()
            
            #removed all blank line
            all_queries = os.linesep.join([s for s in all_queries.splitlines() if s])

            #removed last semicolon
            if all_queries[-1] == ";":
                all_queries = all_queries[:-1]

            
            with self.db_con.cursor() as cursor:
                sqlcommands = all_queries.split(';')
                for sql in sqlcommands:
                    start_time = time.time()
                    cursor.execute (sql.strip(), ignoreErrors = self.ignore_errors)
                    elapsed_time = time.time() - start_time
                    num_row = cursor.rowcount
                    columns_description = cursor.description
                    if self.retlimit == 0:
                        results = cursor.fetchall()
                    else:
                        results = cursor.fetchmany(self.retlimit)
                    
                    # If sql return error that in ignore list
                    if columns_description is None:
                        with open(self.output_file, 'a') as f:
                            f.write(sql + "\n")
                            f.write(" *** Query Failed, error returns found in ignored list %s \n" % (self.ignore_errors))
                            f.write(" *** Total elapsed time was %.3f seconds.\n" % (elapsed_time,))
                            f.write("--------------------------------------------------------------------------------\n")
                            f.write("\n\n\n")
                    else:   
                        num_col = len(columns_description)
                        with open(self.output_file, 'a') as f:
                            if self.data_only:
                                for row in results:
                                    f.write(self.delimiter.join([str(c) for c in row]) + "\n")  # every record of table, e.g: f1, f2, f3
                            else:
                                f.write(sql + "\n")
                                if num_row == 0:
                                    f.write(" *** Query completed. No rows found.\n")
                                    f.write(" *** Total elapsed time was %.3f seconds.\n" % (elapsed_time,))
                                    f.write("--------------------------------------------------------------------------------\n")
                                else:
                                    f.write(" *** Query completed. %s rows found. %s columns returned.\n" % (num_row, num_col))
                                    f.write(" *** Total elapsed time was %.3f seconds.\n" % (elapsed_time,))
                                    f.write("--------------------------------------------------------------------------------\n")
                                    f.write("| ".join([i[0] for i in columns_description]) + "\n")  # column header, index[0] is column name
                                    for row in results:
                                        f.write(self.delimiter.join([str(c) for c in row]) + "\n")  # every record of table, e.g: f1, f2, f3
                                    if self.retlimit != 0 and self.retlimit < num_row:
                                        f.write(" *** Warning: RetLimit exceeded, query returns %s rows, but showing %s rows." % (num_row, self.retlimit))
                                f.write("\n\n\n") 
                return True                     
        except Exception as e:
            with open(self.output_file, 'a') as f:
                elapsed_time = time.time() - start_time
                f.write(sql.strip() + "\n")
                f.write(" *** Query failed with error: " + str(e) + "\n")
                f.write(" *** Total elapsed time was %.3f seconds.\n" % (elapsed_time,))
                f.write("--------------------------------------------------------------------------------\n")
                return False
                #raise
