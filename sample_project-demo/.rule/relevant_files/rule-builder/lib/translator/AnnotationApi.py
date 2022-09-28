#!/usr/bin/python3
"""
AnnotationApi

Collection of APIs that are usable for annotating purposes.
"""

import re
from logger import retrieve_log
from .ConditionParse import ConditionParse

LOGGER = retrieve_log()

# pylint: disable=too-few-public-methods, simplifiable-if-statement, missing-super-argument, invalid-name

def parse_translate(expr):
    """parsing an expression to a form like in template.h file"""
    return ConditionParse.parse(expr).translate()

class FuncParseError(Exception):
    """raised when something goes wrong when parsing function"""
    pass


class FuncParse(object):
    """function parser
    
    function parser class to extract information on the function concerned.
    The information of the function itself is used for the purpose of knowing which 
    function on what class and package (especially in java). For attributes below we 
    will use example of
    <java.lang.StringBuilder: java.lang.StringBuilder append(java.lang.String)>
    
    Attributes:
        sig (str): complete function signature wrapped in "<>"
        cls_name (str): class name, java.lang.StringBuilder
        method_sig (str): method signature, java.lang.StringBuilder append(java.lang.String) 
        ret_type (str): return type, java.lang.StringBuilder
        met_name (str): method name, append
        args (str): arguments (only type), java.lang String  
        is_interface: flag if the method is of interface type, False
    """

    # pylint: disable=too-many-instance-attributes
    def __init__(self, sig):
        LOGGER.debug("parsing function %s", sig)
        try:
            cls_matcher = re.search(r'(?<=<).*(?=:)', sig)
            assert (cls_matcher is not None), "Can't match class name: signature: %s"%sig
            self.sig = sig
            LOGGER.debug("sig = %s", self.sig)

            self.cls_name = cls_matcher.group(0)
            LOGGER.debug("class name = %s", self.cls_name)
            method_sig_matcher = re.search(r'(?<=: ).*(?=>)', sig)
            pkg_split = self.cls_name.split('.')
            if len(pkg_split) > 1: # contain structure, take package name
                self.pkg_name = '.'.join(pkg_split[:-1])
            else:
                self.pkg_name = ""
            assert (method_sig_matcher is not None), \
                "Can't match method signature, signature: %s"%sig
            method_sig = method_sig_matcher.group(0)
            self.method_sig = method_sig
            LOGGER.debug("method_sig = %s", method_sig)
            ret_matcher = re.search(r'^.*(?= )', method_sig)
            self.ret_type = ret_matcher.group(0)
            LOGGER.debug("return type = %s", self.ret_type)
            met_name_matcher = re.search(r'(?<= ).*(?=\()', method_sig)

            assert (met_name_matcher is not None), \
                "can't match method name, method signature: %s"%method_sig
            self.met_name = met_name_matcher.group(0)
            LOGGER.debug("method name = %s", self.met_name)
            args_matcher = re.search(r'(?<=\().*(?=\))', method_sig)

            assert (args_matcher is not None), \
                "Can't match arg list, method signature: %s"% method_sig
            self.args = args_matcher.group(0).split(',')
            LOGGER.debug("arguments = %s", self.args)
            interface_matcher = re.search(r'^(I)', sig)
            if interface_matcher:
                self.is_interface = True
            else:
                self.is_interface = False
            LOGGER.debug("is interface = %s", self.is_interface)
        except AssertionError:
            LOGGER.error("function %s doesn't follow the pattern", sig)
            raise FuncParseError("%s: un-parseable"%sig)

class AnnotationObject(object):
    """Parent class of all annotation API"""
    def __init__(self, function):
        self.parser = FuncParse(function)

    def translate(self):
        """translate this object's annotation into compilable string
            following the template.h"""
        pass

class Tag(AnnotationObject):
    """Set_tag annotation"""
    def __init__(self, function, key, tag):
        super().__init__(function)
        self.key = key
        self.tag = tag

    def translate(self):
        return 'RBC_SET_TAG(%s,"%s")'%(parse_translate(self.key), self.tag)

class Assert(AnnotationObject):
    """Rbc_assert annotation"""
    def __init__(self, function, condition, error):
        super().__init__(function)
        self.condition = condition
        self.error = error

    def translate(self):
        return 'RBC_ASSERT(%s,"%s")'%(parse_translate(self.condition), self.error)

class Set_implicit_assign(AnnotationObject):
    """Set_implicit_assign annotation"""
    def __init__(self, function, key1, key2):
        super().__init__(function)
        self.key1 = key1
        self.key2 = key2

    def translate(self):
        return 'SET_IMPLICIT_ASSIGN(%s,%s)'%(parse_translate(self.key1), parse_translate(self.key2))

class Set_parm_mod(AnnotationObject):
    """Set_parm_mod annotation"""
    def __init__(self, function, key):
        super().__init__(function)
        self.key = key
    def translate(self):
        return 'SET_PARM_MOD(%s)'%parse_translate(self.key)

class Set_parm_deref(AnnotationObject):
    """Set_parm_deref annotation"""
    def __init__(self, function, key):
        super().__init__(function)
        self.key = key
    def translate(self):
        return 'SET_PARM_DEREF(%s)'%parse_translate(self.key)

class Set_func_may_sleep(AnnotationObject):
    """Set_func_may_sleep annotation"""
    def __init__(self, function, key):
        super().__init__(function)
        self.key = key
    def translate(self):
        return 'SET_FUNC_MAY_SLEEP(%s)'%parse_translate(self.key)

class Set_atomic_region_begin(AnnotationObject):
    """Set_atomic_region_begin annotation"""
    def __init__(self, function):
        super().__init__(function)
    def translate(self):
        return 'SET_ATOMIC_REGION_BEGIN'

