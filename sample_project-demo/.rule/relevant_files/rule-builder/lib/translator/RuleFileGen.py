'''
RuleFileGen

API for rule file generation. Rule files can be 
FSM or part of rule annotation.
'''
import sys
import os
import subprocess

from .fsm_g import FSM_G_Node, FSM_G_Edge, FSM_G_Graph
from .TagAssert import TagAssert
from .DeclareRule import DeclareRule
from .ConditionParse import ConditionParse
import logger
logger = logger.retrieve_log()

# path of root
rb_loc = os.path.dirname(
        os.path.dirname(
            os.path.dirname(
            __file__
            )
        )
    )
class LangNotSupported(Exception):
    pass

class ReferenceNotFound(Exception):
    pass

class RuleFileGen:
    # lang: target language of translation
    # references: needs a .mi file if java language is involved
    # loc: output directory
    # fms: FSM_G_Graph object that represents fsm (if exist)

    def __init__(self, lang, references=None, out_dir='.', name='rule'):
        logger.debug("initializing rule file generation") 
        self.lang = lang
        self.references = references
        self.ref_files = []
        self.out_dir = out_dir
        self.fsm = None
        self.name = name
        self.validate()
        
    def validate(self):
        '''validation of arguments passed on'''
        possible = ['c', 'c++', 'cpp', 'java']
        if self.lang not in possible:
            logger.error("%s language not supported"%self.lang)
            raise LangNotSupported('%s language not supported'%self.lang)
        if self.out_dir != None:
            # check if exist
            abs_path = os.path.abspath(self.out_dir)
            if not os.path.exists(abs_path):  
                logger.error("path not found: %s"%abs_path)
                raise FileNotFoundError("path to out directory not found")
            self.out_dir = abs_path
        if self.lang == 'java':
            if self.references == None:
                logger.error("java translation requires reference file")
                raise ReferenceNotFound()
        if self.references != None:
            # get all references checked
            # if file exist, add to ref_files list
            refs = self.references.split(':')
            for ref in refs:
                abs_path = os.path.abspath(ref)
                if not os.path.exists(abs_path):
                    logger.error("path not found: %s"%abs_path)        
                    raise FileNotFoundError
                self.ref_files.append(abs_path)

    def attach_fsm(self, fsm):
        '''adding fsm to go through file generation to rule file'''
        self.fsm = fsm 

    def write_start(self, out_file):
        logger.debug('Writing start...')
        out_file.write("IMPORT1\nIMPORT2\n")
        out_file.write("CLASS(%s)\n"%self.name)
        out_file.write("    START_RULE(%s)\n"%self.name)
        out_file.write('        BUILD_BEGIN("%s")\n'%self.name)
        out_file.write('        NEW_START_STATE\n')
        out_file.write('        NEW_FINAL_STATE\n')

    def write_end(self, out_file):
        logger.debug('Writing end...')
        out_file.write('        BUILD_END("%s")\n'%self.name)
        out_file.write('    END_RULE\n')
        out_file.write('END_CLASS\n')

    def write_transitions(self, fsm, out_file):
        logger.debug("Writing transitions...")
        for edge in fsm.edges:
            start = edge.source.name
            if start == "START":
                start = "start" # specific if name is START, treat node as entry point

            # function name
            # if java, find mangle func name, else leave it be
            if self.lang == "java":
                fname = FSM_G_Graph.find_mangle_func_name_mult(edge.fun_name, *self.ref_files)
            else:
                fname = edge.fun_name 
            logger.debug("fname: %s"%fname) 

            # key
            temp = ConditionParse.parse(edge.key)
            if self.lang == 'java':
                key = temp.translate(self.ref_files)
            else:
                key = temp.translate()
            logger.debug("Result of key parsing: %s"%key)

            # condition
            temp = ConditionParse.parse(edge.condition)
            if self.lang == 'java':
                condition = temp.translate(self.ref_files)
            else:
                condition = temp.translate()
            if condition == "none":
                condition = 1
            elif condition[:7] == "GET_ARG":
                condition = 'GET_VALUE(%s)'%condition

            logger.debug("condition is %s"%condition)

            # next state
            target = edge.target.name
            if target == "END":
                target = "end"
            logger.debug('Target is: "%s"'%target)

            # error
            if edge.err == "none":
                error = '""'
            else:
                error = '"%s"'%(edge.err)
            logger.debug('error is %s'%error)

            # write into file
            out_file.write(
            '       ADD_TRANSITION("%s","%s",%s,%s,"%s",%s)\n'
            %(start, fname, key, condition, target, error)
            )

        for e in fsm.def_acts:
            if isinstance(fsm.def_acts[e], list):
                for err in fsm[e]:
                    if err == "none":
                        err = '""'
                    out_file.write(
                    '       SET_DEFAULT_ACTION("%s","%s")\n'%(e, err)
                    )
            else:
                out_file.write(
                    '       SET_DEFAULT_ACTION("%s","%s")\n'
                    %(e, fsm.def_acts[e])
                )

    def write_fsm(self):
        '''writing an FSM into a file'''
        template_path = os.path.join(os.path.dirname(__file__), 'template.h')
        logger.debug('path to template.h: %s'%template_path) 

        read = open(template_path, 'r')
        to_read = read.readlines()
        read.close()

        if not os.path.exists(template_path):
            logger.error("template file not found")
            raise FileNotFoundError()
        logger.debug('template.h found')

        out_h_path = os.path.join(self.out_dir, 'rule.h') # base file due for a translation
        out_h_file = open(out_h_path, 'w')

        # copy header
        for r in to_read:
            out_h_file.write(r)

        self.write_start(out_h_file)
        self.write_transitions(self.fsm, out_h_file) 
        self.write_end(out_h_file)

    def compile(self):
        '''compiling .h files into target languages'''
        if self.lang == 'c' or self.lang == 'c++':
            command = 'cpp -P %s > %s.cxx'%(os.path.join(self.out_dir, 'rule.h'), 
                    os.path.join(self.out_dir, self.name)
                )
            generated_file = '%s.cxx'%self.name
            generated_file = os.path.join(self.out_dir, generated_file)
            for f in TagAssert.src_files:
                logger.debug('file: %s'%f)
                target_dir = os.path.dirname(f)
                basename = os.path.basename(f)[:-2] # not including .h
                cmd = 'cpp -P %s > %s.cxx'%(f, os.path.join(target_dir, basename))
                os.popen(cmd)
            if DeclareRule.rules:
                cmd = ' cpp -P %s > %s'%(os.path.join(self.out_dir, 'DECLARE_RULE.h'),
                    os.path.join(self.out_dir, 'DECLARE_RULE.cxx'))
                os.popen(cmd)

        elif self.lang == 'java':
            command = 'cpp -P -DLANG_JAVA %s > %s.java'%(os.path.join(self.out_dir, 'rule.h'), 
                    os.path.join(self.out_dir, self.name)
                )
            generated_file = '%s.java'%self.name
            generated_file = os.path.join(self.out_dir, generated_file)
            logger.debug("Generated file: %s"%generated_file)
            for f in TagAssert.src_files:
                target_dir = os.path.dirname(f)
                basename = os.path.basename(f)[:-2]  # not including .h
                cmd = 'cpp -P -DLANG_JAVA %s > %s.java'%(f, os.path.join(target_dir, basename))
                os.popen(cmd) 
            if DeclareRule.rules:
                cmd = 'cpp -P -DLANG_JAVA %s > %s'%(os.path.join(self.out_dir, 'DECLARE_RULE.h'),
                    os.path.join(self.out_dir, 'DECLARE_RULE.java'))
                os.popen(cmd)

        # only if there is rule.h you can generate the fsm rule file 
        if os.path.exists(os.path.join(self.out_dir, 'rule.h')):
            os.popen(command)
            logger.info("File %s succesfully generated"%os.path.basename(generated_file))


    def generate(self):
        '''Generating rule files'''
        
        # Annotation + Rule Declaration dump file
        if not TagAssert.entries:
            logger.debug('no annotations found')   
        else:
            TagAssert.generate(rb_loc, self.out_dir)

        if not DeclareRule.rules:
            logger.debug('no rule declarations found') 
        else:
            DeclareRule.dump(rb_loc, self.out_dir)
        
        # if no fsm or if fsm is empty (no nodes/edges)
        if self.fsm == None:
            logger.debug('no fsm is attached')
        elif not self.fsm.nodes:
            logger.debug('fsm passed is empty')

        else:
            logger.debug("FSM generation...")
            self.write_fsm() # generate all .h files
            
        # from .h files, convert to target languages
        self.compile() 
