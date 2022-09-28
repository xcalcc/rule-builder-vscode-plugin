'''
test_file_gen

unittest for rule file generation
'''
import unittest
import os
from .RuleFileGen import RuleFileGen, LangNotSupported
from .read import read_file, create_fsm
import logger

logger = logger.get_log()
test_dir = os.path.abspath(os.path.join(__file__, '../../../test/translate'))

class TestFileGen(unittest.TestCase):
    @unittest.skip
    def test_lang_err(self):
        logger.debug('-----test_lang_err------')  
        with self.assertRaises(LangNotSupported):
            fg = RuleFileGen('not-exist') 

    @unittest.skip
    def test_out_dir_err(self):
        logger.debug('-----test_out_dir_err------')  
        with self.assertRaises(FileNotFoundError):
            fg = RuleFileGen('c', out_dir='../not_found_dir') 

    @unittest.skip 
    def test_simple(self):
        logger.debug('-----test_assert------')  
        f = os.path.join(test_dir, 'ids03/ids03.mi')
        lines = read_file(f)
        fsm = create_fsm(lines)
        fg = RuleFileGen('java', test_dir+'/ids03/rt.o.vtable.mi' ,out_dir=os.path.join(test_dir, 'ids03'))
        fg.generate()

    def test_fsm(self):
        logger.debug('-----test_fsm------')  
        f = os.path.join(test_dir, 'cwe295-test/cwe295.mi')
        lines = read_file(f)
        fsm = create_fsm(lines)
        fg = RuleFileGen('java', test_dir+'/cwe295-test/org.apache.commons-commons-email.o.vtable.mi', 
            out_dir=test_dir+'/cwe295-test', name='cwe295')
        fg.attach_fsm(fsm)
        fg.generate()        

if __name__=='__main__':
    unittest.main()
