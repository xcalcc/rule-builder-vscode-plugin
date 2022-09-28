#!/usr/bin/python3
'''
automated testing for translation
'''

import unittest
import os
import sys
import subprocess
import argparse

# path to test directory and script
test_dir = os.path.abspath(os.path.dirname(__file__))
script_file = os.path.join(test_dir, 'translate.py')

def create_dir(directory):
    '''create directory: build in specified directory to store
    translation result'''
    build_dir = os.path.join(directory, 'build')
    if not os.path.exists(build_dir):
        os.makedirs(build_dir)
    return build_dir

class TestTranslate(unittest.TestCase):

    def test_cwe295(self):
        cwe295_dir = os.path.join(test_dir, 'cwe295-test')         
        create_dir(cwe295_dir)
        command = [
            'python3',
            script_file,
            os.path.join(cwe295_dir, 'cwe295.mi'),
            '-l', 'java',
            '-r', os.path.join(cwe295_dir, 'org.apache.commons-commons-email.o.vtable.mi'),
            '--out', os.path.join(cwe295_dir, 'build'),
            '--name','cwe295']
        
        subprocess.call(command)


    def test_ids03(self):
        ids03_dir = os.path.join(test_dir, 'ids03')
        create_dir(ids03_dir)
        
        command = [
            'python3',
            script_file,
            os.path.join(ids03_dir, 'ids03.mi'),
            '-l', 'java',
            '-r', os.path.join(ids03_dir, 'rt.o.vtable.mi'),
            '--out', os.path.join(ids03_dir, 'build'),
            '--name', 'ids03'
        ]
        subprocess.call(command)
          
    def test_ser03(self):
        ser03_dir = os.path.join(test_dir, 'ser03')
        create_dir(ser03_dir)
        command = [
            'python3',
            script_file,
            os.path.join(ser03_dir, 'ser03.mi'),
            '-l', 'java',
            '-r', os.path.join(ser03_dir, 'rt.o.vtable.mi'),
            '--out', os.path.join(ser03_dir, 'build'),
            '--name', 'ser03'
        ]
        subprocess.call(command)

    def test_user_rule(self):
        user_rule_dir = os.path.join(test_dir, 'shaw')
        create_dir(user_rule_dir)
        command = [
            'python3',
            script_file,
            os.path.join(user_rule_dir, 'user_rule.mi'),
            '-l', 'java',
            '-r', os.path.join(user_rule_dir, 'ssd_safe-ssd_safe.o.vtable.mi'),
            '--out', os.path.join(user_rule_dir, 'build'),
            '--name', 'URULE'
        ]
        subprocess.call(command)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='test_translate')
    parser.add_argument('--clean', help='clean mode', action='store_true') 
    unittest.main()
    
