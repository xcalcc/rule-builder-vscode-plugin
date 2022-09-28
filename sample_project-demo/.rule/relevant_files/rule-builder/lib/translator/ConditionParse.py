#!/usr/bin/python3

"""
ConditionParse 
class that takes string input of condition in input (.mi) file.
Operation should return a string ready to be translated

translate API calls accordingly if needed for other uses
"""

import logger
logger = logger.retrieve_log()

class APIError(Exception):
    pass

class APINotDefined(Exception):
    pass

class ParseNode:

    API = [
    "not", "is_tag_attr_set", "and", "or", "eq", "assert",
    "tag", "arg", "this", "return", "none", "pre_call"
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
        "pre_call": "PRE_CALL"
    }
                      
    def __init__(self, content, api=False, references=None):
        '''
        condition: raw string of condition
        api: flag whether or not an api is required from this condition
        references: possible reference to be included
        '''

        logger.debug("Node intialisation with %s"%content)
        self.children = []
        if content == "none":
            self.content = content
            return
        start = content.find('(')
        end = content.rfind(')')
        if api:
            if start == -1 or end == -1:
                logger.error("Incorrect API calls")
                raise APIError("%s"%content) 
            cmd = content[:start]
            # ==== change====
            self.content = cmd
            children = content[start+1:end].split(',')
            self.add_children(children) 
            # === ============
            if cmd not in ParseNode.API:
                logger.error("%s not recognised as API"%cmd)
                raise APIError()
        # if API not necessary, look at whether or not it can branch again or not
        elif start == -1:
            # not api, treat it as just a string 
            self.content = content                      
        elif ':' in content: # means there is function call
            self.content = content
        else:
            # contains (, seems to be API
            if end == -1:
                logger.error("Incorrect format")  
                raise APIError()
            elif ':' in content:
                self.content = content
            else:
                logger.debug("API detected")
                parent = content[:start]
                children = content[start+1:end] 
                logger.debug("Parent: %s, children: %s"%(parent, children))
                if parent not in ParseNode.API:
                    logger.error("%s not recognised as API"%parent) 
                    raise APIError()
                self.content = parent
                parts = children.split(',')  # each correspond to something
                self.add_children(parts)

    def api_add_pre_call(self, parts):
        logger.debug("children of PRE_CALL api")
        form = [False]
        # ensure all into 1
        parts = [','.join(parts) ]
        if len(parts) != len(form):
            logger.error("Wrong usage of PRE_CALL api")
            raise APIError()
        for i in range(len(parts)):
            self.children.append(ParseNode(parts[i], form[i]))

    def api_add_return(self, parts):
        logger.debug("children of GET_RET api")
        form = [False]
        if len(parts) != len(form):
            logger.error("Wrong usage of GET_RET api")
            raise APIError()
        if parts[0] != "":
            logger.error("Wrong usage of GET_RET api")
            raise APIError()
        for i in range(len(parts)):
            self.children.append(ParseNode(parts[i], form[i]))
    
    def api_add_not(self, parts):
        logger.debug("children of NOT api")     
        # NOT API: RBC_ENGINE.Not(API())
        parts = [",".join(parts)]
        form = [True] 
        if len(parts) != len(form):
            logger.error("wrong usage of NOT api")
            raise APIError() 
        for i in range(len(parts)):
            self.children.append(ParseNode(parts[i], form[i]) )
    
    def api_add_is_attr_set(self, parts):
        logger.debug("children of IS_ATTR_SET api") 
        form = [True, False, False]
        if len(parts) != len(form):
            logger.error("wrong usage of IS_ATTR_SET api")
            raise APIError()
        for i in range(len(parts)):
            self.children.append(ParseNode(parts[i], form[i])) 

    def api_add_this(self, parts):
        logger.debug("children of THIS_POINTER api")
        form = [False]
        if len(parts) != len(form):
            logger.error("Wrong usage of THIS_POINTER api") 
            raise APIError()
        if parts[0] != "":
            logger.error("Wrong usage of THIS_POINTER api")
            raise APIError()
        for i in range(len(parts)):
            self.children.append(ParseNode(parts[i], form[i]))
        
    def api_add_arg(self, parts):
        logger.debug("children of ARG api") 

        form = [False]
        if len(parts) != len(form):
            logger.error("Wrong usage of ARG API")
            raise APIError()
        for i in range(len(parts)):
            self.children.append(ParseNode(parts[i], form[i]))
             
    def api_add_tag(self, parts):
        logger.debug("children of RBC_SET_TAG API")
        form = [True, False]
        if len(parts) != len(form):
            logger.error("Wrong usage of RBC_SET_TAG API")
            raise APIError()
        for i in range(len(parts)):
            self.children.append(ParseNode(parts[i], form[i]))
    
    def api_add_assert(self, parts):
        logger.debug('children of RBC_ASSERT')
        form  = [True, False]
        # divide into 2 parts
        parts = [",".join(parts[:-1]), parts[-1]]

        if len(parts) != len(form):
            logger.debug("%s is expected, given %s"%(len(form), len(parts)))
            logger.debug("parts: %s"%parts)
            logger.error("Wrong usage of RBC_ASSERT API")
            raise APIError()
        for i in range(len(parts)):
            self.children.append(ParseNode(parts[i], form[i]))

    def add_children(self, parts):
        logger.debug("Adding %s as children to %s"%(parts, self.content))
        api = self.content 
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
        else:
            raise APINotDefined()
    
    def translate(self, references=None):
        '''
        tree structure->string recursive
        might need to include reading from references
        '''  
        logger.debug("Translating content %s"%self.content)
        if len(self.children) == 0:
            # not API, so return pure string
            logger.debug("%s contains no children"%self.content)
            return self.content
        elif self.content == 'pre_call':
            return '%s("%s")'%(ParseNode.TRANSLATION[self.content], ParseNode.find_mangle_func_name_mult(self.children[0].content, *references))
        elif self.children[0].content == "":
            logger.debug("%s contains empty children"%self.content)
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
        except FileNotFoundError as e:
            logger.error("reference file not found")
            raise FileNotFoundError()
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
        logger.debug("Finding mangle name for %s"%fname)
        f_to_read = list(files)
        for i in f_to_read:
            name = ParseNode.find_mangle_func_name(fname, i)
            if name:
                return name 
        return None


class ConditionParse:

    def __init__(self):
        pass
    
    @classmethod
    def parse(cls, condition): 
        '''
        parse condition input into string 
        ready for translation in .h file
        '''
        logger.debug('---------------')
        logger.debug("Parsing condition: %s"%condition)
        root = ParseNode(condition, True)
        return root
