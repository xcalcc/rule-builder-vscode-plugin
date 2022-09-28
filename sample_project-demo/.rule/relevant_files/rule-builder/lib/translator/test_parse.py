import unittest
import os
'''
unit test for condition-parsing component
'''

from .ConditionParse import APIError, ConditionParse, APINotDefined
import logger
logger = logger.get_log()
class TestParse(unittest.TestCase):
    def test_1(self):
        with self.assertRaises(APIError):
            ConditionParse.parse('abc')     
    def test_2(self):
        with self.assertRaises(APINotDefined):
            ConditionParse.parse('next()')
    def test_3(self):
        with self.assertRaises(APIError):
            ConditionParse.parse('not(a,b)')
    def test_4(self):
        with self.assertRaises(APIError):
            ConditionParse.parse('not(a)')
    def test_5(self):
        a = ConditionParse.parse('not(arg(1))')
        c = a.children[0].children[0]
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
        with self.assertRaises(APIError):
            a = ConditionParse.parse('is_tag_attr_set(this(x), "tainted", "abc")') 
    def test_get_ret(self):
        a = ConditionParse.parse('return()')
        s = a.translate()
        self.assertEqual(s, "GET_RET")
    def test_tag(self):
        a = ConditionParse.parse('tag(this(),"tainted")')
        s = a.translate()
        self.assertEqual(s,'RBC_SET_TAG(THIS_POINTER,"tainted")')
    def test_another(self):
        a = ConditionParse.parse('tag(return(),"tainted")')
    def test_assert(self):
        a = ConditionParse.parse('assert(is_tag_attr_set(this(),"tainted","abc"),"SER03-J")')
        s = a.translate()
        self.assertEqual(s, 'RBC_ASSERT(RBC_IS_TAG_ATTR_SET(THIS_POINTER,"tainted","abc"),"SER03-J")')
    def test_pre_call(self):
        logger.debug('----test_pre_call----')
        a = ConditionParse.parse('pre_call(ssd_safe.App: void <init>())')
        #s = a.translate()
        logger.info("file path: %s"%__file__)
        s = a.translate(['/home/nigel/rb_backend/test/translate/shaw/ssd_safe-ssd_safe.o.vtable.mi'])
        self.assertEqual(s, 'PRE_CALL("_ZN8ssd_safe3AppC1Ev")') 
         
if __name__ == "__main__":
    unittest.main()
