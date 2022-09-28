"""
declare_rule

API for storing rule declaration
storing rule information in separate file combine altogether
"""

import os
#from ..logger import Logger

from . import template_h_path
from common.XcalException import XcalException
from common.XcalLogger import XcalLogger
from ruleBuildService.config import ErrorNo

# _logger = Logger.retrieve_log() # pylint: disable=invalid-name

class RuleInfo(object):
    """rule information object

    contains minimum information on the rule information, to be used as
    rbc_engine.Declare_rule(..) API.

    Attributes:
        rulecode (str): rule code i.e. ERR01-J
        ruleset (str): rule set that contains this rule information i.e. CUSTOM
        info (str): short description for the info

    Args:
        rulecode (str): rule code i.e. ERR01-J
        ruleset (str): rule set that contains this rule information i.e. CUSTOM
        information (str): deccription for this rule information
    """
    # pylint: disable=too-few-public-methods
    def __init__(self, rulecode, ruleset, information):
        self.rulecode = rulecode
        self.ruleset = ruleset
        self.info = information

    def __repr__(self):
        return "(%s, %s, %s)"%(self.rulecode, self.ruleset, self.info)

class DeclareRule(object):
    """rule declaration class

    storing all rule information objects ready to be dumped into a file
    only dump file when there are entries
    """
    rules = []

    def __init__(self):
        pass

    @classmethod
    def clear(cls):
        '''clearing entry of rules for reset'''
        cls.rules = [] # empty the rules

    @classmethod
    def add_entry_raw(cls, line):
        """raw addition to entries

        adding raw string to be parsed/split and psas to add_entry function

        Args:
            line (str): complete unparsed-string
        Raises:
            TypeError: if line is not of type string
        """
        parts = line.split('|')

        cls.add_entry(parts[0], *parts[1:])

    @classmethod
    def add_entry(cls, action, *fields):
        """adding parsed string

        process all the arguments passed, turn them into RuleInfo
        object and add into list of entries.

        Args:
            action (str): supposed to be of constant "DECLARE"
            fields: list of fields to be used as argument to ame RuleInfo object
        """
        if action != "DECLARE":
            raise XcalException("declare_rule", "add_entry", "The Field is not of type DECLARE_RULE",
                                err_code=ErrorNo.E_INCORRECT_API_CALL)

        # add to list of rule declarations
        rule = RuleInfo(*fields) # pylint: disable=no-value-for-parameter
        cls.rules.append(rule)

    @classmethod
    def write_header(cls, out_file):
        """writing header file

        imports and class declaration printed into the header file

        Args:
            out_file (str): path to the output file
        """
        out_file.write("IMPORT1\nIMPORT2\n\n") # header
        out_file.write("CLASS(DECLARE_RULE)\n\n")

    @classmethod
    def write_rule_desc(cls, out_file, rule):
        """writing the rule description

        writing the declaration into the output file
        regarding the rule information stored as RuleInfo

        Args:
            out_file (str): path to output file
            rule (RuleInfo): RuleInfo object that stores information
        """
        # eliminate - for rule code
        rulecode = rule.rulecode.replace('-', '_')
        out_file.write("        START_RULE(%s)\n"%rulecode)
        out_file.write('            DECLARE_RULE_INFO("%s","%s","%s")\n'%(
            rule.rulecode, rule.ruleset, rule.info))
        out_file.write("        END_RULE\n")

    @classmethod
    def write_class_close(cls, out_file):
        """end class

        writing out final declaratio of class

        Args:
            out_file (str): output path of the file
        """
        out_file.write("END_RULE\n")

    @classmethod
    def dump(cls, out_dir='.'):
        """dumping info to output

        takes all entry in the entries list of rule information and
        write out the information one by one into designated output file

        Args:
            out_dir (str): output directory
        Raises:
            FileNotFoundError: if out_dir doesn't exist
        """
        with XcalLogger("declare_rule", "dump") as log:
            if not cls.rules: # if no entry just return
                log.debug("dump", "no rules entry listed")
                return
            file_name = os.path.join(out_dir, 'DECLARE_RULE.h')
            out_file = open(file_name, 'w')

            # copy template file
            template_h = open(template_h_path, 'r') # copy template file content set as header
            for line in template_h.readlines():
                out_file.write(line)

            cls.write_header(out_file)

            # for every entry, create rule_desc
            for rule in cls.rules:
                cls.write_rule_desc(out_file, rule)

            cls.write_class_close(out_file)
            # Closing all opened files
            log.debug("dump", "closing all opened resources")
            # _logger.debug("Closing files")
            template_h.close()
            out_file.close()
