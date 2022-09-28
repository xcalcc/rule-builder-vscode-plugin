import logging

def get_log():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    c_handler = logging.StreamHandler()
    f_handler = logging.FileHandler('rule_builder.log')
    c_handler.setLevel(logging.INFO)
    f_handler.setLevel(logging.DEBUG)
    c_format = logging.Formatter('[%(levelname)s] ----- %(message)s')
    f_format = logging.Formatter('[%(asctime)s][][%(levelname)s][%(filename)s][%(funcName)s][%(message)s]')
    c_handler.setFormatter(c_format)
    f_handler.setFormatter(f_format)
    logger.addHandler(c_handler)
    logger.addHandler(f_handler)
    return logger

def retrieve_log():
    logger = logging.getLogger(__name__)
    return logger
