import unittest
from .fsm_g import *
import logger

logger = logger.get_log()
# Example Case
case = [
    "NODE|START", 
    "NODE|init",  
    "NODE|ssl_connect", 
    "NODE|verified", 
    "NODE|END",
    "EDGE|START|init|org.apache.commons.mail.SimpleEmail: void <init>()|none|this()|none",
    "EDGE|init|ssl_connect|org.apache.commons.mail.Email: org.apache.commons.mail.Email setSSLOnConnect(boolean)|arg(1)|this()|none",
    "EDGE|ssl_connect|verified|org.apache.commons.mail.Email: org.apache.commons.mail.Email setSSLCheckServerIdentity(boolean)|arg(1)|this()|none",
    "EDGE|verified|END|org.apache.commons.mail.Email: java.lang.String send()|none|this()|none",
    "EDGE|init|END|org.apache.commons.mail.Email: java.lang.String send()|none|this()|CWE295",
    "EDGE|ssl_connect|END|org.apache.commons.mail.Email: java.lang.String send()|none|this()|CWE295",
    "DECLARE|CWE295|CUSTOM|SSL Not Verified" 
]

class TestFSM(unittest.TestCase):

    def test_duplicate_node(self):
        logger.debug("------ TEST1 --------")
        g = FSM_G_Graph()
        with self.assertRaises(NodeCreationError):
            g.add_node("a")
            g.add_node("a")

    def test_edge_err(self):
        logger.debug("------ TEST2 --------")
        g = FSM_G_Graph()
        with self.assertRaises(EdgeCreationError):
            g.add_node("a")
            g.add_node("c")
            g.add_edge("a","b","w", "x","y","z") 

    def test_edge_valid(self):
        logger.debug("------ TEST3 --------")
        g = FSM_G_Graph()
        g.add_node("a")
        g.add_node("b")
        g.add_edge("a","b","w", "x","y","z") 


    def test_def_act_err(self):
        # adding default action
        logger.debug("------ TEST4 --------")
        g = FSM_G_Graph() 

        with self.assertRaises(GraphCreationError):
            g.add_node("a")
            g.add_def_acts("b","IDS03-J") # should introduce error

    def test_mini_edge(self):
        logger.debug("------ TEST5 --------")
        g = Func('a', 'b', 'c')
        h = Func('a', 'b', 'c')

        self.assertEqual(g==h, True)
    
    def test_merge_invalid(self):
        logger.debug("------ TEST6 --------")
        g =  FSM_G_Graph()
        g.add_node("a")
        g.add_node("b")
        g.add_edge("a", "b", "w", "x", "y", "z")

        h = FSM_G_Graph()
        h.add_node('c')
        h.add_node('d')
        h.add_edge('c', 'd', 'w', 'x', 'y', 'z')

        with self.assertRaises(GraphMergeError):
            g.merge(h)
    
    def test_merge_valid(self):
        logger.debug("------ TEST7 --------")
        g = FSM_G_Graph()
        g.add_node("START")
        g.add_node("init")
        g.add_node("END")
        g.add_edge("START", "init", 'w', 'x', 'y', 'z')
        g.add_edge("init", "END", 'a', 'b', 'c', 'd')

        h = FSM_G_Graph()
        h.add_node('START')
        h.add_node('init')
        h.add_node('END')
        h.add_edge("START", "init", 's', 'd', 'f', 'g')
        h.add_edge("init", "END", 'g', 'h', 'j', 'k')

        g.merge(h)

    def test_merge_valid2(self):
        logger.debug("------ TEST8 --------")
        g = FSM_G_Graph()
        g.add_node("START")
        g.add_node("init")
        g.add_node("END")
        g.add_edge("START", "init", 'w', 'x', 'y', 'z')
        g.add_edge("init", "END", 'a', 'b', 'c', 'd')

        h = FSM_G_Graph()
        h.add_node('START')
        h.add_node('INTER')
        h.add_node('END')
        h.add_edge("START", "INTER", 's', 'd', 'f', 'g')
        h.add_edge("INTER", "END", 'g', 'h', 'j', 'k')

        g.merge(h)



if __name__ == "__main__":
    unittest.main()