class Set_atomic_region_end(AnnotationObject):
    """Set_atomic_region_end annotation"""
    def __init__(self, function):
        super().__init__(function)
    def translate(self):
        return 'SET_ATOMIC_REGION_END'

class Set_func_atomic(AnnotationObject):
    """Set_func_atomic annotation"""
    def __init__(self, function):
        super().__init__(function)
    def translate(self):
        return 'SET_FUNC_ATOMIC'

class Set_func_shutdown(AnnotationObject):
    """Set_func_shutdown annotation"""
    def __init__(self, function):
        super().__init__(function)
    def translate(self):
        return 'SET_FUNC_SHUTDOWN'

class Set_func_coll_append(AnnotationObject):
    """Set_func_coll_append annotation"""
    def __init__(self, function, key1, key2):
        super().__init__(function)
        self.key1 = key1
        self.key2 = key2
    def translate(self):
        return 'SET_FUNC_COLL_APPEND(%s,%s)'% \
            (parse_translate(self.key1), parse_translate(self.key2))

class Set_func_coll_remove(AnnotationObject):
    """Set_func_coll_remove annotation"""
    def __init__(self, function, key1, key2):
        super().__init__(function)
        self.key1 = key1
        self.key2 = key2
    def translate(self):
        return 'SET_FUNC_COLL_REMOVE(%s,%s)'% \
            (parse_translate(self.key1), parse_translate(self.key2))

class Set_func_coll_get(AnnotationObject):
    """Set_func_coll_get annotation"""
    def __init__(self, function, key1, key2):
        super().__init__(function)
        self.key1 = key1
        self.key2 = key2
    def translate(self):
        return 'SET_FUNC_COLL_GET(%s,%s)'%(parse_translate(self.key1), parse_translate(self.key2))

class Set_func_map_put(AnnotationObject):
    """Set_func_map_put annotation"""
    def __init__(self, function, key1, key2, key3):
        super().__init__(function)
        self.key1 = key1
        self.key2 = key2
        self.key3 = key3
    def translate(self):
        return 'SET_FUNC_MAP_PUT(%s,%s,%s)'% \
            (parse_translate(self.key1), parse_translate(self.key2), parse_translate(self.key3))


class Set_func_map_get(AnnotationObject):
    """Set_func_map_get annotation"""
    def __init__(self, function, key1, key2):
        super().__init__(function)
        self.key1 = key1
        self.key2 = key2
    def translate(self):
        return 'SET_FUNC_MAP_GET(%s,%s)'%(parse_translate(self.key1), parse_translate(self.key2))


class Set_func_str_get(AnnotationObject):
    """Set_func_str_get annotation"""
    def __init__(self, function, key1, key2):
        super().__init__(function)
        self.key1 = key1
        self.key2 = key2
    def translate(self):
        return "SET_FUNC_STR_GET(%s,%s)"%(parse_translate(self.key1), parse_translate(self.key2))

class Copy_tag(AnnotationObject):
    """Copy_tag annotation"""
    def __init__(self, function, key1, key2):
        super().__init__(function)
        self.key1 = key1
        self.key2 = key2
    def translate(self):
        return "COPY_TAG(%s,%s)"%(parse_translate(self.key1), parse_translate(self.key2))

class Or_tag(AnnotationObject):
    """Or_tag annotation"""
    def __init__(self, function, key1, key2):
        super().__init__(function)
        self.key1 = key1
        self.key2 = key2
    def translate(self):
        return "OR_TAG(%s,%s)"%(parse_translate(self.key1), parse_translate(self.key2))

class Fsm_use(AnnotationObject):
    """Fsm_use annotation"""
    def __init__(self, function, err_name):
        super().__init__(function)
        self.err_name = err_name
    def translate(self):
        return 'FSM_USE("%s")'%self.err_name

class Set_tag_attr(AnnotationObject):
    """Set_tag_attr annotation"""
    def __init__(self, function, key1, key2, tag, attr):
        super().__init__(function)
        self.key1 = key1
        self.key2 = key2
        self.tag = tag
        self.attr = attr

    def translate(self):
        return (
            'SET_TAG_ATTR(%s,%s,"%s","%s")'%
            (parse_translate(self.key1), parse_translate(self.key2), self.tag, self.attr)
        )

ANNOTATION_API = {
    "TAG": Tag,
    "ASSERT": Assert,
    "SET_IMPLICIT_ASSIGN": Set_implicit_assign,
    "SET_PARM_MOD": Set_parm_mod,
    "SET_PARM_DEREF": Set_parm_deref,
    "SET_FUNC_MAY_SLEEP": Set_func_may_sleep,
    "SET_ATOMIC_REGION_BEGIN": Set_atomic_region_begin,
    "SET_ATOMIC_REGION_END": Set_atomic_region_end,
    "SET_FUNC_ATOMIC": Set_func_atomic,
    "SET_FUNC_SHUTDOWN": Set_func_shutdown,
    "SET_FUNC_COLL_APPEND": Set_func_coll_append,
    "SET_FUNC_COLL_REMOVE": Set_func_coll_remove,
    "SET_FUNC_COLL_GET": Set_func_coll_get,
    "SET_FUNC_MAP_PUT": Set_func_map_put,
    "SET_FUNC_MAP_GET": Set_func_map_get,
    "SET_FUNC_STR_GET": Set_func_str_get,
    "COPY_TAG": Copy_tag,
    "OR_TAG": Or_tag,
    "FSM_USE": Fsm_use,
    "SET_TAG_ATTR": Set_tag_attr
}
