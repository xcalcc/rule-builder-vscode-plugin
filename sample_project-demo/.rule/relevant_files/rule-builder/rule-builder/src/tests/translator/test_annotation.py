"""
test_annotate

unit testing for annotation
"""

import unittest
import os
import subprocess
from ruleBuildService.config import ErrorNo
from ruleBuildService.translator.annotation import Annotation
from common.XcalException import XcalException
#from ruleBuildService.translator.annotation_api import FuncParseError
from . import output_dir
from .. import rb_loc

#### Examples
ex1 = "TAG|<Point: void <init>(double,double)>|this()|sensitive"
ex2 = "TAG|<java.net.Socket: void <init>(java.lang.String,int)>|this()|tainted"
ex3 = "TAG|<java.net.Socket: void <init>(java.net.InetAddress,int)>|this()|tainted"
ex4 = "TAG|<java.net.Socket: void connect(java.net.SocketAddress)>|this()|tainted"

class TestAnnotate(unittest.TestCase):

    def test_add_1(self):
        """adding just 1 entry"""
        expr = Annotation()
        expr.add_entry_raw(ex1)

    def test_err_func(self):
        """function format should report error"""
        expr = Annotation()
        expr.add_entry_raw(ex1)
        err_func = "TAG|<void err(java.lang.String,int)>|arg(1)|tainted"
        try:
            expr.add_entry_raw(err_func)
        except XcalException as e:
            self.assertEqual(e.err_code, ErrorNo.E_INVALID_FUNCTION_FORMAT)

    def test_parm_mod(self):
        """use one of the API"""

        expr = Annotation()
        expr.add_entry_raw(
            "SET_PARM_MOD|<Point: void <init>(double,double)>|this()"
        )
        y = expr.classes_entry['Point']['void <init>(double,double)']
        translation = y[0].translate()

        self.assertEqual(translation, "SET_PARM_MOD(THIS_POINTER)")


    def test_file_gen(self):
        """test if file generation is in correct directory"""
        expr = Annotation()
        expr.add_entry_raw(ex1)
        expr.generate('java', output_dir)

        exist = os.path.exists(os.path.join(output_dir, 'Point.h'))
        self.assertEqual(exist, True)

    def test_ex_2(self):
        """test example 2"""
        expr = Annotation()
        expr.add_entry_raw(ex2)
        expr.generate('java', output_dir)

        exist = os.path.exists(os.path.join(output_dir, 'java/net/Socket.h'))
        self.assertEqual(exist, True)

    def test_multiple(self):
        """test by passing multi-line (as if reading a file)"""
        expr = Annotation()
        expr.add_entry_raw(ex1)
        expr.add_entry_raw(ex2)
        expr.add_entry_raw(ex3)
        expr.add_entry_raw(ex4)
        expr.generate('java', output_dir)

        exist = os.path.exists(os.path.join(output_dir, 'java/net/Socket.h'))
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

        expr.generate('java', output_dir)

    def test_duplicate_api(self):
        expr = Annotation()
        expr.add_entry_raw(
            "SET_PARM_DEREF|<java.util.List: int get(int)>|this()"
        )
        expr.add_entry_raw(
            "SET_PARM_DEREF|<java.util.List: int get(int)>|this()"
        )
        expr.generate('java', os.path.join(output_dir, 'dup'))

    def test_language_err(self):
        """language not supported test"""
        expr = Annotation()
        expr.add_entry_raw(
            "SET_PARM_DEREF|<java.util.List: int get(int)>|this()"
        )

        try:
            expr.generate('c+', os.path.join(output_dir, 'dup')) # should produce error
        except XcalException as e:
            self.assertEqual(e.err_code, ErrorNo.E_LANGUAGE_NOT_SUPPORTED)