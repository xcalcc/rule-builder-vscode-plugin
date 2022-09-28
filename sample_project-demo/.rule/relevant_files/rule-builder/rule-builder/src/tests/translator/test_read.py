"""
test_read

unit testing for reading utility of input (.mi) file
"""

import unittest
import os

from ruleBuildService.translator.read import read_file, read_annotation, create_fsm

from .. import test_dir
from ruleBuildService.config import ErrorNo
from common.XcalException import XcalException

class TestRead(unittest.TestCase):

    def test_read(self):
        """basic read for lines"""
        f = os.path.join(test_dir, 'translate/cwe295-test/cwe295.mi')
        lines = read_file(f)

    def test_read_err(self):
        """File not found supposed to be reported"""
        f = os.path.join(test_dir, 'translate/cwe295-test/filenotfound.mi')

        try:
            lines = read_file(f)
        except XcalException as e:
            self.assertEqual(e.err_code, ErrorNo.E_RESOURCE_NOT_FOUND)

    def test_create_fsm(self):
        """involves creation of fsm"""
        f = os.path.join(test_dir, 'translate/cwe295-test/cwe295.mi')
        lines = read_file(f)
        fsm, annotator = create_fsm(lines, 'cwe295', None)

    def test_read_annotation(self):
        """testing for annotation-only reading"""
        f = os.path.join(test_dir, 'translate/annotation/annot1.mi')
        lines = read_file(f)
        annotator = read_annotation(lines)
        self.assertTrue(len(annotator.entries) == len(lines))

    def test_annot_fsm(self):
        """read annotation with create_fsm"""
        f = os.path.join(test_dir, 'translate/annotation/annot1.mi')
        lines = read_file(f)
        fsm, annotator = create_fsm(lines, 'annot1', None)
        self.assertTrue(len(annotator.entries) == len(lines))