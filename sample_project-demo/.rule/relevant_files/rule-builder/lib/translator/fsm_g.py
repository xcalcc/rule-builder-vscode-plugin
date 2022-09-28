#!/usr/bin/python3

"""
fsm_g: FSM Graph
graph representative of FSM 
contains Node, Edge, and Graph
"""

import logger
import sys
from .ConditionParse import ConditionParse

logger = logger.retrieve_log()

class GraphCreationError(Exception):
    pass
class GraphInvalid(Exception):
    pass
class NodeCreationError(GraphCreationError):
    pass
class EdgeCreationError(GraphCreationError):
    pass
class GraphMergeError(GraphCreationError):
    pass

class FSM_G_Node:
    def __init__(self, name:str):
        self.name = name
        self.edges = []
    def add_edge(self, e):
        self.edges.append(e)
    def __repr__(self):
        return self.name

class Func:
    def __init__(self, fun_name, condition, key):
        self.fun_name = fun_name
        self.condition = condition
        self.key = key
    
    def __eq__(self, other):
        return (self.fun_name == other.fun_name and
            self.condition ==  other.condition and
            self.key == other.key)

class FSM_G_Edge:
    def __init__(self, source: FSM_G_Node, target:FSM_G_Node,
                fun_name, condition, key, err):
        '''
        source, target: FSM_G_Node
        '''
        self.source = source
        self.target = target
        self.fun_name = fun_name
        self.condition = condition
        self.key = key
        self.err = err
    def __repr__(self):
        return "%s=>%s"%(self.source.name, self.target.name) 

    def change_source(self, source):
        self.source = source
    
    def change_target(self, target):
        self.target = target

class FSM_G_Graph:

    def __init__(self):
        self.nodes = {} # represent it as a 'name' to node object
        self.edges = []
        self.functions = [] # function declaration, for merge assertion later
        self.start = None # starting point of FSM
        self.end = None # end point of FSM
        self.def_acts = {} # default action store
    
    @staticmethod
    def find_mangle_func_name(fname, ref_file):
        '''
        find mangled function name based on function name
        '''
        try:
            f = open(ref_file, 'r')
        except FileNotFoundError as e:
            logger.error("reference file not found")
        lines = f.readlines()
        for line in lines:
            splits = line.strip().split('|')
            if "<%s>"%fname == splits[0]:
                return splits[1]
        return None
    
    @staticmethod
    def find_mangle_func_name_mult(fname, *files):
        '''
        reading from multiple files
        '''
        logger.debug("Finding mangle name for %s"%fname)
        f_to_read = list(files)
        for i in f_to_read:
            name = FSM_G_Graph.find_mangle_func_name(fname, i)
            if name:
                return name 
        return None
    
    def check(self):
        '''check whether the graphs is valid'''
        if self.start == None and self.end == None:
            logger.error("Can't find start or end node")
            raise GraphInvalid()

    def add_node(self, name):
        '''
        add node to graph (taking note of START and END as well)
        ''' 
        logger.debug("adding %s to graph"%name)
        if name in self.nodes:
            logger.error("duplicate node: %s"%name)
            raise NodeCreationError("Duplicate node detected")
        # if not exist, create node and add reference
        node_o = FSM_G_Node(name)
        self.nodes[name] = node_o
        if name == "START":
            logger.debug("Start node found")
            self.start = node_o
        elif name == "END":
            logger.debug("End node found")
            self.end = node_o

        logger.debug("%s inserted to list of nodes"%name)
    
    def add_edge(self, source: str, target: str,
                fun_name, condition, key, err):
        '''
        linking 2 EXISTING node in the graph
        '''
        logger.debug("adding edge to connect %s and %s"%(source, target))
        
        # checks if 2 nodes exist
        if source not in self.nodes:
            logger.error("%s not found"%source)
            raise EdgeCreationError()
        if target not in self.nodes:
            logger.error("%s not found"%target)
            raise EdgeCreationError()
        # get node object, link them 
        source_o = self.find_node(source)
        target_o = self.find_node(target)
        
        edge_o = FSM_G_Edge(source_o, target_o, fun_name,
                    condition, key, err)
       
        self.edges.append(edge_o)
        source_o.add_edge(edge_o)
        # Add the functions used
        func = Func(fun_name, condition, key)
        self.functions.append(func)

    def find_node(self, label: str):
        '''
        return node object where name matches
        '''
        if label in self.nodes:
            return self.nodes[label]
        else:
            return None

    def add_def_acts(self, name, err):
        '''
        adding Fsm_default_action (hanging state)
        notify if there is error
        ''' 
        logger.debug("Finding Fsm_default_action for %s"%name)
        if name in self.nodes:
            self.def_acts[name] = err
        else:
            # not in node
            logger.error("node not found")
            raise GraphCreationError("node not found")

    def pointed_by_start(self):
        '''
        return edges that is point to start
        '''
        return [node for node in self.start.edges]

    def points_to_end(self):
        '''
        return edges that point to end
        '''
        edges = []
        for edge in self.edges:
            if edge.target == self.end:
                edges.append(edge)
        return edges

    
    def merge(self, other):
        '''
        merging this fsm with an incoming FSM
        assert that function can only belong to 1 fsm
        ''' 
        logger.debug("FSM Merge on progress")
        # check between the functions if there is anything shared         
        for f1 in self.functions:
            for f2 in other.functions:
                if f1 == f2:
                    logger.error("The 2 FSM shares function %s"%f1.fun_name)
                    raise GraphMergeError()
        logger.debug("merge-ability check passed") 
        
        # self's start has to point to other's start
        edges = other.pointed_by_start()
        logger.debug("Edges that start points to: %s"%edges)
        for edge in edges:
            # change the start for every edge
            edge.change_source(self.start)
            self.start.edges.append(edge)

        # edges that point to end  
        edges = other.points_to_end() 
        logger.debug("Edges that point to end: %s"%edges) 
        for edge in edges:
            # change the end for every edge
            edge.change_target(self.end)
            
        # add collection of nodes and edges from other to current 
        
        for node in other.nodes:
            if other.nodes[node].name == 'START' or other.nodes[node].name == 'END':
                continue # no need to add start and end again
            if node in self.nodes: # avoid clashes
                other.nodes[node].name += '2'
                self.nodes[node+'2'] = other.nodes[node]
            else:
                self.nodes[node] = other.nodes[node]

        self.edges += other.edges

        # result of changes
        logger.debug("After change, start points to %s"%self.pointed_by_start())
        logger.debug("After change, end is pointed by %s"%self.points_to_end())
        logger.debug("Nodes: %s"%self.nodes)
        logger.debug("Edges: %s"%self.edges)

