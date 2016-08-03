"""
This is common module to access the node via paramiko ssh and run any command lines
Date Published: 05/15/2016
Contributors: tl151006 (tl151006@teradata.com)
"""
import sys
import os
import logging
import socket
import platform
from .osutilities import scan_a_file
os_type = platform.system()
if os_type == "Linux":
    import paramiko

class DataCheck (object):
    """
    Connect to the PDN node using ssh and run scandisk or/and checktable

    Args:
        dbs_name (str): Name of Teradata database system
        root_password (str): PDN root password

    Example Creating an Instance:
        dbs_name = "prune"
        root_password = "whatever"

        datacheck_instance = tdtestpy.DataCheck (dbs_name, root_password) 

    Example Running Method After Instance Created:
        check_database_name = "dbc"
        check_table_name = "none" 
        check_level = "two"
        checktable_log = "prune>checktable.log"

        datacheck_instance.checktable (check_database_name, check_table_name, check_level, checktable_log):

    Available Methods:
        get_ip_address
        get_ssh_connect
        scandisk
        checktable
    """
    def __init__(self, dbs_name, root_password):
        self.dbs_name = dbs_name
        self.root_password = root_password
    # Purpose: Get IP Address of a node
    def get_ip_address (self):
        """
        Get IP address of the PDN node

        Returns:
            ip_address if connection successful or socket error if can't established connection.
        """

        dbs_name = self.dbs_name
        if 'cop1' in dbs_name:
            pdn_node = dbs_name
        # Any Ip address always has 3 periods
        elif dbs_name.count('.') == 3:
            pdn_node = dbs_name
        else:
            pdn_node = dbs_name + "cop1"
        # Now check see if ip_address is pingable
        response = os.system("ping -c 1 " + pdn_node)
        if response == 0:
            ip_address = socket.gethostbyname(pdn_node)
            return ip_address
        else:
            logging.error ("your dbs_name: %s is not pingable" % (dbs_name))
            exit (1)
            
    # Establish SSH connection
    def get_ssh_connect (self):
        """
        Get ssh connection with corrected root password

        Returns:
            ssh connection string if connection successful or socket error if can't established connection.
        """

        dbs_name = self.dbs_name
        root_password = self.root_password
        try:
            hostname = self.get_ip_address()
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.load_system_host_keys()
            ssh.connect(hostname=hostname, username="root", password=root_password)
            return ssh
        except Exception as e:
            raise    

    # Purpose: Run scandisk and return True if no error, else return False
    def scandisk (self, db_conn, output):
        """
        Run scandisk from PDN node.

        Args:
            db_conn (str): This is the connection string login to the database.
            output (str): Scandisk output will save under

        Returns:
            True if all vprocs responded with no messages or errors, otherwise return False
        """

        ssh = self.get_ssh_connect()
        
        command = '/usr/pde/bin/cnsrun -utility filer -commands "{enable script} {scandisk} {yes} {quit} " -debug 3 -force -multi'
                
        with db_conn.cursor() as cursor:
                cursor.execute("sel hashamp()+1")
                res = cursor.fetchone()
                num_vprocs = res[0]
        
        scanpass = str(num_vprocs) + " of " + str(num_vprocs) + " vprocs responded with no messages or errors"
    
        logging.info ("scandisk started")
        stdin, stdout, stderr = ssh.exec_command(command)
        # block until remote command completes
        status = stdout.channel.recv_exit_status()
        # status 0 completed
        logging.info ("scandisk completed")
        #http://stackoverflow.com/questions/10019456/usage-of-sys-stdout-flush-method
        sys.stdout.flush()
        # write stdout to the log
        with open(output,'wb') as data_check_out:
            for line in stdout.read().splitlines():
                data_check_out.write(line + "\n".encode('ascii'))
    
        if scan_a_file(output, scanpass):
            return True
        return False

    # Purpose: Run checktables and return True if no error, else return False
    def checktable (self, DatabaseName, TableName, CheckLevel, output):
        """
        Run checktable from PDN node.

        Args:
            DatabaseName (str): Name of the database to check, if "none" then check entire system.
            TableName (str): Name of a table to check, if "none" then check entire DatabaseName.
            CheckLevel (str): Checktable level
            output (str): Checktable output will save under

        Returns:
            True if 0 table(s) failed the check., otherwise return False
        """

        ssh = self.get_ssh_connect()
        
        if DatabaseName != 'none' and TableName == 'none':
            command = '/usr/pde/bin/cnsrun -utility checktableb -prompt "Enter a command, \\"QUIT;\\" or \\"HELP;\\"" \
                   -commands "{check ' + DatabaseName + ' at level ' + CheckLevel + ';} {quit;} " -debug  5 -force -multi'
        elif DatabaseName != 'none' and TableName != 'none':
            if type(TableName) is tuple:
                check_multiple_tables = (", ".join(DatabaseName + '.' + t for t in TableName))
                command = '/usr/pde/bin/cnsrun -utility checktableb -prompt "Enter a command, \\"QUIT;\\" or \\"HELP;\\"" \
                   -commands "{check ' + check_multiple_tables + ' at level ' + CheckLevel + ';} {quit;} " -debug  5 -force -multi'
            else:
                command = '/usr/pde/bin/cnsrun -utility checktableb -prompt "Enter a command, \\"QUIT;\\" or \\"HELP;\\"" \
                       -commands "{check ' + DatabaseName + '.' + TableName + ' at level ' + CheckLevel + ';} {quit;} " -debug  5 -force -multi'
        elif DatabaseName == 'none' and TableName == 'none':
            command = '/usr/pde/bin/cnsrun -utility checktableb -prompt "Enter a command, \\"QUIT;\\" or \\"HELP;\\"" \
                   -commands "{check all tables at level ' + CheckLevel + ';} {quit;} " -debug  5 -force -multi'
        else:
            logging.error ("Your input DatabaseName = %s, TableName = %s are invalid combo" % (DatabaseName, TableName))
            exit(1)
    
        checkpass = "0 table\(s\) failed the check."
    
        logging.info ("checktable started")
        stdin, stdout, stderr = ssh.exec_command(command)
        # block until remote command completes
        status = stdout.channel.recv_exit_status()
        # status 0 completed
        logging.info ("checktable completed")
        #http://stackoverflow.com/questions/10019456/usage-of-sys-stdout-flush-method
        sys.stdout.flush()
        # write stdout to the log
        with open(output,'wb') as data_check_out:
            for line in stdout.read().splitlines():
                data_check_out.write(line.strip() + "\n".encode('ascii'))
    
        if scan_a_file(output, checkpass):
            return True
        return False
