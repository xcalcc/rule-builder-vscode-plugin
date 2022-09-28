#!/usr/bin/python3
"""
test_annotate
unittest for annotation purposes
"""

import unittest
import os
import subprocess

from .Annotate import Annotation, IncorrectAPIUsage
from .AnnotationApi import FuncParseError
from . import rb_loc
import logger
logger = logger.get_log()


file_dir = os.path.dirname(os.path.realpath(__file__))
ex1 = "TAG|<Point: void <init>(double,double)>|this()|sensitive"
ex2 = "TAG|<java.net.Socket: void <init>(java.lang.String,int)>|this()|tainted"
ex3 = "TAG|<java.net.Socket: void <init>(java.net.InetAddress,int)>|this()|tainted"
ex4 = "TAG|<java.net.Socket: void connect(java.net.SocketAddress)>|this()|tainted"

class TestAnnotate(unittest.TestCase):
    
    def test_add_1(self):
        expr = Annotation()
        expr.add_entry_raw(ex1)
    
    def test_err_func(self):
        """function format is wrong"""
        expr = Annotation()
        expr.add_entry_raw(ex1)
        err_func = "TAG|<void err(java.lang.String,int)>|arg(1)|tainted"
        with self.assertRaises(FuncParseError):
            expr.add_entry_raw(err_func)
    
    def test_incorrect_api_call(self):
        """api call incorrect"""
        expr = Annotation()
        example = "SET_PARM_MOD|extra_field_incorrect|<Point: void <init>(double,double)>|this()"
        with self.assertRaises(IncorrectAPIUsage):
            expr.add_entry_raw(example) 
    
    def test_parm_mod(self):
        expr = Annotation()
        expr.add_entry_raw(
        "SET_PARM_MOD|<Point: void <init>(double,double)>|this()"
        )
        y = expr.classes_entry['Point']['void <init>(double,double)']
        logger.debug(y[0].translate())

    @unittest.skip
    def test_file_gen(self):
        """test if file generation is in correct directory"""
        expr = Annotation()
        expr.add_entry_raw(ex1)
        expr.generate(rb_loc, file_dir)
    
        exist = os.path.exists(os.path.join(file_dir, 'Point.h'))
        self.assertEqual(exist, True)

    @unittest.skip
    def test_ex_2(self):
        """test example 2"""
        expr = Annotation()
        expr.add_entry_raw(ex2)
        expr.generate(rb_loc, file_dir)
        
        exist = os.path.exists(os.path.join(file_dir, 'java/net/Socket.h'))
        self.assertEqual(exist, True) 
    
    def test_multiple(self):
        """test by passing multi-line (as if reading a file)"""
        expr = Annotation()
        expr.add_entry_raw(ex1)
        expr.add_entry_raw(ex2)
        expr.add_entry_raw(ex3)
        expr.add_entry_raw(ex4)
        expr.generate(rb_loc, file_dir)

        exist = os.path.exists(os.path.join(file_dir, 'java/net/Socket.h'))
        self.assertEqual(exist, True)

    def test_new_api(self):
        """testing of new API"""
        expr = Annotation()
        expr.add_entry_raw(
            "SET_PARM_MOD|<Point: void <init>(double,double)>|this()"
        )
        expr.add_entry_raw(
            "SET_IMPLICIT_ASSIGN|<org.xml.sax.InputSource: void <init>(java.io.Reader)>|this()|arg(1)"
        )
        expr.add_entry_raw(
            "SET_PARM_DEREF|<java.util.List: int get(int)>|this()"
        )

        expr.generate(rb_loc, file_dir)


if __name__ == "__main__":
    unittest.main()
