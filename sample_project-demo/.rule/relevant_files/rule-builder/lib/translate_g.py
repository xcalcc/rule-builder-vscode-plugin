#!/usr/bin/python3
'''
Script to run translation

ERROR_CODES
-1: argument to script is incorrect
'''
import sys
import os
import subprocess
import argparse

from translator.fsm_g import *
from translator.rule_tag import FuncParse, Tagging
from translator.TagAssert import TagAssert
from translator.DeclareRule import DeclareRule

import logger

logger = logger.get_log()
logger.debug("-------- Translation Start ----------")

rb_loc = subprocess.run(['which', 'rbuild'], stdout=subprocess.PIPE, universal_newlines=True)
if rb_loc.returncode != 0:
    print("RBNotFound: Library not found, you may not have included the rule builder to your PATH")
    sys.exit(1)
rb_loc = rb_loc.stdout.strip()
rb_loc = os.path.dirname(rb_loc)
logger.debug("rb path: %s"%rb_loc)

# Arguments parsing
languages=['c', 'java']
parser = argparse.ArgumentParser(description="Translate")
parser.add_argument('input', nargs='+', help='.mi file for input') # there may be multiple .mi file as input
parser.add_argument('-l', '--lang', help='Target language')
parser.add_argument('-r', '--ref', help='reference mi file, if multiple, concatenate with :')
parser.add_argument('-n', '--name', help='rule name')
args = parser.parse_args()

# Input Validation
for i in args.input:
    if not i.endswith(".mi"):
            logger.error("Invalid Input file: %s"%args.input)
            sys.exit(-1)
input_files = args.input

# Error name
if not args.name:
    ERROR_NAME = "rule"
else:
    ERROR_NAME = args.name
logger.debug("error name: %s"%ERROR_NAME)

if not args.lang:
    logger.error("Taget language not specified")
    sys.exit(-1)

if args.lang not in languages:
    logger.error("Invalid target language. Choose either c or java")
    sys.exit(-1)

lang = args.lang
logger.debug("Target language: %s"%lang)

if args.ref:
    references = args.ref.split(':')
else:
    references = [os.path.join(rb_loc, 'lib/rt.o.vtable.mi')] # by default always include rt.o.vtable.mi
logger.debug("References: %s"%references)

# CONSTANTS
NODE = "NODE"
EDGE = "EDGE"
TAG = "TAG"
ASSERT = "ASSERT"
DECLARE = "DECLARE"
DEF_ACTION = "DEF_ACTION"

def create_graph(f):
    '''Creating FSM graph from here'''
    logger.debug("Parsing from file %s"%(f))
    fopen = open(f, 'r')
    flines = fopen.readlines()
    content = []
    for f in flines:
        content.append(f.strip())
    fsm = FSM_G_Graph()
    for i in content:
        logger.debug("Parsing content %s"%i)
        fields = i.split('|')
        if fields[0] == NODE:
            fsm.add_node(fields[1])
        elif fields[0] == EDGE:
            fsm.add_edge(*fields[1:])
        elif fields[0] == DEF_ACTION:
            fsm.add_def_acts(*fields[1:])
        elif fields[0] == TAG:
            TagAssert.add_entry_raw(i)
        elif fields[0] == ASSERT:
            TagAssert.add_entry_raw(i)
        elif fields[0] == DECLARE:
            DeclareRule.add_entry_raw(i)
        else:
            logger.error("Field: %s not recongised"% fields[0])
            sys.exit(2)
    return fsm

fsm_list = []

for i in input_files:
    fsm_list.append(create_graph(i))
    
# for tag, assert, and rule declaration
TagAssert.generate(rb_loc)
if TagAssert.entries:
    logger.info("Generating file paths for tags")
DeclareRule.dump(rb_loc)
if DeclareRule.rules:
    logger.info("Generating file for rule declaration: DECLARE_RULE.h")

# TODO: Possible for merging here

fsm_available = False # flag whether or not rule includes fsm
main_fsm = fsm_list[0] # there will always be a fsm even if content is empty

# check if there is fsm
if main_fsm.nodes and main_fsm.edges:
    logger.info("FSM constructed from input file")
    fsm_available = True


# if fsm available, prepare rule.h that holds macros
if fsm_available:
    template_path = os.path.join(rb_loc, 'lib/translator/template.h')
    logger.debug("copying template path to rule.h")
    read = open(template_path, 'r')
    out_file = open('rule.h', 'w')
    to_read = read.readlines()
    for r in to_read:
        out_file.write(r)
    
