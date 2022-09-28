"""
test_rule_file_gen

unit testing for rule file generation for both FSM and annotation
"""

import unittest
import os
from ruleBuildService.translator.rule_file_gen import RuleFileGen, LangNotSupported
from ruleBuildService.translator.read import read_file, create_fsm, read_annotation
from ruleBuildService.config import ErrorNo
from common.XcalException import XcalException
from .. import test_dir
from . import output_dir

class TestRuleFileGen(unittest.TestCase):

    def test_lang_err(self):
        '''wrong input for language, should report error'''
        try:
            fg = RuleFileGen('lang-not-exist')
        except XcalException as e:
            self.assertEqual(e.err_code, ErrorNo.E_LANGUAGE_NOT_SUPPORTED)

    def test_out_dir_err(self):
        '''output not found, should report error'''
        try:
            fg = RuleFileGen('c++', out_dir='../not_found_dir')
        except XcalException as e:
            self.assertEqual(e.err_code, ErrorNo.E_RESOURCE_NOT_FOUND)

    def test_ids03(self):
        f = os.path.join(test_dir, 'translate/ids03/ids03.mi')
        lines = read_file(f)
        fsm, annotator = create_fsm(lines, 'ids03', None)
        fg = RuleFileGen('java', os.path.join(test_dir,'translate/ids03/rt.o.vtable.mi'),
            out_dir = output_dir)
        #fsm, annotator = create_fsm(lines)
        fg.attach_annotations(annotator)
        fg.generate()

    def test_cwe295(self):
        f = os.path.join(test_dir, 'translate/cwe295-test/cwe295.mi')
        lines = read_file(f)
        fsm, annotator = create_fsm(lines, 'cwe295', None)

        fg = RuleFileGen('java', os.path.join(test_dir,'translate/cwe295-test/org.apache.commons-commons-email.o.vtable.mi'),
            out_dir=output_dir, name='cwe295')
        fg.attach_fsm(fsm) 
        fg.generate()