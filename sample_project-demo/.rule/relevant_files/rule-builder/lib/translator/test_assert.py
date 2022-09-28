#!/usr/bin/python3

import unittest
from .TagAssert import FuncParse, TagAssert


class TestAssert(unittest.TestCase):    
    assert1 = "ASSERT|<Point: void <init>(double,double)>|is_tag_attr_set(this(),\"sensitive\",\"sanitize_data\")|SER03"

    def test_1(self):
        TagAssert.add_entry_raw(TestAssert.assert1)
        TagAssert.generate('/home/nigel/rb_backend/')
