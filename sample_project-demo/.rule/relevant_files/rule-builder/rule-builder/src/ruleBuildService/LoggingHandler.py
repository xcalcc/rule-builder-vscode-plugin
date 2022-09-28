"""
LoggingHandler

initialize the log settings before being wrapped by XcalLogger.
Add level, set level, and add file handler
"""
import logging
import os
from logging.handlers import RotatingFileHandler

from common.XcalLogger import XcalLogger
from ruleBuildService.config import DEFAULT_LOG_LEVEL, RULE_BUILDING_LOG_PATH, ErrorNo

def initialize_logging_util(log_level='DEBUG'):
    """initialize logging with certain level

    Args:
        log_level (str): lowest level to report
    initializing logging config system to be used during rule building service
    """
    fmt = '%(asctime)s.%(msecs)3d %(levelname)10s \
            %(process)5d --- [%(threadName)15s] %(filename)40s: %(message)s' # format
    date_fmt = '%Y-%m-%d %H:%M:%S' # date format
    logging.basicConfig(format=fmt, datefmt=date_fmt, level=DEFAULT_LOG_LEVEL)
    logging.addLevelName(XcalLogger.XCAL_TRACE_LEVEL, 'TRACE') # trace level

    logger = logging.getLogger()
    default_log_level = DEFAULT_LOG_LEVEL

    # set log level
    if log_level == 'DEBUG':
        default_log_level = logging.DEBUG
    elif log_level == 'INFO':
        default_log_level = logging.INFO
    elif log_level == 'WARN':
        default_log_level = logging.WARN
    elif log_level == 'ERROR':
        default_log_level = logging.ERROR
    elif log_level == 'FATAL':
        default_log_level = 'FATAL'
    logger.setLevel(default_log_level)

    if not os.path.exists(os.path.dirname(RULE_BUILDING_LOG_PATH)):
        os.makedirs(os.path.dirname(RULE_BUILDING_LOG_PATH))

    # file output for log
    f_handler = RotatingFileHandler(RULE_BUILDING_LOG_PATH, maxBytes=50000000, backupCount=10)
    f_handler.setFormatter(logging.Formatter(fmt, date_fmt))
    logger.addHandler(f_handler)

    logging.info("log file path: %s", RULE_BUILDING_LOG_PATH)
