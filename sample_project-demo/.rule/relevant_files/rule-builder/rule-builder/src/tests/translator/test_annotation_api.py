"""
test_annotation_api

unit testing for annotation, check whether
annotation returns the expected string
"""

import unittest

from ruleBuildService.translator.annotation_api import *

f = "<java.net.Socket: void <init>(java.lang.String,int)>"

class TestAnnotateAPI(unittest.TestCase):

    def test_tag(self):
        tag = Tag(f, "this()", "sensitive")
        s = tag.translate()
        self.assertEqual(s,
            'RBC_SET_TAG(THIS_POINTER,"sensitive")'
        )

    def test_assert(self):
        expr = Assert(
        f,
        'is_tag_attr_set(arg(1),"tainted","sanitize_fmt_str")',
        "IDS03-J"
        )
        s = expr.translate()
        self.assertEqual(
            s,
            'RBC_ASSERT(RBC_IS_TAG_ATTR_SET(GET_ARG(1),"tainted","sanitize_fmt_str"),"IDS03-J")'
        )

    def test_set_implicit_assign(self):
        expr = Set_implicit_assign(f, 'this()', 'arg(1)')
        s = expr.translate()
        self.assertEqual(
            s,
            'SET_IMPLICIT_ASSIGN(THIS_POINTER,GET_ARG(1))'
        )

    def test_set_parm_mod(self):
        expr = Set_parm_mod(f, 'this()')
        s = expr.translate()
        self.assertEqual(
            s,
            "SET_PARM_MOD(THIS_POINTER)"
        )

    def test_set_func_may_sleep(self):
        expr = Set_func_may_sleep(f, 'arg(1)')
        s = expr.translate()
        self.assertEqual(
            s,
            "SET_FUNC_MAY_SLEEP(GET_ARG(1))"
        )
    
    def test_set_atomic_region_begin(self):
        expr = Set_atomic_region_begin(f)
        s = expr.translate()
        self.assertEqual(
            s,
            "SET_ATOMIC_REGION_BEGIN"
        )
    
    def test_set_atomic_region_end(self):
        expr = Set_atomic_region_end(f)
        s = expr.translate()
        self.assertEqual(
            s,
            "SET_ATOMIC_REGION_END"
        )

    def test_set_func_atomic(self):
        expr = Set_func_atomic(f)
        s = expr.translate()
        self.assertEqual(
            s,
            "SET_FUNC_ATOMIC"
        )
    
    def test_func_shutdown(self):
        expr = Set_func_shutdown(f)
        s = expr.translate()
        self.assertEqual(
            s,
            "SET_FUNC_SHUTDOWN"
        )
    
    def test_set_func_coll_append(self):
        expr = Set_func_coll_append(f, "this()", "arg(1)")
        s = expr.translate()
        self.assertEqual(
            s,
            "SET_FUNC_COLL_APPEND(THIS_POINTER,GET_ARG(1))"
        )
    
    def test_set_func_coll_remove(self):
        expr = Set_func_coll_remove(f, "this()", "arg(1)")
        s = expr.translate()
        self.assertEqual(
            s,
            "SET_FUNC_COLL_REMOVE(THIS_POINTER,GET_ARG(1))"
        )
    
    def test_set_func_coll_get(self):
        expr = Set_func_coll_get(f, "this()", "arg(1)")
        s = expr.translate()
        self.assertEqual(
            s,
            "SET_FUNC_COLL_GET(THIS_POINTER,GET_ARG(1))"
        )

    def test_set_func_map_put(self):
        expr = Set_func_map_put(f, "this()", "arg(1)", "arg(2)")
        s = expr.translate()
        self.assertEqual(
            s,
            "SET_FUNC_MAP_PUT(THIS_POINTER,GET_ARG(1),GET_ARG(2))"
        )
    
    def test_func_map_get(self):
        expr = Set_func_map_get(f, "this()", "arg(1)")
        s = expr.translate()
        self.assertEqual(
            s,
            "SET_FUNC_MAP_GET(THIS_POINTER,GET_ARG(1))"
        )
    
    def test_set_func_str_get(self):
        expr = Set_func_str_get(f, "this()", "arg(1)")
        s = expr.translate()
        self.assertEqual(
            s,
            "SET_FUNC_STR_GET(THIS_POINTER,GET_ARG(1))"
        )

    def test_copy_tag(self):
        expr = Copy_tag(f, "this()", "arg(1)")
        s = expr.translate()
        self.assertEqual(
            s,
            "COPY_TAG(THIS_POINTER,GET_ARG(1))"
        )
    
    def test_eval_tag(self):
        expr = Eval_tag(f, "return()", "this()")
        s = expr.translate()
        self.assertEqual(
            s,
            "EVAL_TAG(GET_RET,THIS_POINTER)"
        )
