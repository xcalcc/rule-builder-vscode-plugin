"""
annotation_api

API available for annotation functionality
"""

import re
from .condition_parse import ConditionParse
from common.XcalLogger import XcalLogger
from common.XcalException import XcalException
from ruleBuildService.config import ErrorNo

# pylint: disable=too-few-public-methods, simplifiable-if-statement, missing-super-argument, invalid-name


class FuncParseError(Exception):
    """error encountered during function parsing"""
    pass

def parse_translate(expr):
    """short-hand translation

    using parsing of raw expression string and translate them
    into format specified in resources/template.h

    Args:
        expr (str): expression to be translated
    Returns:
        str: string containing the API short-hand form as described in
            template.h
    """
    return ConditionParse.parse(expr).translate()

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
    def __init__(self, sig, lang):
        log = XcalLogger("annotation_api", "__init__")
        log.debug("__init__", "parsing function %s" % sig)

        try:
            cls_matcher = re.search(r'(?<=<).*(?=:)', sig)
            assert (cls_matcher is not None), "Can't match class name: signature: %s"%sig
            self.sig = sig
    
            self.cls_name = cls_matcher.group(0)
            log.debug("__init__", "class name = %s" % self.cls_name)

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
            log.debug("__init__", "method signature = %s" % method_sig)
            
            if lang == "java":
                ret_matcher = re.search(r'^.*(?= )', method_sig)
                self.ret_type = ret_matcher.group(0)
            else:
                ret_matcher = re.search(r'(.* (\*)?)(?=\w+\()', method_sig)
                self.ret_type = ret_matcher.group(1).strip()
            log.debug("__init__", "return type = %s" % self.ret_type)

            if lang == "java":
                met_name_matcher = re.search(r'(?<= ).*(?=\()', method_sig)
            else:
                met_name_matcher = re.search(r'(\*)?(\S+)(?=\()', method_sig)

            assert (met_name_matcher is not None), \
                "can't match method name, method signature: %s"%method_sig

            if lang == "java":
                self.met_name = met_name_matcher.group(0)
            else:
                self.met_name = met_name_matcher.group(2)
            log.debug("__init__", "method name = %s" % self.met_name)
            args_matcher = re.search(r'(?<=\().*(?=\))', method_sig)

            assert (args_matcher is not None), \
                "Can't match arg list, method signature: %s"% method_sig
            self.args = args_matcher.group(0).split(',')
            log.debug("__init__", "arguments = %s" % self.args)
            interface_matcher = re.search(r'^(I)', sig)
            if interface_matcher:
                self.is_interface = True
            else:
                self.is_interface = False
            log.debug("__init__", "is interface = %s" % self.is_interface)

        except AssertionError:
            raise XcalException("annotation_api", "__init__", "function: %s not parseable" % sig,
                                err_code=ErrorNo.E_INVALID_FUNCTION_FORMAT)


class AnnotationObject(object):
    """Parent class of all annotation API"""
    def __init__(self, function, lang = "java"):
        self.parser = FuncParse(function, lang)

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
        if self.condition == "true" or self.condition == "false":   
            return 'RBC_ASSERT(%s,"%s")'%(self.condition, self.error)
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

class Eval_tag(AnnotationObject):
    """Eval_tag annotation"""
    def __init__(self, function, key1, key2):
        super().__init__(function) 
        self.key1 = key1
        self.key2 = key2
    def translate(self):
        return(
            'EVAL_TAG(%s,%s)'%
            (parse_translate(self.key1), parse_translate(self.key2))
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
    "SET_TAG_ATTR": Set_tag_attr,
    "EVAL_TAG": Eval_tag
}
