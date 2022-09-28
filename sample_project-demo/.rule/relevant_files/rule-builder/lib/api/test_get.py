import unittest
import logger
from .api import API

logger = logger.get_log()

class TestGet(unittest.TestCase):
    def test_login(self):
        API.login()       
    
    def test_get_rule_sets(self):
        token = API.login()
        r = API.get_rule_sets(token)
        print(r['content'])

    def test_insert_rule(self):
        code = "TEST99-J"
        token = API.login()
        API.insert_rule(token, code)
