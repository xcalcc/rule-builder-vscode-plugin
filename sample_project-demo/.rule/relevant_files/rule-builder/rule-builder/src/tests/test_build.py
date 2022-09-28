"""
build test

testing for building capability
"""

import unittest
import os
from ruleBuildService.config import ErrorNo
from ruleBuildService.build import RuleBuildService
from common.XcalException import XcalException
from common.XcalLogger import XcalLogger
from . import test_dir

class TestBuild(unittest.TestCase):
    def setUp(self):
        self.logger = XcalLogger("test_build", "setUp")

    def test_operations(self):
        """testing the operations for changing attributes"""
        service = RuleBuildService('java','tests/output') # rule
        service.set_language('c++')
        service.add_inputs(
            os.path.join(test_dir, 'translate/cwe295-test/cwe295.mi')
        )
        service.add_references(
            os.path.join(test_dir, 'translate/cwe295-test/org.apache.commons-commons-email.o.vtable.mi')
        )
        service.output_to('tests/output')
        service.name_rule('cwe295')

    @unittest.skip
    def test_translate_1(self):
        """testing for translate (cwe295)"""
        service = RuleBuildService('java','tests/output') # rule
        service.add_inputs(
            os.path.join(test_dir, 'translate/cwe295-test/cwe295.mi')
        )
        service.add_references(
            os.path.join(test_dir, 'translate/cwe295-test/org.apache.commons-commons-email.o.vtable.mi')
        )
        service.name_rule('cwe295')
        service.translate()

    @unittest.skip
    def test_translate_2(self):
        """testing for translatino of SER03"""
        service = RuleBuildService('java', 'tests/output/ser03')
        service.add_inputs(
            os.path.join(test_dir, 'translate/ser03/ser03.mi')
        )
        service.add_references(
            os.path.join(test_dir, 'translate/ser03/rt.o.vtable.mi')
        )
        service.output_to('tests/output')
        service.name_rule('ser03')
        service.translate()


    def test_compile(self):
        """testing for translation and compilation of CWE295"""
        service = RuleBuildService('java','tests/output') # rule
        service.add_inputs(
            os.path.join(test_dir, 'translate/cwe295-test/cwe295.mi')
        )
        service.add_references(
            os.path.join(test_dir, 'translate/cwe295-test/org.apache.commons-commons-email.o.vtable.mi')
        )
        service.output_to('tests/output')
        service.name_rule('cwe295')
        service.add_dependencies(
            "/home/nigel/rule-builder-backup/test/translate/cwe295-test/apache-mail.jar",
            "/home/nigel/rule-builder-backup/test/translate/cwe295-test/javax-mail.jar"
        )

        service.translate()
        service.xvsa_compile('/home/nigel/xvsa')

    @unittest.skip
    def test_compile_2(self):
        """testing for translation and compilatino of SER03"""
        service = RuleBuildService('java', 'tests/output/')
        service.add_inputs(
            os.path.join(test_dir, 'translate/ser03/ser03.mi')
        )
        service.add_references(
            os.path.join(test_dir, 'translate/ser03/rt.o.vtable.mi')
        )
        service.name_rule('ser03')
        service.translate()
        service.xvsa_compile('/home/nigel/xvsa')