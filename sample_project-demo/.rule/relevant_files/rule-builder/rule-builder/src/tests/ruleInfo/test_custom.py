import unittest

from ruleBuildService.config import ErrorNo
from ruleBuildService.ruleInfo.custom import csv_stringify, MasterCustom
from common.XcalException import XcalException

class TestCustom(unittest.TestCase):
    def test_stringify(self):
        self.assertEqual(
            csv_stringify("CSV"),
            "CSV0"
        )
    
    def test_stringify_2(self):
        self.assertEqual(
            csv_stringify("CSV01"),
            "C010"
        )

    def test_stringify_3(self):
        self.assertEqual(
            csv_stringify("CSV01-J"),
            "C01J0"
        )
