#!/usr/bin/python3
'''
read

provides API for reading .mi file to generate the FSM abstract data
'''

#from translator.fsm_g import *
from .fsm_g import *
from translator.TagAssert import TagAssert
from translator.DeclareRule import DeclareRule
from .Annotate import Annotation
from .AnnotationApi import annotation_api # supply available APIs
import os 
import logger

logger = logger.retrieve_log()

# CONSTANT LABELS
NODE = 'NODE'
EDGE = 'EDGE'
TAG = 'TAG'
ASSERT = 'ASSERT'
DECLARE = 'DECLARE'
DEF_ACTION = 'DEF_ACTION'

class ReadInputError(Exception):
    pass
class FieldNotRecognised(ReadInputError):
    pass

def read_file(f):
    logger.info("Reading from file %s"%os.path.basename(f))
    if not os.path.exists(f):
        logger.error("file %s not found"%os.path.basename(f))
        raise FileNotFoundError()

    f_open = open(f, 'r')
    f_lines = f_open.readlines()

    # close and return non-empty lines
    f_open.close()
    return [i.strip() for i in f_lines if i is not '']

def create_fsm(lines):
    '''
    creating fsm (graph) abstract type from file lines 
    '''
    logger.debug("Generating fsm & info objects")
    fsm = FSM_G_Graph()

    for line in lines:
        logger.debug("Parsing content %s"%line)
        fields = line.split('|')
        if fields[0] == NODE:
            fsm.add_node(fields[1])
        elif fields[0] == EDGE:
            fsm.add_edge(*fields[1:])
        elif fields[0] == DEF_ACTION:
            fsm.add_def_acts(*fields[1:])
        elif fields[0] == TAG or fields[0] == ASSERT:
            TagAssert.add_entry_raw(line)
        elif fields[0] == DECLARE:
            DeclareRule.add_entry_raw(line)
        else:
            logger.error("%s not recognised"%fields[0])
            raise FieldNotRecognised()

    return fsm

def read_annotation(lines):
    """reading specialized for annotation part only"""
    logger.debug("generating annotation entries") 
    annotator = Annotation()

    for line in lines:
        logger.debug("line: %s"%line)
        fields = line.split('|')
        
        if fields[0] in annotation_api:
            annotator.add_entry_raw(line)
        else:
            logger.warning("%s not recognised as annotation"%fields[0]) # ignore, but present warning

    return annotator
