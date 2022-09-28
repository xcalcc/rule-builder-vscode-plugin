#!/usr/bin/python3
"""
condition_parse

class to take string input of operation API from input (.mi) file.
Operation to return string ready for translation process
"""

from common.XcalLogger import XcalLogger
from common.XcalException import XcalException
from ruleBuildService.config import ErrorNo

class APIError(Exception):
    """API Call error

    Exception raised when an API is incorrectly called
    """
    pass

class APINotDefined(Exception):
    """Exception of API not found

    Exception raised when an API is called eventhough it is not listed
    """
    pass

class ParseNode(object):
    """Node structure to hold function structure

    Node level of tree structure to parse a compound API (i.e. not(this())).
    The structure is only parent->child link. Insertion is done on recursive pattern

    Args:
        content (str): The raw (complete) string passed to the node to be parsed
        api (bool): Checking whether this node is an API
        references (str): reference (if any) for translation later on

    Attributes:
        content (str): string of the node representation
        children (ParseNode): children nodes
    """

    API = [
        "not", "is_tag_attr_set", "and", "or", "eq", "assert",
        "tag", "arg", "this", "return", "none", "pre_call",
        "is_parm_tainted", "func_may_not_return", "var", "value"
    ]

    TRANSLATION = {
        "not": "NOT",
        "arg": "GET_ARG",
        "": "",
        "is_tag_attr_set": "RBC_IS_TAG_ATTR_SET",
        "this": "THIS_POINTER",
        "assert": "RBC_ASSERT",
        "return": "GET_RET",
        "tag": "RBC_SET_TAG",
        "pre_call": "PRE_CALL",
        "is_parm_tainted": "IS_PARM_TAINTED",
        "func_may_not_return": "FUNC_MAY_NOT_RETURN",
        "or": "OR",
        "and": "AND",
        "eq": "EQ",
        "var": "GET_VAR",
        "value": "GET_VALUE"
    }

    def __init__(self, content, api=False, references=None):
        # _logger.debug("Node intialisation with %s"%content)
        self.children = []
        if content == "none":
            self.content = content
            return
        start = content.find('(')
        end = content.rfind(')')

        if api:
            if start == -1 or end == -1:
                raise XcalException("condition_parse", "__init__", "Incorrect API call: %s" % content,
                                    err_code=ErrorNo.E_INCORRECT_API_CALL)
            cmd = content[:start]
            # ==== change ====
            self.content = cmd
            children = content[start+1:end].split(',') # split does not properly parse args
            idx = 0
            curr = min(1, len(children))
            while (curr < len(children)): # split may separate children arguments
                # get a count of all the parentheses
                paren_count = children[idx].count('(') - children[idx].count(')')
                if paren_count: # paren count uneven, must be child arg split
                    children[idx] += "," + children[curr]
                else:
                    idx += 1
                    children[idx] = children[curr]
                curr += 1
            self.add_children(children[:idx + 1])
            # === ============
            if cmd not in ParseNode.API:
                raise XcalException("condition_parse", "__init__", "api: %s not recognised" % cmd,
                                    err_code=ErrorNo.E_API_NOT_EXIST)
        # if API not necessary, look at whether or not it can branch again or not
        elif start == -1:
            self.content = content
        elif ':' in content: # means there is function call
            self.content = content
        else:
            # contains (, seems to be API
            if end == -1:
                raise XcalException("condition_parse", "__init__", "Incorrect API call",
                                    err_code=ErrorNo.E_INCORRECT_API_CALL)
            elif ':' in content:
                self.content = content
            else:
                parent = content[:start]
                children = content[start+1:end]
                if parent not in ParseNode.API:
                   raise XcalException("condition_parse", "__init__", "api: %s not recognised" % parent,
                                    err_code=ErrorNo.E_API_NOT_EXIST)
                self.content = parent
                parts = children.split(',')  # each correspond to something
                self.add_children(parts)

    def api_add_pre_call(self, parts):
        # _logger.debug("children of PRE_CALL api")
        form = [False]
        # ensure all into 1
        parts = [','.join(parts)]
        if len(parts) != len(form):
            # _logger.error("Wrong usage of PRE_CALL api")
            raise XcalException("condition_parse", "api_add_pre_call", "Incorrect API call for Pre_call",
                                    err_code=ErrorNo.E_INCORRECT_API_CALL)
        for i in range(len(parts)):
            self.children.append(ParseNode(parts[i], form[i]))

    def api_add_return(self, parts):
        # _logger.debug("children of GET_RET api")
        form = [False]
        if len(parts) != len(form):
            # _logger.error("Wrong usage of GET_RET api")
            raise XcalException("condition_parse", "api_add_return", "Incorrect API call for Get_ret",
                                    err_code=ErrorNo.E_INCORRECT_API_CALL)
        if parts[0] != "":
            # _logger.error("Wrong usage of GET_RET api")
            raise XcalException("condition_parse", "api_add_return", "Incorrect API call for Get_ret",
                                    err_code=ErrorNo.E_INCORRECT_API_CALL)
        for i in range(len(parts)):
            self.children.append(ParseNode(parts[i], form[i]))

    def api_add_not(self, parts):
        # _logger.debug("children of NOT api")
        # NOT API: RBC_ENGINE.Not(API())
        parts = [",".join(parts)]
        form = [True]
        if len(parts) != len(form):
            # _logger.error("wrong usage of NOT api")
            raise XcalException("condition_parse", "api_add_not", "Incorrect API call for Not",
                                    err_code=ErrorNo.E_INCORRECT_API_CALL)
        for i in range(len(parts)):
            self.children.append(ParseNode(parts[i], form[i]) )

    def api_add_is_attr_set(self, parts):
        # _logger.debug("children of IS_ATTR_SET api")
        form = [True, False, False]
        if len(parts) != len(form):
            # _logger.error("wrong usage of IS_ATTR_SET api")
            raise XcalException("condition_parse", "api_add_is_attr_set", "Incorrect API call for Is_tag_attr_set",
                                    err_code=ErrorNo.E_INCORRECT_API_CALL)
        for i in range(len(parts)):
            self.children.append(ParseNode(parts[i], form[i]))

    def api_add_this(self, parts):
        # _logger.debug("children of THIS_POINTER api")
        form = [False]
        if len(parts) != len(form):
            # _logger.error("Wrong usage of THIS_POINTER api")
            raise XcalException("condition_parse", "api_add_this", "Incorrect API call for Get_this_pointer",
                                    err_code=ErrorNo.E_INCORRECT_API_CALL)
        if parts[0] != "":
            # _logger.error("Wrong usage of THIS_POINTER api")
            raise XcalException("condition_parse", "api_add_this", "Incorrect API call for Get_this_pointer",
                                    err_code=ErrorNo.E_INCORRECT_API_CALL)
        for i in range(len(parts)):
            self.children.append(ParseNode(parts[i], form[i]))

    def api_add_arg(self, parts):

        form = [False]
        if len(parts) != len(form):
            raise XcalException("condition_parse", "api_add_arg", "Incorrect API call for Get_arg",
                                    err_code=ErrorNo.E_INCORRECT_API_CALL)
        for i in range(len(parts)):
            self.children.append(ParseNode(parts[i], form[i]))

    def api_add_tag(self, parts):
        form = [True, False]
        if len(parts) != len(form):
            # _logger.error("Wrong usage of RBC_SET_TAG API")
            raise XcalException("condition_parse", "api_add_tag", "Incorrect API call for Set_tag",
                                    err_code=ErrorNo.E_INCORRECT_API_CALL)
        for i in range(len(parts)):
            self.children.append(ParseNode(parts[i], form[i]))

    def api_is_parm_tainted(self, parts):
        form = [True]
        if len(parts)!=len(form):
            raise XcalException("condition_parse", "api_is_parm_tainted", "Incorrect API call for Is_parm_tainted",
                                    err_code=ErrorNo.E_INCORRECT_API_CALL)
        for i in range(len(parts)):
            self.children.append(ParseNode(parts[i], form[i]))

    def api_add_assert(self, parts):
        form = [False, False]
        # divide into 2 parts
        parts = [",".join(parts[:-1]), parts[-1]]

        if len(parts) != len(form):
            # _logger.debug("%s is expected, given %s"%(len(form), len(parts)))
            # _logger.debug("parts: %s"%parts)
            # _logger.error("Wrong usage of RBC_ASSERT API")
            raise XcalException("condition_parse", "api_add_assert", "Incorrect API call for Rbc_assert",
                                    err_code=ErrorNo.E_INCORRECT_API_CALL)
        for i in range(len(parts)):
            self.children.append(ParseNode(parts[i], form[i]))

    def api_func_may_not_return(self, parts):
        form = [True]
        if len(parts)!=len(form):
            raise XcalException("condition_parse", "api_func_may_not_return", "Incorrect API call for Func_may_not_return",
                                    err_code=ErrorNo.E_INCORRECT_API_CALL)
        for i in range(len(parts)):
            self.children.append(ParseNode(parts[i], form[i]))

    def api_add_and(self, parts):
        form = [True, True]
        if len(parts) != len(form):
            # _logger.error("Wrong usage of RBC_SET_TAG API")
            raise XcalException("condition_parse", "api_add_and", "Incorrect API call for And",
                                    err_code=ErrorNo.E_INCORRECT_API_CALL)
        for i in range(len(parts)):
            self.children.append(ParseNode(parts[i], form[i]))

    def api_add_or(self, parts):
        form = [True, True]
        if len(parts) != len(form):
            # _logger.error("Wrong usage of RBC_SET_TAG API")
            raise XcalException("condition_parse", "api_add_or", "Incorrect API call for Or",
                                    err_code=ErrorNo.E_INCORRECT_API_CALL)
        for i in range(len(parts)):
            self.children.append(ParseNode(parts[i], form[i]))
    
    def api_add_eq(self, parts):
        form = [True, True]
        if len(parts) != len(form):
            # _logger.error("Wrong usage of RBC_SET_TAG API")
            raise XcalException("condition_parse", "api_add_eq", "Incorrect API call for Eq",
                                    err_code=ErrorNo.E_INCORRECT_API_CALL)
        for i in range(len(parts)):
            self.children.append(ParseNode(parts[i], form[i]))
    
    def api_add_var(self, parts):
        form = [False]
        if len(parts)!=len(form):
            raise XcalException("condition_parse", "api_add_var", "Incorrect API call for Variable",
                                    err_code=ErrorNo.E_INCORRECT_API_CALL)
        for i in range(len(parts)):
            self.children.append(ParseNode(parts[i], form[i]))

    def api_add_value(self, parts):
        form = [False]
        if len(parts)!=len(form):
            raise XcalException("condition_parse", "api_add_value", "Incorrect API call for Get_value",
                                    err_code=ErrorNo.E_INCORRECT_API_CALL)
        for i in range(len(parts)):
            self.children.append(ParseNode(parts[i], form[i]))

    def add_children(self, parts):
        # _logger.debug("Adding %s as children to %s"%(parts, self.content))
        api = self.content.strip()
        # depending on api, check if parts fill the criteria
        if api == 'not':
            self.api_add_not(parts)
        elif api == 'arg':
            self.api_add_arg(parts)
        elif api == 'is_tag_attr_set':
            self.api_add_is_attr_set(parts)
        elif api == 'this':
            self.api_add_this(parts)
        elif api == 'return':
            self.api_add_return(parts)
        elif api == 'tag':
            self.api_add_tag(parts)
        elif api == 'assert':
            self.api_add_assert(parts)
        elif api == 'pre_call':
            self.api_add_pre_call(parts)
        elif api == 'is_parm_tainted':
            self.api_is_parm_tainted(parts)
        elif api == 'func_may_not_return':
            self.api_func_may_not_return(parts)
        elif api == 'and':
            self.api_add_and(parts)
        elif api == 'or':
            self.api_add_or(parts)
        elif api == 'eq':
            self.api_add_eq(parts)
        elif api == 'var':
            self.api_add_var(parts)
        elif api == 'value':
            self.api_add_value(parts)
        else:
            raise XcalException("condition_parse", "add_children", "API: %s not exist" % api,
                                err_code=ErrorNo.E_API_NOT_EXIST)

    def translate(self, references=None):
        '''
        tree structure->string recursive
        might need to include reading from references
        '''
        # _logger.debug("Translating content %s", self.content)
        if len(self.children) == 0:
            # not API, so return pure string
            # _logger.debug("%s contains no children"%self.content)
            return self.content
        elif self.content == 'pre_call':
            return '%s("%s")'%(ParseNode.TRANSLATION[self.content], ParseNode.find_mangle_func_name_mult(self.children[0].content, *references))
        elif self.children[0].content == "":
            # _logger.debug("%s contains empty children"%self.content)
            return ParseNode.TRANSLATION[self.content]
        else:
            return '%s(%s)'%(ParseNode.TRANSLATION[self.content], ",".join([i.translate(references) for i in self.children]))

    @staticmethod
    def find_mangle_func_name(fname, ref_file):
        '''
        find mangled function name based on function name
        '''
        try:
            f = open(ref_file, 'r')
        except FileNotFoundError:
            raise XcalException("condition_parse", "find_mangle_func_name", "file: %s not found" % ref_file,
                                err_code=ErrorNo.E_RESOURCE_NOT_FOUND)
        lines = f.readlines()
        for line in lines:
            splits = line.strip().split('|')
            if "<%s>"%fname == splits[0]:
                return splits[1]
        f.close()
        return None

    @staticmethod
    def find_mangle_func_name_mult(fname, *files):
        '''
        reading from multiple files
        '''
        # _logger.debug("Finding mangle name for %s"%fname)
        f_to_read = list(files)
        for i in f_to_read:
            name = ParseNode.find_mangle_func_name(fname, i)
            if name:
                return name
        return None


class ConditionParse:
    """Main parsing class functionality

    serves as tree root for the whole structure
    """
    @classmethod
    def parse(cls, condition):
        """parsing string

        parse the raw complete string of api calls one after the other

        Args:
            condition (str): Raw string to be translated into compilable string
        Returns:
            ParseNode: the root node containing every structure
        """
        # _logger.debug("Parsing condition: %s", condition)
        with XcalLogger("ConditionParse", "parse") as log:
            log.debug("parse", "parsing condition: %s" % condition)
        root = ParseNode(condition, True)
        return root