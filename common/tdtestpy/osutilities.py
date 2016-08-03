"""
This is common module that run os utilities to create, remove, compare, search for files.
Date Published: 05/15/2016
Contributors: tl151006 (tl151006@teradata.com)
"""
import os
import errno
import re
import logging
import shutil
import glob
import tarfile


def scan_a_file(file_name, what_to_scan):
    """
    Search for a specific string from a file

    Args:
        file_name (str): Name of the file to search
        what_to_scan (str): What string to search for

    Returns:
        True if string match, otherwise False

    Raises:
        Raising exception
    """
    with open(file_name, 'r') as log_f:
        if '(' in what_to_scan:
            for line in log_f:
                if re.match(what_to_scan, line):
                    return True
        else:       
            for line in log_f.readlines():
                if re.search(r"\b(?=\w)%s\b(?!\w)" % (what_to_scan), line):
                    return True
    return False

def get_property_value (file_name, prop_name):
    """
    Search jmeter properties file for property name and return property value

    Args:
        file_name (str): Properties file name to search
        prop_name (str): Property name that need to search for value

    Returns:
        Property value if property name exists, otherwise return error and exit 1

    Raises:
        Raising exception
    """
    try:
        with open(file_name, 'r') as f:
            for line in f:
                if prop_name in line:
                    prop_value = line.split(":", 1)[1]
                    return prop_value.strip()
        logging.error("There is no property name: %s in file: %s" % (prop_name, file_name))
        exit(1)                
    except Exception as e:
        logging.error(traceback.format_exc())
        exit(1)
        
def scan_files_extension(path_with_extension, what_to_scan):
    """
    Scan specific string from all files in the same directory ending with specific extension

    Args:
        path_with_extension (str): Directory path with extension (e.g: /tmp/*.log)
        what_to_scan (str): A string that need to be scan for

    Returns:
        True if string match, otherwise False

    Raises:
        Raising exception
    """
    files = glob.glob(path_with_extension)
    for fname in files:
        try:
            with open(fname) as f:
               for line in f:
                  if what_to_scan in line:
                      print ("Message found: %s" % (line))
                      print ("File Name: %s" % (fname))
                      return True
        except IOError as exc:
            if exc.errno != errno.EISDIR: # Do not fail if a directory is found, just ignore it.
                raise # Propagate other kinds of IOError.
    return False

def tarfile_archive (archive_name, archive_dir):
    """
    Archive a directory in tar ball, all files and sub directory.

    Args:
        archive_name (str): Tar ball name
        archive_dir (str): Name of the directory that need to be archive

    Returns:
        True if archive successful, error if failed.

    Raises:
        Raising exception
    """
    # Run "gunzip -c foo.tar.gz | tar xopf -" to untar
    if os.path.isdir(archive_dir):
        try:
           with tarfile.open(archive_name + '.tar.gz', mode='w:gz') as archive:
               archive.add(archive_dir, recursive=True)
        except Exception as e:
            raise
    return True

def convert_a_template(input_template, output_template, new_items):
    """
    Convert original file to a new file with new items in the dictionary

    Args:
        input_template (str): Original file that need to convert
        output_template (str): Name of new file after conversion
        new_items (dict[str]) or (str): All items in dictionary format that need to be replace or new string need to add

    Returns:
        True if successful, otherwise False

    Raises:
        Raising exception
    """
    # If dictionary then replace old items with new items
    if isinstance(new_items, dict):
        need_replace_items = new_items
        with open(input_template) as infile, open(output_template, 'w') as outfile:
            for line in infile:
                for src, target in need_replace_items.items():
                    line = line.replace(src, target)
                outfile.write(line)
        return True
    # If string then add new items at the end of new file.           
    elif isinstance(new_items, str):
        with open(input_template) as infile, open(output_template, 'w') as outfile:
            for line in infile:
                outfile.write(line)
            outfile.write("\n")
            outfile.write(new_items)
        return True
    else:
        logging.error ("new_items must be in dictionary or string format")
        return False
            
def get_full_line_if_string_match(file_name, what_to_scan):
    """
    Get a completed line if portion of a string found in the line

    Args:
        file_name (str): Name of the file need to be search
        what_to_scan (str): Portion of a string need to search in the line

    Returns:
        Completed line if portion of a string found, otherwise False

    Raises:
        Raising exception
    """

    with open(file_name, 'r') as log_f:
        for line in log_f:
            if what_to_scan in line:
                return line.strip()
    return False

def get_ignore_errors(ignore_errors):
    """
    Convert Bteq ignore errors in a string separate by comma to a list format

    Args:
        ignore_errors (str): All ignore errors in string separate by comma

    Returns:
        List with ignore errors, otherwise exception error

    Raises:
        Raising exception
    """

    return [int(e.strip()) for e in ignore_errors.split(",") if e.strip()]

def ensure_dir(dirname):
    """
    Create a directory if it does not exist, ignore if it already exist

    Args:
        dirname (str): Name of the directory need to be create

    Returns:
        True if successful, otherwise False

    Raises:
        Raising exception
    """
    try:
        os.makedirs(dirname)
    except OSError as e:
        if e.errno == errno.EEXIST:
            return
        raise e

def delete_one_file(name_of_file_with_path):
    """
    Delete a file name with or without full path, ignore if it does not exist

    Args:
        name_of_file_with_path (str): File name that need to be delete

    Returns:
        True if successful, error if exception

    Raises:
        Raising exception
    """
    try:
        os.remove(name_of_file_with_path)
    except OSError as e:
        if e.errno != errno.ENOENT:
            raise

def copy_file(src, dest):
    """
    Copy a file to another directory

    Args:
        src (str): File name need to be copy
        dest (str): Directory need to be copy to

    Returns:
        True if successful.

    Raises:
        IOError: source or destination doesn't exist
    """
    try:
        shutil.copy(src, dest)
    # Fail if source or destination doesn't exist
    except IOError as e:
        logging.error ('Error: %s' % e.strerror)
        exit(1)

def compare_results(val1, val2):
    """
    Compare 2 values that have the same type

    Args:
        val1 (any): First value that need to be compare
        val2 (any): Second value that need to be compare

    Returns:
        True if both values match exact, otherwise False

    Raises:
        Raising exception
    """
    if type(val1) != type(val2):
        logging.error ("Can not compare type %s with type %s, please covert your data type first and try again" % (type(val1), type(val2)))
        return False
    else:
        if val1 != val2:
            logging.error ("Value 1: %s, and  Value 2: %s is not the same" % (val1, val2))
            return False
        else:
            logging.info ("%s is the same as %s" % (val1, val2))
            return True
