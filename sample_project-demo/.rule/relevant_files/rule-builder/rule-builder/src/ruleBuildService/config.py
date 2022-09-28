#!/usr/bin/python3
"""
config

shared configuration settings for running rule-builder
"""
import os
from enum import Enum
DEFAULT_LOG_LEVEL = 25
#RULE_BUILDING_LOG_PATH = os.path.realpath(os.curdir)
RULE_BUILDING_LOG_PATH = os.path.realpath(os.path.join(__file__, os.pardir, 'rule_builder.log'))

class ErrorNo(Enum):
    """Errors and respective Codes"""
    E_RESOURCE_NOT_FOUND = 0x815C002B
    E_FSM_INVALID = 0x815D002B
    E_MANGLE_NAME_NOT_FOUND = 0x815E002B
    E_INCORRECT_API_CALL = 0x015F0329
    E_API_NOT_EXIST = 0x01600329
    E_INVALID_FUNCTION_FORMAT = 0x8161002B
    E_LANGUAGE_NOT_SUPPORTED = 0x8162002B
    E_MI_FIELD_UNKNOWN = 0x8164002B
    E_XVSA_COMPILE_ERROR = 0x81650329
    E_INFO_FIELD_MISSING = 0x81660329