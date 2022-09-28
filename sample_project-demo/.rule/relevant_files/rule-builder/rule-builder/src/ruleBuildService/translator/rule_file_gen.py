"""
rule_file_gen

API for rule file generation. Rule files can be FSM
or from Annotation
"""

import os
import subprocess
from .fsm import FSM_G_Graph
from .annotation import Annotation
from .declare_rule import DeclareRule
from .condition_parse import ConditionParse
from . import template_h_path
#from ..logger import Logger
from common.XcalLogger import XcalLogger
from common.XcalException import XcalException
from ruleBuildService.config import ErrorNo
from .. import rb_loc
from .annotation_api import FuncParse

# _logger = Logger.retrieve_log()

class LangNotSupported(Exception):
    """report error if language is not from the supported languages yet"""
    pass

class ReferenceNotFound(Exception):
    """when doing java translation, if reference file not found, report
    this error"""
    pass

class RuleFileGen(object):
    """class for rule file generation

    Based on FSM (if exist) and annotations, create the corresonding rule files
    needed for next stage process: compilation.

    Args:
        lang (str): target language {c, c++, java}
        references (str): reference file to find mangled function name
        out_dir (str): output directory
        name (str): rule name representation (default: rule)

    Attributes:
        lang (str): target language
        references (str): raw string of references
        ref_files (list): separate reference files
        out_dir (str): path to output directory
        fsm (FSM_G_Graph): fsm obejct (default None)
        annotations (Annotation): annotation object
        name (str): rule name
    """

    def __init__(self, lang, references=None, out_dir='.', name='rule'):
        # _logger.debug("initializing rule file generation")
        self.logger = XcalLogger("rule_file_gen", "__init__")
        self.logger.debug("__init__", "initializing rule file generation")
        self.lang = lang
        self.references = references
        self.ref_files = []
        self.out_dir = out_dir
        self.fsm = None
        self.annotations = Annotation() # initialize with empty entries
        self.name = name
        self.validate()

    def validate(self):
        """validation check for passed arguments/arguments hold"""
        self.logger.debug("validate", "validation in progress...")
        possible = ['c', 'c++', 'cpp', 'java']
        if self.lang not in possible:
            raise XcalException("rule_file_gen", "validate", "Language not supported: %s" % self.lang,
                                err_code=ErrorNo.E_LANGUAGE_NOT_SUPPORTED)
            
        if self.out_dir != None:
            # check if exist
            abs_path = os.path.abspath(self.out_dir)
            if not os.path.exists(abs_path):
                raise XcalException("rule_file_gen", "validate", "path to output directory not found: %s" % abs_path,
                                    err_code=ErrorNo.E_RESOURCE_NOT_FOUND)
            self.out_dir = abs_path
        if self.references != None:
            # get all references checked
            # if file exist, add to ref_files list
            refs = self.references.split(':')
            for ref in refs:
                abs_path = os.path.abspath(ref)
                if not os.path.exists(abs_path):
                    raise XcalException("rule_file_gen", "validate", "path to output directory not found: %s" % abs_path,
                                        err_code=ErrorNo.E_RESOURCE_NOT_FOUND)
                    
                self.ref_files.append(abs_path)

    def attach_fsm(self, fsm):
        """set fsm

        initially no fsm is put, but if fsm is encountered,
        attach it to the class so that it can be included during
        file generation

        Args:
            fsm (FSM_G_Graph):  graph object to be attached
        """
        self.fsm = fsm
        self.logger.debug("attach_fsm", "fsm attached")

    def attach_annotations(self, annot):
        """set annotations

        initially annotation object is initialised but is guaranteed
        to be empty. Replace annotation object

        Args:
            annot (Annotation): replacement annotation object
        """
        self.annotations = annot
        self.logger.debug("attach_annotations", "annotation attached")

    def write_start(self, out_file):
        """start of file write for fsm

        for fsm, the start of file is writing imports, class
        rule declaration start, etc.

        Args:
            out_file: path to the output file
        """
        out_file.write("IMPORT1\nIMPORT2\n")
        out_file.write("CLASS(%s)\n"%self.name)
        out_file.write("IFDEF1\nIFDEF2\nIFDEF3\n")
        out_file.write("    START_RULE(%s)\n"%self.name)
        out_file.write('        BUILD_BEGIN("%s")\n'%self.name)
        out_file.write('        NEW_START_STATE\n')
        out_file.write('        NEW_FINAL_STATE\n')

    def write_end(self, out_file):
        """writing end of fsm rule

        when all content of fsm has been written out, close
        the fsm rule.

        Args:
            out_file (str): path to output file
        """
        out_file.write('        BUILD_END("%s")\n'%self.name)
        out_file.write('    END_RULE\n')
        out_file.write("IFDEF1\n")
        out_file.write("END_RULE\n")
        out_file.write("IFDEF3\n")
        out_file.close() # close file

    def write_transitions(self, fsm, out_file):
        """write out transition detail of fsm

        fsm details which mostly focuses on the transition
        between states will be translated into a text format
        that can follow API of RBC_ENGINE.

        Args:
            fsm (FSM_G_Graph): FSM object graph
            out_file (str): path to output file
        """

        for edge in fsm.edges:
            start = edge.source.name
            if start == "START":
                start = "start" # specific if name is START, treat node as entry point

            # if java, find mangle func name, else leave it be
            if self.lang == "java":
                fname = FSM_G_Graph.find_mangle_func_name_mult(edge.fun_name, *self.ref_files)
            else:
                name = "<" + edge.fun_name + ">"
                parse_fname = FuncParse(name, self.lang) # get function method detail
                fname = parse_fname.met_name

            # key
            temp = ConditionParse.parse(edge.key)
            if self.lang == 'java':
                key = temp.translate(self.ref_files)
            else:
                key = temp.translate()
                if key == "none": # convert none to NULL for c/cxx/cpp
                    key = "NULL"

            # condition
            temp = ConditionParse.parse(edge.condition)
            if self.lang == 'java':
                condition = temp.translate(self.ref_files)
            else:
                condition = temp.translate()
            if condition == "none":
                condition = 1
            elif condition[:7] == "GET_ARG": # get_arg=>get_value
                condition = 'GET_VALUE(%s)'%condition

            # next state
            target = edge.target.name
            if target == "END":
                target = "end"

            # error
            if edge.err == "none":
                error = '""'
            else:
                error = '"%s"'%(edge.err)

            # int message
            message = edge.msg

            # write into file
            out_file.write(
                '       ADD_TRANSITION("%s","%s",%s,%s,"%s",%s,%s)\n'
                %(start, fname, key, condition, target, error, message)
            )

        for e in fsm.def_acts: # pylint: disable=invalid-name
            if isinstance(fsm.def_acts[e], list):
                for (err, msg) in fsm[e]:
                    if err == "none":
                        err = '""'
                    out_file.write(
                        '       SET_DEFAULT_ACTION("%s","%s",%s)\n'%(e, err, msg)
                    )
            else:
                (err, msg) = fsm.def_acts[e]
                out_file.write(
                    '       SET_DEFAULT_ACTION("%s","%s",%s)\n'
                    %(e, err, msg)
                )

    def write_fsm(self):
        """main call of writing fsm into a file"""

        if not self.fsm:
            # _logger.debug("no fsm attached, abort writing")
            self.logger.debug("write_fsm", "no fsm attached, no writing needed")
            return

        if self.lang == 'java':
            if self.references is None:
                # _logger.error("java translation requires reference file")
                raise XcalException("rule_file_gen", "write_fsm", "java fsm rule creation requires reference",
                                    err_code=ErrorNo.E_MANGLE_NAME_NOT_FOUND)

        template_path = template_h_path

        read = open(template_path, 'r')
        to_read = read.readlines()
        read.close()

        out_h_path = os.path.join(self.out_dir, 'rule.h') # base file due for a translation
        out_h_file = open(out_h_path, 'w')

        # copy header
        for ref in to_read:
            out_h_file.write(ref)

        self.write_start(out_h_file)
        self.write_transitions(self.fsm, out_h_file)
        self.write_end(out_h_file)

    def compile(self):
        """compiling .h files into their respective target languages"""
        files = []
        self.logger.debug("compile", "compilig .h file to target language")
        if self.lang == 'c' or self.lang == 'c++':
            command = 'cpp -P %s > %s.cxx'%(
                os.path.join(self.out_dir, 'rule.h'),
                os.path.join(self.out_dir, self.name)
                )
            generated_file = '%s.cxx'%self.name
            generated_file = os.path.join(self.out_dir, generated_file)
            for src_file in self.annotations.src_files:
                self.logger.debug('compile', 'file: %s' % src_file)
                target_dir = os.path.dirname(src_file)
                basename = os.path.basename(src_file)[:-2] # not including .h
                cmd = 'cpp -P %s > %s.cxx'%(src_file, os.path.join(target_dir, basename))
                os.popen(cmd)
                files.append("%s.cxx" % os.path.join(target_dir, basename))
            """
            if DeclareRule.rules:
                cmd = ' cpp -P %s > %s'%(
                    os.path.join(self.out_dir, 'DECLARE_RULE.h'),
                    os.path.join(self.out_dir, 'DECLARE_RULE.cxx'))
                files.append(os.path.join(self.out_dir, 'DECLARE_RULE.cxx'))
                os.popen(cmd)
                DeclareRule.clear()
            """

        elif self.lang == 'java':
            command = 'cpp -P -DLANG_JAVA %s > %s.java'%(
                os.path.join(self.out_dir, 'rule.h'),
                os.path.join(self.out_dir, self.name)
            )
            generated_file = '%s.java'%self.name
            generated_file = os.path.join(self.out_dir, generated_file)
            self.logger.debug("compile", "Generated file: %s" % generated_file)
            for src_file in self.annotations.src_files:
                target_dir = os.path.dirname(src_file)
                basename = os.path.basename(src_file)[:-2]  # not including .h
                cmd = 'cpp -P -DLANG_JAVA %s > %s.java'%(
                    src_file, os.path.join(target_dir, basename))
                os.popen(cmd)
                files.append("%s.java" % os.path.join(target_dir, basename))
            """
            if DeclareRule.rules:
                self.logger.debug("compile", "rule declaration included")
                cmd = 'cpp -P -DLANG_JAVA %s > %s'%(
                    os.path.join(self.out_dir, 'DECLARE_RULE.h'),
                    os.path.join(self.out_dir, 'DECLARE_RULE.java'))
                #os.popen(cmd)
                decl = subprocess.call(cmd, shell=True)
                files.append(os.path.join(self.out_dir, 'DECLARE_RULE.java'))
                DeclareRule.clear()
            """

        # only if there is rule.h you can generate the fsm rule file
        if os.path.exists(os.path.join(self.out_dir, 'rule.h')):
            os.popen(command)
            files.append(generated_file)
            # _logger.info("File %s succesfully generated", os.path.basename(generated_file))
        return files # contain all generated files

    def generate(self):
        """generating the rule file"""
        # annotation dump
        self.logger.debug("generate", "generating rule file")
        annot = self.annotations
        if annot and annot.entries: # if there are entries
            annot.generate(self.lang, self.out_dir)

        # declare rule dump
        """
        if not DeclareRule.rules:
            self.logger.debug("generate", "no rule declarations found")
        else:
            DeclareRule.dump(self.out_dir)
        """

        # if no fsm or if fsm is empty (no nodes/edges)
        if self.fsm is None:
            # _logger.debug('no fsm is attached')
            self.logger.debug("generate", "no fsm is attached")
        elif not self.fsm.nodes:
            # _logger.debug('fsm passed is empty')
            self.logger.debug("generate", "fsm passed is empty")

        else:
            self.write_fsm() # generate all .h files

        # from .h files, convert to target languages
        return self.compile()
