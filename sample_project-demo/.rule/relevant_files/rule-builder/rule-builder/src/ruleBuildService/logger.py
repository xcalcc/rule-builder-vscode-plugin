#!/usr/bin/python3
"""
logger

Logging functionality for rule building service
"""

import logging
import os
from . import rb_loc

class Logger(object):
    """Logger class to get logging object"""

    def __init__(self):
        pass

    @classmethod
    def get_log(cls, test_mode=False, path=rb_loc, filename='rule_builder.log'):
        """Initializing logging object.

        Initialized logging object that logs to console (stdout) and
        file. Used for entry-point programs (i.e. scripts). If it's in
        test mode, don't stream it unless it's critical

        Args:
            test_mode (bool): flag whether logging is for test.
            path (str): path to where log file is generated
            filename(str): log name, may be specific to scripts
        Returns:
            logging.Logger: Logger object
        Raises:
            FileNotFoundError: if path not found
        """
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.DEBUG)

        if not os.path.exists(path):
            raise FileNotFoundError("%s not found"%path) # pylint: disable=undefined-variable
        log_file = os.path.join(path, filename) # file name
        open_log = open(log_file, 'w') # create new/clear for every run
        open_log.close()

        c_handler = logging.StreamHandler() # console log handler
        f_handler = logging.FileHandler(log_file) # file handler

        if test_mode:
            c_handler.setLevel(logging.CRITICAL)
        else:
            c_handler.setLevel(logging.INFO)
        f_handler.setLevel(logging.DEBUG)

        c_format = logging.Formatter('[%(levelname)s] ----- %(message)s')
        f_format = logging.Formatter(
            '[%(asctime)s][][%(levelname)s][%(filename)s][%(funcName)s][%(message)s]'
        )
        c_handler.setFormatter(c_format)
        f_handler.setFormatter(f_format)
        logger.addHandler(c_handler)
        logger.addHandler(f_handler)

        return logger

    @classmethod
    def retrieve_log(cls):
        """Retrieving an initialized logging object

        Used mostly in source code for APIs. Only used when it has been initialized
        under __name__ before

        Returns:
            logging.Logger: Logger object
        """
        logger = logging.getLogger(__name__)
        return logger
