#!/usr/bin/python3

import unittest
from .TagAssert import FuncParse, TagAssert, ActionNotRecognised

class TestTag(unittest.TestCase):
    '''
    Testing for Tagging
    '''
    inv_1 = "<Point: void <init>(double,double)>|this()|sensitive" # invalid
    ex1 = "TAG|<Point: void <init>(double,double)>|this()|sensitive"
    ex2 = "TAG|<java.net.Socket: void <init>(java.lang.String,int)>|this()|tainted"
    ex3 = "TAG|<java.net.Socket: void <init>(java.net.InetAddress,int)>|this()|tainted"
    ex4 = "TAG|<java.net.Socket: void connect(java.net.SocketAddress)>|this()|tainted"
    ex5 = "TAG|<java.net.Socket: void bind(java.net.SocketAddress)>|this()|tainted"

    def test_invalid(self):
        with self.assertRaises(ActionNotRecognised):
            TagAssert.add_entry_raw(TestTag.inv_1)

    def test_valid(self):
        # running 5 cases at once
        TagAssert.add_entry_raw(TestTag.ex1)
        TagAssert.add_entry_raw(TestTag.ex2)
        TagAssert.add_entry_raw(TestTag.ex3)
        TagAssert.add_entry_raw(TestTag.ex4)
        TagAssert.add_entry_raw(TestTag.ex5)
        TagAssert.generate('/home/nigel/rb_backend/')
