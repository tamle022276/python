# File: jenkins_scan.py
# Author: Tam Le
# Author Email: tam.le@teradata.com
# Date Published: 02/05/2015
# Purpose: This program is running scan log files
# Usage: python jenkins_scan.py
import sys
import os
import errno
import traceback
import logging
import getpass
import platform

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

log_name = "jenkins_scan_python.log"
logging.basicConfig(filename=log_name, format='%(asctime)-15s %(levelname)s: %(message)s', level=logging.DEBUG)


# Python exit wrapper function
def exit(ok=True):
    if ok is True or ok == 0:
        logging.info("================= End: [Jenkins Build Passed] =================")
        sys.exit(0)
    else:
        logging.info("================== End: [Jenkins Build Failed, See Logs Above] ==================")
        sys.exit(1)


if __name__ == "__main__":

    try:

        path_of_error_logs = os.path.join(python_src, '*.log')

        # Scan jenkins build logs using common scan_files_extension function
        if not uda2c.scan_files_extension(path_of_error_logs, "Jmeter test failed"):
            exit(1)
        else:
            exit(0)

    except Exception as e:
        logging.error(traceback.format_exc())
        exit(1)

    exit(0)
