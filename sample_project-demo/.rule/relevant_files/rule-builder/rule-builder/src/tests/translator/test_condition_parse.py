#!/usr/bin/python3
"""
test_condition_parse

unit testing for condition_parse
"""

import unittest
from ruleBuildService.translator.condition_parse import ConditionParse, APIError, APINotDefined
from common.XcalLogger import XcalLogger
from common.XcalException import XcalException
from ruleBuildService.config import ErrorNo
#from .. import logger

class TestConditionParse(unittest.TestCase):
    """Testing for Condition Parsing"""

    def test_api_not_found(self):
        """Not recognised as API"""
        try:
            ConditionParse.parse('abc')
        except XcalException as e:
            self.assertEqual(e.err_code, ErrorNo.E_INCORRECT_API_CALL)

    def test_api_not_defined(self):
        """api not defined reported"""
        # with self.assertRaises(APINotDefined):
        #     ConditionParse.parse('next()')
        try:
            ConditionParse.parse('next()')
        except XcalException as e:
            self.assertEqual(e.err_code, ErrorNo.E_API_NOT_EXIST)

    def test_api_inccorect_use(self):
        """api not used correctly"""
        # with self.assertRaises(APIError):
        #     ConditionParse.parse('not(a,b)')
        try:
            ConditionParse.parse('not(a,b)')
        except XcalException as e:
            self.assertEqual(e.err_code, ErrorNo.E_INCORRECT_API_CALL)

    def test_node_content(self):
        root = ConditionParse.parse('not(arg(1))')
        c = root.children[0].children[0]
        self.assertEqual(c.content, '1')

    def test_not_api(self):
        a = ConditionParse.parse('not(arg(1))')
        s = a.translate()
        self.assertEqual(s, "NOT(GET_ARG(1))")

    def test_is_attr_set(self):
        a = ConditionParse.parse('is_tag_attr_set(this(),"tainted","abc")')
        #x = a.children[0]
        #self.assertEqual(len(x.children), 1)
        s = a.translate()
        self.assertEqual(s, "RBC_IS_TAG_ATTR_SET(THIS_POINTER,\"tainted\",\"abc\")")

    def test_is_attr_set_invalid(self):
        # with self.assertRaises(APIError):
        #     a = ConditionParse.parse('is_tag_attr_set(this(x), "tainted", "abc")') 
        try:
            ConditionParse.parse('is_tag_attr_set(this(x),"tainted","abc")')
        except XcalException as e:
            self.assertEqual(e.err_code, ErrorNo.E_INCORRECT_API_CALL)

    def test_get_ret(self):
        a = ConditionParse.parse('return()')
        s = a.translate()
        self.assertEqual(s, "GET_RET")

    def test_tag(self):
        a = ConditionParse.parse('tag(this(),"tainted")')
        s = a.translate()
        self.assertEqual(s,'RBC_SET_TAG(THIS_POINTER,"tainted")')

    def test_assert(self):
        a = ConditionParse.parse('assert(is_tag_attr_set(this(),"tainted","abc"),"SER03-J")')
        s = a.translate()
        self.assertEqual(s, 'RBC_ASSERT(RBC_IS_TAG_ATTR_SET(THIS_POINTER,"tainted","abc"),"SER03-J")')