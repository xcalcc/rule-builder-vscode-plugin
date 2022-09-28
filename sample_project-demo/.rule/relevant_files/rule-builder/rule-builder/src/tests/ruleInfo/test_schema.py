import unittest
import json
import os
from . import test_dir
from ruleBuildService.ruleInfo.schema import RuleInfoSchema
from common.XcalException import XcalException
from ruleBuildService.config import ErrorNo

class TestSchema(unittest.TestCase):
    def test_1(self):
        schema = RuleInfoSchema()
        # with open("/home/nigel/rule-builder/test/info/single.json") as f:
        #     schema.read_json(json.load(f))
        with open(os.path.join(test_dir, 'info/single.json')) as f:
            schema.read_json(json.load(f))

    def test_err(self):
        """language field not found in json"""
        schema = RuleInfoSchema()
        # with open("/home/nigel/rule-builder/test/info/invalid.json") as f:
        with open(os.path.join(test_dir, 'info/invalid.json')) as f:
            try:
                schema.read_json(json.load(f))
            except XcalException as e:
                self.assertEqual(e.err_code, ErrorNo.E_INFO_FIELD_MISSING)