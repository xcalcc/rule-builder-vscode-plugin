#!/usr/bin/python3
# ====================
# fsm
# modelling of fsm with Graph data structure
# contains Node, Edge, and Graph
# =====================

from .usr_graph import Graph, Node, Edge
import logger
import sys
logger = logger.retrieve_log()
class FSM_Node:
    def __init__(self, num, builtin=None):
        if not builtin==None:
            self.name = builtin
        else:
            self.name = 's'+str(num)  # identifier
        self.edges = [] # list of nodes adjacent to this node

    def add_edge(self, e):
        logger.debug("Adding edge %s->%s to %s"%(e.start.name, e.target.name, self.name))
        self.edges.append(e)     
    
    def remove_edge(self, e):
        logger.debug("removing edge %s->%s from node %s"%(e.start.name, e.target.name, self.name))
        to_pop = None
        for i in range(len(self.edges)):
            if self.edges[i].equals(e):
                to_pop = i
        if to_pop:
            self.edges.pop(i) 

class FSM_Edge:
    # Edge represents transition detail from 1 state(node) to another
    def __init__(self, start, target, fname, key, condition, err):
        self.start = start # Start Node
        self.target = target # Target Node 
        self.fname = fname # Function Name
        self.key = key # key (this, arg(1), null, return)
        self.condition = condition # condition for this transition
        self.err = err # check if error exists (!none)
    
    def __repr__(self):
        # visualization of edges
        return (
            f"start = {self.start.name}\n"
            f"target = {self.target.name}\n"
            f"function name = {self.fname}\n"
            f"condition = {self.condition}\n"
            f"error = {self.err}"
        )
    def equals(self, other):
        return self.start == other.start and self.target == other.target
 
    def __eq__(self, other):
        return self.fname == other.fname and self.key == other.key and self.condition == other.condition

    def cond_parse(self):
        # parsing condition string to acceptable format
        if self.condition == "none":
            return []# return as is if no condition
        c_list = []
        conds = self.condition.split("&&")
        try:
            for c in conds:
                temp = c.split("==")  
                c_list.append( (temp[0][-1], temp[1])) 
            return c_list
        except Exception as e:
            logger.error("Something wrong happen when parsing the condition: %s"%(self.condition))
            sys.exit(4)

    def replace_start(self, start: FSM_Node):
        logger.debug("Replacing %s->%s to node %s->%s"%(self.start.name, self.target.name , start.name, self.target.name))
        self.start = start

    def replace_end(self, end: FSM_Node):
        logger.debug("Replacing %s->%s to node %s->%s"%(self.start.name, self.target.name, end.name, self.target.name))
        self.target = end
                    
