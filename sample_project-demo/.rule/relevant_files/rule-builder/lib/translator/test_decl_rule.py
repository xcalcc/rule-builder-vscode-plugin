'''
Unit Test for rule declaration
'''
import unittest
from logger import *
from .DeclareRule import DeclareRule
logger = get_log()


class TestDeclareRule(unittest.TestCase):
    def test_declare_fault(self):
        with self.assertRaises(TypeError):
            DeclareRule.add_entry_raw(1)

    def test_declare_desc(self):
        DeclareRule.add_entry_raw("DECLARE|IDS03-J|CUSTOM|Do not Log unsanitized user input")
        DeclareRule.add_entry_raw("DECLARE|CWE295|CUSTOM|SSL Not Verified")
        DeclareRule.dump('/home/nigel/rb_backend/')

if __name__ == "__main__":
    unitest.main()

