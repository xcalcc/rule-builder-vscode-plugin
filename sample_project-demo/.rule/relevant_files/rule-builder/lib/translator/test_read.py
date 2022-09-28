#!/usr/bin/python3

'''
test_read

unittest for reading utility of input (.mi) file
'''
import unittest

from .read import read_file, create_fsm
import logger
import os
logger = logger.get_log()

test_dir = os.path.abspath(os.path.join(__file__, '../../../test/translate'))

class TestReadmi(unittest.TestCase):
    def test_read(self):
        logger.debug('----test_read-----')
        #f = '/home/nigel/rb_backend/test/translate/cwe295-test/cwe295.mi'
        f = os.path.join(test_dir, 'cwe295-test/cwe295.mi')
        lines = read_file(f)
        logger.debug(lines)

    def test_read_err(self):
        logger.debug('----test_read_err-----')
        #f = '/home/nigel/rb_backend/test/translate/cwe295-test/filenotfound.mi'
        f = os.path.join(test_dir, 'cwe295-test/filenotfound.mi')
        with self.assertRaises(FileNotFoundError):
            lines = read_file(f)

    def test_create_fsm(self):
        logger.debug('----test_create_fsm-----')
        #f = '/home/nigel/rb_backend/test/translate/cwe295-test/cwe295.mi'
        f = os.path.join(test_dir, 'cwe295-test/cwe295.mi')
        lines = read_file(f)
        fsm = create_fsm(lines)
        logger.debug(fsm)
    

if __name__ == "__main__":
    unittest.main()
