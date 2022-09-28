#!/usr/bin/python3

"""
API to help Declaring rule information
store rule information in separate file and have all of them gathered
"""

import sys
import re
import os
import logger

logger = logger.retrieve_log()

class RuleInfo:
    def __init__(self, rulecode, ruleset, information):
        self.rulecode = rulecode
        self.ruleset = ruleset
        self.info = information
    
    def __repr__(self):
        return "(%s, %s, %s)"%(self.rulecode, self.ruleset, self.info)

class DeclareRule:
    '''
    store all rule declaration and dump it in a file
    '''
    rules = []

    @classmethod
    def add_entry_raw(cls, line):
        if not isinstance(line, str):
            logger.error("wrong data type")
            raise TypeError("expected a str type")  
        parts = line.split('|') 

        cls.add_entry(parts[0], *parts[1:])

    @classmethod
    def add_entry(cls, action, *fields):
        '''
        action: supposed to be of type DECLARE
        ''' 
        if action != "DECLARE":
            logger.error("Incorrect Action passed")
            return
        # add to list of rule declarations
        rule = RuleInfo(*fields)
        logger.info("Adding a declaration of %s"%rule)
        cls.rules.append(rule) 
    
    @classmethod
    def write_header(cls, out_file):
        logger.debug("Writing Header")
        out_file.write("IMPORT1\nIMPORT2\n\n") # header  
        out_file.write("CLASS(DECLARE_RULE)\n\n")

    @classmethod
    def write_rule_desc(cls, out_file, rule):
        '''
        writing a rule: RuleInfo
        '''
        logger.debug("writing rule description for %s"%rule) 
        # eliminate - for rule code
        rulecode = rule.rulecode.replace('-','_') 
        out_file.write("        START_RULE(%s)\n"%rulecode) 
        out_file.write('            DECLARE_RULE_INFO("%s","%s","%s")\n'%(rule.rulecode, rule.ruleset, rule.info))
        out_file.write("        END_RULE\n") 
         
    @classmethod
    def write_class_close(cls, out_file):
        out_file.write("END_RULE\n") 

    @classmethod
    def dump(cls, rb_loc, out_dir='.'):
        '''
        dump the content of rule declarations into this file
        rb_loc: path to rb_backend directory
        '''
        if len(cls.rules) == 0:
            return
        #file_name = "DECLARE_RULE.h" # set it as .h first for multiple-conversion
        file_name = os.path.join(out_dir, 'DECLARE_RULE.h')
        out_file = open(file_name, 'w')
        logger.debug("Dumping rule declarations to %s"%file_name)

        # copy template file
        template_h = open(os.path.join(rb_loc, 'lib/translator/template.h'), 'r')
        for l in template_h.readlines():
            out_file.write(l) 
        
        cls.write_header(out_file)
         
        # for every entry, create rule_desc
        for rule in cls.rules:
            cls.write_rule_desc(out_file, rule)
        
        cls.write_class_close(out_file)
        # Closing all opened files
        logger.debug("Closing files")
        template_h.close()
        out_file.close()
