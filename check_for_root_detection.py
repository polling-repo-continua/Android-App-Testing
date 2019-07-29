#!/usr/bin/env python3

__author__ = "Jake Miller (@LaconicWolf)"
__date__ = "20190726"
__version__ = "0.01"
__description__ = '''\
A script that recursively searches smali files for the presence of root detection strings.
First, decode an APK with apktool "apktool d example.apk". Next, move to the newly created 
directory and run this script.
'''

import sys

if not sys.version.startswith('3'):
    print('\n[-] This script will only work with Python3. Sorry!\n')
    exit()

import os
import re
import threading
from queue import Queue


def find_smali_files(root_dir):
    """Recursively looks for *.smali files and returns
    a list containing the full file path.
    """
    smali_files = []
    for root, dirnames, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.endswith('.smali'):
                smali_files.append(os.path.join(root, filename))
    return smali_files


def search_text_for_root_detection_strings(textfile):
    """Reads and searches a specified textfile for presence 
    of root detection strings. Returns the name
    of the text file and matches if a match is found. Based on:
    https://stackoverflow.com/questions/1101380/determine-if-running-on-a-rooted-device
    and:
    https://stackoverflow.com/questions/12286928/fastest-way-in-python-to-search-for-multiple-items-in-a-body-of-text
    """
    root_detection_strings = [
                "/system/app/Superuser.apk", "/sbin/su",
                "/system/bin/su", "/system/xbin/su", "/data/local/xbin/su",
                "/data/local/bin/su", "/system/sd/xbin/su", 
                "/system/bin/failsafe/su", "/data/local/su", "/su/bin/su",
                "test-keys", '"/system/xbin/which", "su"', "'/system/xbin/which', 'su'",
            ]
    with open(textfile) as fh:
        contents = fh.read()
    regex = re.compile('|'.join(re.escape(x) for x in root_detection_strings))
    found = regex.findall(contents)
    if found:
        for item in found:
            method_name, matched_string = find_parent_method(contents, item)
            with print_lock:
                print("{}, {}, {}".format(textfile, method_name, matched_string))


def find_parent_method(file_contents, string):
    """Return the name of a method where a string is found."""
    start_method_indices = [c.start() for c in re.finditer('\.method', file_contents)]
    end_method_indices = [c.start() for c in re.finditer('\.end method', file_contents)]
    for index in zip(start_method_indices, end_method_indices):
        method = file_contents[index[0]:index[1]]
        if string in method:
            method_name = method.split('\n')[0]
            method_names.append(method_name)
            return method_name, string


def find_method_invocation(method):
    """Takes a method name and attempts to find where that 
    method is called, then repeats the process until it traces
    the last call."""
    pass



def manage_queue():
    """Manages the smali file queue and calls the 
    search_text_for_root_detection_strings function.
    """
    while True:
        current_filename = file_queue.get()
        search_text_for_root_detection_strings(current_filename)
        file_queue.task_done()


def main():
    root_dir = '.'
    print('[*] Checking for .smali files...')
    smali_file_list = find_smali_files(root_dir)
    if smali_file_list:
        print('[+] Found {} .smali files.'.format(len(smali_file_list)))
    else:
        print('[-] No .smali files found while searching recursively from {}.'.format(os.getcwd()))
        exit()
    print('[*] Searching files for strings that are commonly used for root detection...')

    for i in range(number_of_threads):
        t = threading.Thread(target=manage_queue)
        t.daemon = True
        t.start()

    for current_file in smali_file_list:
        file_queue.put(current_file)
    file_queue.join()

if __name__ == '__main__':

    # Shared variables for the threads

    method_names = []

    number_of_threads = 30
    print_lock = threading.Lock()
    file_queue = Queue()

    main()
