#!/usr/bin/python3

import unittest
from .TagAssert import FuncParse, TagAssert

class TestTagAssert(unittest.TestCase):
    func1 = "<Point: void <init>(double,double)>"
    line1 = "TAG|<Point: void <init>(double,double)>|this()|sensitive"
    line2 = "TAG|<Point: void <init>(double)>|this()|sensitive"
    assert1 = "ASSERT|<Point: void <init>(double,double)>|is_tag_attr_set(this(),\"sensitive\",\"sanitize_data\")|SER03"

    ex1 = "TAG|<Point: void <init>(double,double)>|this()|sensitive"
    ex2 = "TAG|<java.net.Socket: void <init>(java.lang.String,int)>|this()|tainted"
    ex3 = "TAG|<java.net.Socket: void <init>(java.net.InetAddress,int)>|this()|tainted"
    ex4 = "TAG|<java.net.Socket: void connect(java.net.SocketAddress)>|this()|tainted"
    ex5 = "TAG|<java.net.Socket: void bind(java.net.SocketAddress)>|this()|tainted"

    def test_1(self):
        a = FuncParse(TestTagAssert.func1)
        self.assertEqual(a.cls_name, "Point")  
    
    def test_2(self):
        TagAssert.add_entry_raw(ex1)
        TagAssert.add_entry_raw(ex2)
        TagAssert.add_entry_raw(ex3)
        TagAssert.add_entry_raw(ex4)
        TagAssert.add_etnry_raw(ex5) 
        TagAssert.generate('/home/nigel/rb_backend')

if __name__== "__main__":
    unittest.main()
