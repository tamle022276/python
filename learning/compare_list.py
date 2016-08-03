#http://stackoverflow.com/questions/12661999/get-raw-decimal-value-from-mysqldb-query

#!/usr/bin/env python
import sys
import re
import MySQLdb
import logging
import traceback
from decimal import *
from difflib import get_close_matches

DATABASE = ('localhost', 'root', 'Du0ng$83O3', 'apennyle_load')

def compare_db_results():
    """
    Fetch db results for TABLE1, TABLE2 and compare rows.
    @param db: data base object
    """
    # prepare a cursor object using cursor() method
    db = MySQLdb.connect(*DATABASE)
    cursor = db.cursor()
    # Execute the SQL(table1) and fetch all the rows in a list of lists
    cursor.execute("select * from apennyle_penny.table1")
    array1 = list(cursor.fetchall())
    print (array1)
    len1 = len(array1)
    print (len1)
    cursor.execute("select * from apennyle_penny.table2 order by x1 desc")
    #array2 = list(cursor.fetchall())
    #array2 = [(6L, '1000', 1000L, 20000001L, 11000L, 50.00), (5L, '11000', 11000L, 20000001L, 11000L, 50.00), (4L, '11000', 11000L, 20000001L, 11000L, 4.50), (3L, '11000', 11000L, 20000001L, 11000L, 3.78), (2L, '11000', 11000L, 20000001L, 11000L, 2.45), (1L, 'ABCDe', 11000L, 20000001L, 11000L, 10.40)]
    array2 = [(2L, '11000', 11000L, 20000001L, 11000L, Decimal('2.45')), (3L, '11000', 11000L, 20000001L, 11000L, Decimal('3.78')), (4L, '11000', 11000L, 20000001L, 11000L, Decimal('4.50')), (5L, '11000', 11000L, 20000001L, 11000L, Decimal('50.00')), (6L, '1000', 1000L, 20000001L, 11000L, Decimal('50.00'))]
    print (array2)
    len2 = len(array2)
    print (len2)

    if len1 != len2:
        print "Length of tables are not the same!!!"
        exit(1)

    # Body, compare results
    all_match = True
    cutoff = 1  # matching score value(exact match)
    while array1:
        i = 0
        while i < len(array1):
            # Match most corresponding element from array2
            match_list = get_close_matches(array1[i], array2, cutoff=cutoff)
            if match_list:
                if cutoff < 1:  # If no exact match, it is fail
                    print "Row not match is; from sql1 %s, and sql2 %s" % (array1[i], match_list[0])
                del array1[i]
                array2.remove(match_list[0])
            else:
                # becomes false earlier, then corresponding array2 elem is finding
                all_match = False
                i += 1
        cutoff -= 0.1  # increase by 10%
        print (cutoff)
        if cutoff < 0:
            print "Length of tables are not the same!!!"
            return

    if all_match:
        print "All match"


def compare_db_results(db):
    """
    Fetch db results for TABLE1, TABLE2 and compare rows.
    @param db: data base object
    """
    # prepare a cursor object using cursor() method
    cursor = db.cursor()
    # Execute the SQL(table1) and fetch all the rows in a list of lists
    cursor.execute("SELECT * FROM table1")
    array1 = list(cursor.fetchall())
    cursor.execute("SELECT * FROM table2")
    array2 = list(cursor.fetchall())

    # Body, compare results
    all_match = True
    if len(array1) != len(array2):
        print "Length of tables are not the same!!!"
        exit(1)
    else:
        for rowA in array1:
            # get rowB from array2 with same primary key as for rowA
            rowB = next((row for row in array2 if row[0] == rowA[0]), None)
            if rowB is None:
                print "there is no row in second table with primary key %s" % rowA[0]
                all_match = False
            elif rowA != rowB:
                print "Row not match is; from sql1 %s, and sql2 %s" % (rowA, rowB)
                all_match = False
    if all_match:
        print "All match"
        exit(0)
    exit(1)


if __name__ == "__main__":
    logging.basicConfig(filename="compare.log", format='%(asctime)-15s %(levelname)s: %(message)s', level=logging.DEBUG)

    try:
        compare_db_results()
    except MySQLdb.MySQLError as e:
        logging.error("Mysql Error happend: %s", e)
        logging.error(traceback.format_exc())
    except IOError as e:
        logging.error(e)
        logging.error(traceback.format_exc())



