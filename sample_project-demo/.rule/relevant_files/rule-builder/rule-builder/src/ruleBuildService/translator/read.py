"""
read

Expose API for reading .mi file, whether it is for FSM or annotation based
"""

import os

from .fsm import FSM_G_Graph
from .annotation import Annotation
from .annotation_api import ANNOTATION_API
from .declare_rule import DeclareRule
from common.XcalLogger import XcalLogger
from common.XcalException import XcalException
from ruleBuildService.config import ErrorNo

#from ..logger import Logger
# _logger = Logger.retrieve_log() # pyling: disable=invalid-name

# CONSTANTS (labels)
NODE = "NODE"
EDGE = "EDGE"
DECLARE = "DECLARE"
DEF_ACTION = "DEF_ACTION"

class ReadInputError(Exception):
    """general error encountered when doing any read .mi file"""
    pass

class FieldNotRecognised(ReadInputError):
    """when the field is not part of existing API, this error is reported"""
    pass

def read_file(filename):
    """read content of filename

    reading content of filename and return the list of it, line by line.

    Args:
        filename (str): path to the file to be read
    Returns:
        list: containing list of content in the file
    """
    # _logger.info("Reading from file %s", os.path.basename(filename))
    if not os.path.exists(filename):
        raise XcalException("read", "read_file", "Resource: %s is not found" % filename,
                            err_code=ErrorNo.E_RESOURCE_NOT_FOUND)

    with XcalLogger("read", "read_file") as log:
        log.debug("read_file", "reading from %s" % filename)
        f_open = open(filename, 'r')
        f_lines = f_open.readlines()

        f_open.close()
        return [i.strip() for i in f_lines if i != ''] # return non-empty string

def read_fsm(lines):
    """read lines and create fsm

    line by line read and check if first field matches with any
    from a group of attributes.

    Args:
        line (list): content of file line by line
    Returns:
        FSM_G_Graph: fsm object
    """
    fsm = FSM_G_Graph()

    with XcalLogger("read", "read_fsm") as log:
        for line in lines:
            # _logger.debug("parsing content %s", line)
            log.debug("parsing content %s" % line)
            fields = line.split('|')
            if fields[0] == NODE:
                fsm.add_node(fields[1])
            elif fields[0] == EDGE:
                fsm.add_edge(*fields[1:])
            elif fields[0] == DEF_ACTION:
                fsm.add_def_acts(*fields[1:])
            elif fields[0] == DECLARE:
                DeclareRule.add_entry_raw(line)
            else:
                # _logger.debug("%s not part of FSM API", fields[0])
                log.warn("%s not part of FSM API" % fields[0])
        return fsm

def read_annotation(lines):
    """reading lines for annotation speciality

    line by line read and check if the first field matches any existing
    or implemented Annotation API.

    Args:
        line (list): content of file line by line
    Returns:
        Annotation: annotation object with entries
    """
    # _logger.debug("generating annotation entries")
    with XcalLogger("read", "read_annotation") as log:
        log.info("read_annotation", "readding for annotation")
        annotator = Annotation()

        for line in lines:
            fields = line.split('|')
            if fields[0] in ANNOTATION_API:
                log.debug("read_annotation", "annotatiton added: %s" %fields[0])
                annotator.add_entry_raw(line)
            else:
                log.warn("%s not recognised for annotation" % fields[0])

        return annotator

def create_fsm(lines, name, annotator):
    """creating fsm and annotation object

    line by line read and see if it matches any field from FSM or annotation.
    If not found raise error.

    Args:
        lines (list): content of file line by line
        annotator (Annotation): annotation object
        name (str): rule name, to take care of fsm use
    Returns:
        FSM_G_Graph: fsm graph object
        Annotation: annotator object
    Raises:
        FieldNotRecognised: if field neither from fsm or annotation
    """
    with XcalLogger("read", "create_fsm") as log:
        log.debug("read", "generating fsm and annotation object from reading")
        fsm = FSM_G_Graph()
        if not annotator: # if no annotator object passed
            annotator = Annotation()
        for line in lines:
            log.debug("create_fsm", "parsing content %s" % line)
            fields = line.split('|')
            if fields[0] == NODE:
                fsm.add_node(fields[1])
            elif fields[0] == EDGE:
                func_name = fsm.add_edge(*fields[1:])
                annotator.add_entry_raw(
                    "FSM_USE|%s|%s" % (func_name, name)
                )
            elif fields[0] == DEF_ACTION:
                fsm.add_def_acts(*fields[1:])
            elif fields[0] == DECLARE:
                DeclareRule.add_entry_raw(line)
            elif fields[0] in ANNOTATION_API:
                annotator.add_entry_raw(line)
            else:
                raise XcalException("read", "create_fsm", "field: %s not recognised" % fields[0],
                                    ErrorNo.E_MI_FIELD_UNKNOWN)
        return fsm, annotator