# Writing rules
def write_start(out_file):
    logger.debug("Writing start")
    out_file.write("IMPORT1\nIMPORT2\n")
    out_file.write("CLASS(%s)\n"%ERROR_NAME)
    out_file.write('    START_RULE(%s)\n'%ERROR_NAME)
    out_file.write('        BUILD_BEGIN("%s")\n'%ERROR_NAME)
    out_file.write('        NEW_START_STATE\n')
    out_file.write('        NEW_FINAL_STATE\n')

def write_end(out_file):
    logger.debug("Writing end part")
    out_file.write('        BUILD_END("%s")\n'%ERROR_NAME)
    out_file.write('    END_RULE\n')
    out_file.write('END_CLASS\n')

def write_transitions(fsm, out_file):
    logger.debug("Writing into %s"%out_file.name)
    write_start(out_file)
    for edge in fsm.edges:
        logger.debug(edge)
        
        # Start
        start = edge.source.name
        if start == "START":
            start ="start"
        logger.debug("start is %s"%start)
        # Function Name
        if lang == "java":
            reference = args.ref
            fname = FSM_G_Graph.find_mangle_func_name_mult(edge.fun_name, *references)
            logger.debug(fname)
        else:
            fname = edge.fun_name # in C, just let the function name be itself

        # Key
        temp = ConditionParse.parse(edge.key)
        if lang == 'java':
            key = temp.translate(references)
        else:
            key = temp.translate() 
        logger.debug("Result of key parsing: %s"%key)
        
        # Condition
        temp = ConditionParse.parse(edge.condition)
        if lang == 'java':
            condition = temp.translate(references)
        else:
            condition = temp.translate()
        if condition == "none":
            condition = 1 # convert into 1
        #elif condition[:7] == "GET_ARG":
            #condition = 'GET_VALUE(%s)'%condition

        logger.debug("Condition is %s"%condition)

        # Next State
        target = edge.target.name
        if target == "END":
            target = "end"
        logger.debug('Target is : "%s"'% target)

        # Error
        if edge.err == "none":
            error = '""'
        else:
            error = '"%s"'%(edge.err)
        logger.debug("Error is %s"%error)
        
        # Write into file
        out_file.write(
        '       ADD_TRANSITION("%s","%s",%s,%s,"%s",%s)\n'
        % (start, fname, key, condition, target, error))

        # Writing Default action
    for e in fsm.def_acts:
        if isinstance(fsm.def_acts[e], list): # if list one by one
            for err in fsm[e]:
                if err == "none":
                    err = '""'
                out_file.write(
                '        SET_DEFAULT_ACTION("%s","%s")\n'%(e, err)
                )
        else:
            out_file.write(
            '       SET_DEFAULT_ACTION("%s","%s")\n'
            %(e, fsm.def_acts[e]))
    write_end(out_file)

        
if fsm_available:
    write_transitions(main_fsm, out_file)

generated_file = ''
if lang == 'c':
    if fsm_available:
        logger.info("Writing into %s.cxx"%(ERROR_NAME))
        command = 'cpp -P rule.h > %s.cxx'%ERROR_NAME
        generated_file = '%s.cxx'%ERROR_NAME 
    for f in TagAssert.src_files:
        parts = f.split('/')
        cmd = 'cpp -P %s > %s.cxx'%(f, parts[-1][:-2])
        os.popen(cmd)
    if DeclareRule.rules:
        cmd = 'cpp -P DECLARE_RULE.h > DECLARE_RULE.cxx'
        os.popen(cmd)

elif lang == 'java':
    if fsm_available:
        logger.info("Writing into %s.java"%ERROR_NAME)
        command = 'cpp -P -DLANG_JAVA rule.h > %s.java'%ERROR_NAME
        generated_file = '%s.java'%ERROR_NAME
    for f in TagAssert.src_files:
        parts = f.split('/')
        cmd = 'cpp -P -DLANG_JAVA %s > %s.java'%(f, parts[-1][:-2])
        os.popen(cmd)
    if DeclareRule.rules:
        cmd = 'cpp -P -DLANG_JAVA DECLARE_RULE.h > DECLARE_RULE.java'
        os.popen(cmd)

if fsm_available:
    os.popen(command)
    logger.info("File %s is successfully generated"%generated_file)
sys.exit(0)
