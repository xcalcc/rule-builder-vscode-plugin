import os
import unittest
from . import test_dir
from ruleBuildService.info_push import InfoPush

class TestInfoPush(unittest.TestCase):
    def test_read(self):
        push = InfoPush()
        #push.read_path("/home/nigel/rule-builder/test/info/rules.json")
        push.read_path(os.path.join(test_dir, 'info/rules.json'))
        push.dump_to_file(os.path.join(
            test_dir, 'info/'
        ))
