#
#  Copyright (C) 2019-2020  XC Software (Shenzhen) Ltd.
#


import unittest

from common.CommandLineUtility import CommandLineUtility
from common.XcalLogger import XcalLogger


class BasicCase(unittest.TestCase):
    def setUp(self):
        self.logger = XcalLogger("CommandLineUtilityTest", "BasicCase")

    def test_echo_success(self):
        rc = CommandLineUtility.bash_execute("echo ok", 1.0, self.logger, "test.log")
        self.assertEqual(0, rc)

    def test_not_found_command(self):
        rc = CommandLineUtility.bash_execute("makes ome unknown program ok", 1.0, self.logger, "test.log")
        self.assertNotEqual(0, rc)

    def test_temp_logfile(self):
        rc = CommandLineUtility.bash_execute("echo ok", 1.0, self.logger)
        self.assertEqual(0, rc)

if __name__ == '__main__':
    unittest.main()
