"""
APIs to expose rule building
Takes in input files from user and convert them to .a/.udr

files:
.mi, .h, .jar -> .a/.udr files
"""
# ruleBuildService related
import logging
import os
import subprocess
import time
from ruleBuildService.translator.read import read_file, create_fsm, \
        read_fsm, read_annotation # reading utilities
from ruleBuildService.translator.rule_file_gen import RuleFileGen
from ruleBuildService.translator.annotation import Annotation
from ruleBuildService.compile import Compile
# commons
from common.XcalLogger import XcalLogger
from common.XcalException import XcalException


class RuleBuildService:
    """RuleBuildService main component

    Service to provide users the API to create their own rules

    Args:
        lang(str): target rule programming language
        out_dir (str): path to output directory
        rule (str): label for the rule
    Attributes:
        lang (str): target programming language for rule
        input_files (list): list of path to input files
        references (list): list of (.mi) reference file
        logger (XcalLogger): logger object
        dependencies (list): list of file dependencies (ie. .jar file)
        rule (str): label of rule
    """
    def __init__(self, lang=None, out_dir='output/', rule='rule'):
        self.lang = lang
        self.input_files = []
        self.references = []
        self.dependencies = []
        self.out_dir = out_dir
        self.logger = XcalLogger("RuleBuildService", "__init__")
        self._generated = []
        self.rule = rule  # rule name

    def set_language(self, lang):
        """set programming language

        Args:
            lang (str): programming language
        self.lang = lang
        """
        self.logger.debug("set_language", "setting language to %s" % lang)
        self.lang = lang

    def add_inputs(self, *inputs):
        """adding .mi (for user input)

        .mi text file that is used for showing the user input
        for both FSM or Annotation is to be passed. There could be multiple

        Args:
            *inputs (str): path to input file
        """
        for in_file in inputs:
            self.logger.debug("add_input", "adding input: %s" % in_file)
            self.input_files.append(in_file)

    def add_references(self, *references):
        """adding reference files (.mi)

        .aside from .mi input file, .mi can also be a reference file
        especially if the rule is for Java programming language. Reference file
        contains the mapping of normal function name to mangled function name

        Args:
            *references (str): path to reference file
        """
        for in_ref in references:
            self.logger.debug("add_references", "adding reference file: %s" % in_ref)
            self.references.append(in_ref)

    def add_dependencies(self, *dependencies):
        """adding dependencies (i.e. .jar file)
        
        Args:
            dependencies (str): path to dependency file
        """
        for in_dep in dependencies:
            self.logger.debug("add_dependencies", "adding dependency file: %s" % in_dep)
            self.dependencies.append(in_dep)

    def output_to(self, out_dir):
        """locate where to generate output

        Place to hold all temporary files and intermediate generated files
        to a certain output

        Args:
            out_dir (str): path to output directory
        """
        self.logger.debug("output_to", "location of output is in : %s" % out_dir)
        self.out_dir = out_dir

    def name_rule(self, rule):
        """naming the rule

        Set the rule name to rule
        Args:
            rule (str): rule name
        """
        self.logger.debug("name_rule", "naming the rule to: %s" % rule)
        self.rule = rule

    def translate(self):
        """translation phase (phase 1)

        from input .mi file, turn the user input in text format into a rule file
        of a specific target language. all will be turned into a .h file before compiling
        them into a .java/.cxx file
        """
        if not self.input_files: # no input files
            self.logger.warn("translate", "no input files are passed, aborting..")
            return
        try:
            self.logger.debug("translate", "Translation phase start...")
            self.logger.debug("translate", "DEBUGEDEBUG %s" % self.references)
            annotator = Annotation() # initialise annotator

            fsm_list = []
            for f_input in self.input_files:
                lines = read_file(f_input)
                fsm, annotator = create_fsm(lines, self.rule, annotator)
                fsm_list.append(fsm) # store the fsm

            # merge all fsm into 1
            main_fsm = fsm_list[0]
            if len(fsm_list) > 1:
                self.logger.debug("translate", "merging ongoing")
                for i in range(1, len(fsm_list)):
                    main_fsm.merge(fsm_list[i]) # 1 by 1 merge

            self.logger.debug("translate", "File generation phase")
            ref_str = ':'.join(self.references) # turn references to acceptable string:
            file_gen = RuleFileGen(self.lang, ref_str, self.out_dir, name=self.rule) # to generate the file
            file_gen.attach_fsm(main_fsm)
            file_gen.attach_annotations(annotator)
            generated_files = file_gen.generate()
            self.logger.info("translate", "translation phase success")
            self.logger.debug("translate", "generated files: %s" % generated_files)
            self._generated += generated_files # list addition
            return

        except XcalException as err:
            logging.exception(err)
            self.logger.error("build", "translate", ("exception encountered", str(err)))
        except Exception as err:
            logging.exception(err)
            self.logger.error("build", "translate", ("unexpected exception encountered", str(err)))

    def xvsa_compile(self, xvsa_home):
        """compilation with xvsa

        Args:
            xvsa_home (str): path to xvsa home directory
        """
        try:
            time.sleep(1)
            self.logger.debug("xvsa_compile", "compiling with xvsa")
            if not self._generated:
                self.logger.warn("xvsa_compile", "You haven't generated the files yet")
                return
            compiler = Compile(self.lang, self.out_dir, xvsa_home)
            compiler.compile_files(self._generated)
            compiler.compile_jar(self.dependencies)
            compiler.archive_files(self.out_dir)
        except XcalException as err:
            logging.exception(err)
            self.logger.error("build", "translate", ("exception encountered", str(err)))
        except Exception as err:
            logging.exception(err)
            self.logger.error("build", "translate", ("unexpected exception encountered", str(err)))