"""
test_declare_rule

unit testing for rule declaration
"""

import os
import unittest
from ruleBuildService.translator.declare_rule import DeclareRule
from . import rb_loc, output_dir

class TestDeclareRule(unittest.TestCase):
    def test_generate_file(self):
        DeclareRule.add_entry_raw("DECLARE|IDS03-J|CUSTOM|Do not Log unsanitized user input")
        DeclareRule.add_entry_raw("DECLARE|CWE295|CUSTOM|SSL Not Verified")
        #DeclareRule.dump(rb_loc, output_dir)
        DeclareRule.dump(output_dir)
        self.assertTrue(os.path.exists(os.path.join(output_dir, 'DECLARE_RULE.h'))) # check if expected file exist