class FSM_Graph:

    # takes the user graph and convert it into an FSM logic 
    # ready for conversion into file depending on target language
    # change self._end into a list
    STATE_NUM = 1
    def __init__(self, usr_g: Graph):
        self.usr_graph = usr_g 
        self.__find_start()
        self._end = []
        self.__find_end()
        self.nodes = []
        self.edges = []
        self.default_action = {}
        self._represent()
    
    @staticmethod
    def find_mangle_f(fname, ref_file):
        # if language is java, substitute function name with the 
        # mangled function name
        f = open(ref_file, 'r')
        lines = f.readlines()
        for line in lines:
            splits = line.strip().split('|')
            if f'<{fname}>' == splits[0]:
                return splits[1]
        return None
    
    @staticmethod
    def find_mangle_f_multifile(fname, *files):
        # substitute the function name
        files_to_read = list(files)
        for i in files_to_read:
            name = FSM_Graph.find_mangle_f(fname, i)
            if not name == None:
                return name
    
    def add_node(self, node):
        # add unique node
        for n in self.nodes:
            if node.name == n.name:
                return
        self.nodes.append(node)

    def __repr__(self):
        # representation of the graph model
        mappings = f"===============NODES=============\n"
        for node in self.nodes:
            mappings += f"{node.name}: {len(node.edges)}\n" 
        edges_info = f"===============EDGES DATA==============\n"
        for edge in self.edges:
            edges_info += f"{edge.start.name} -> {edge.target.name}\n"
            edges_info += f"\t-function name : {edge.fname}\n"
            edges_info += f"\t-key: {edge.key}\n"
            edges_info += f"\t-condition : {edge.cond_parse()}\n"
            edges_info += f"\t-error : {edge.err}\n" 

        return mappings+edges_info


    def __find_start(self):
        # extract start node
        usr_g = self.usr_graph
        for node in usr_g.nodes:
            if node.name == "start":
                self._start = node
                return node
        raise Exception("Start node not found") 


    def __find_end(self):
        # finding state that represent end state
        usr_g = self.usr_graph
        for node in usr_g.nodes:
            # if the only non-error outgoing edge is pointing "end" state
            #if (node.valid_edge() == 1) and (node.points_to_end()):
            #   self._end = node
            #   return node
            if (len(node.edges)==1) and (node.points_to_end()):
                #self._end = node
                self._end.append(node.name)
                return node
        raise Exception("End node not found")

    def _represent(self):
        # takes user defined form and map it to this FSM Graph
        usr_graph = self.usr_graph
        self.repr = {} # representation of name -> node
        for node in usr_graph.nodes:
            if node.name == "end":
                continue   # if node is the end, not included
            n = self.create_node(node.name)      
            self.repr[node.name] = n
            self.nodes.append(n)

    def return_end(self):
        return self.find(self._end[0])

    def return_start(self):
        return self.find(self._start.name) 

    def create_node(self, name):
        if name == "start":
            n = FSM_Node(0, "start")
        #elif name == self._end.name:
        elif name in self._end:
            n = FSM_Node(0, "end")
        else:
            n = FSM_Node(FSM_Graph.STATE_NUM)
            FSM_Graph.STATE_NUM += 1 
        return n    
         
    def find(self, name) -> FSM_Node :
        try:
            return self.repr[name]
        except:
            raise Exception(f"{name} not included in FSM logic") 
    
    def create_edge(self, start, target, fname, key, condition, err):
        # function to create an FSM_Edge between 2 FSM_Node with attributes
        ed = FSM_Edge(start, target, fname, key, condition, err)
        self.edges.append(ed)
        start.add_edge(ed)

    def remove_edge(self, e):
        logger.debug("removing edge %s->%s from fsm"%(e.start.name, e.target.name))
        to_pop = None
        for i in range(len(self.edges)):
            #if self.edges[i] == e:
            if self.edges[i].equals(e):
                #self.edges.pop(i) # remove the edge from list
                to_pop = i
        foc = self.edges[to_pop]
        logger.info("%s->%s"%(foc.start.name, foc.target.name))
        if to_pop:
            self.edges.pop(to_pop) 

    def remove_node(self, n):
        logger.debug("Removing node %s"%(n.name))
        to_pop = None
        for i in range(len(self.nodes)):
            if self.nodes[i] == n:
                to_pop = i
        if to_pop:
            self.nodes.pop(to_pop)

    def remove_def_action(self , n):
        logger.debug("removing default action of node %s"%(n.name))
        if n.name in self.default_action:
            self.default_action.pop(n.name)

    def add_def_action(self, n, err):
        logger.debug("adding default action fo node %s with err %s"%(n.name, err))
        if n.name in self.default_action:
            try:
                self.default_action[n.name].append(err) 
            except:
                self.default_action[n.name] = [self.default_action[n.name]]
                self.default_action[n.name].append(err)

        else:
            self.default_action[n.name] = err

    def convert(self):
        # convert from User Input into FSM logic
        logger.debug("Converting User input into FSM logic")
        usr_graph = self.usr_graph
        
        for edge in usr_graph.edges:
            frm = edge.nd_from
            to = edge.nd_to
            
            #if frm == self._end:
            if frm.name in self._end:
                continue # end should not be pointing anywhere else
            elif to.name == "end":
                frm_node = self.find(frm.name)
                #self.default_action.append(frm.name)
                self.default_action[frm_node.name]=edge.err
                continue
            
            frm_node = self.find(frm.name)
            to_node = self.find(to.name)
            # create edge
            ed = self.create_edge(
                frm_node, to_node, to.name, to.key, to.condition, edge.err 
            )
        
