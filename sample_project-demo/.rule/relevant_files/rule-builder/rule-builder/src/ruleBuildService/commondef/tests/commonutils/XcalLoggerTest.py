#
#  Copyright (C) 2019-2020  XC Software (Shenzhen) Ltd.
#


import unittest
from common.XcalLogger import XcalLogger


class MyTestCase(unittest.TestCase):
    def test_something(self):
        log = XcalLogger("agent", "test")
        log.info("abc", "")
        self.assertEqual(True, True)


if __name__ == '__main__':
    unittest.main()
