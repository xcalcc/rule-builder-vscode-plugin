#!/usr/bin/python3
"""
fsm

graph data structure representation of FSM
contains node, edge and graph
"""

import sys
from .condition_parse import ConditionParse
from common.XcalException import XcalException
from common.XcalLogger import XcalLogger
from ruleBuildService.config import ErrorNo

class GraphCreationError(Exception):
    '''general exception when constructing fsm'''
    pass
class GraphInvalid(Exception):
    '''exception when graph is wrong after validation check'''
    pass
class NodeCreationError(GraphCreationError):
    '''exception when a trouble is encountered when creating nodes'''
    pass
class EdgeCreationError(GraphCreationError):
    """exception when a trouble is encountered when creating edge
    between 2 nodes"""
    pass
class GraphMergeError(GraphCreationError):
    '''when error occurs during merge of 2 graphs'''
    pass

class Func:
    """simple function object

    object for getiting function information, used for duplicate checking validation

    Attributes:
        fun_name (str): function name
        condition (str): condition to trigger transition
        key (str): key focus of transition
    """
    def __init__(self, fun_name, condition, key):
        self.fun_name = fun_name
        self.condition = condition
        self.key = key

    def __eq__(self, other):
        return (self.fun_name == other.fun_name and
            self.condition ==  other.condition and
            self.key == other.key)


class FSM_G_Node:
    """state representation in FSM

    Node is equivalent to states in FSM where each are identifiable
    by a name.

    Args:
        name (str): identifier of a node/state

    Attributes:
        name (str): identifier of a node/state
        edges (list): list of FSM_G_Edge objects
    """
    def __init__(self, name):
        self.name = name
        self.edges = [] # initializing edges

    def add_edge(self, e):
        """new edge

        Adding edge to list of edges.

        Args:
            e (FSM_G_Edge): edge object to be appended
        """
        self.edges.append(e)

    def __repr__(self):
        return self.name

class FSM_G_Edge:
    """link representation in FSM

    Edge is equivalent to directed link between 2 nodes. In FSM,
    The link has attributes attached which means that in order for
    the transition between one state to another happen,

    Args:
        source (FSM_G_Node): where the edge is pointing from
        target (FSM_G_Node): where the edge is pointing to
        fun_name (str): function name that triggers the transition
        condition (str): condition attached to function (if any)
        key (str): primary focus of what to track from the function
        err (str): whether or not this transition produce any error
    """
    def __init__(self, source: FSM_G_Node, target:FSM_G_Node,
                fun_name, condition, key, err, msg):
        self.source = source
        self.target = target
        self.fun_name = fun_name
        self.condition = condition
        self.key = key
        self.err = err
        self.msg = msg

    def __repr__(self):
        return "%s=>%s"%(self.source.name, self.target.name)

    def change_source(self, source):
        """redirecting source

        redirecting source to a different node
        Args:
            source (FSM_G_Node): new node for source
        """
        self.source = source

    def change_target(self, target):
        """redirecting target

        redirecting target to a different node
        Args:
            target (FSM_G_Node): new node for target
        """
        self.target = target

class FSM_G_Graph:
    """graph representation of FSM

    Big picture of FSM as represented by FSM. Nodes are the states and
    Edges are transitions. The graph is entry point for users to operate

    Attributes:
        nodes (dict): mapping name to FSM_G_Node object
        edges (FSM_G_Edge): list of existing edges on the graph
        functions (list): list of functions (for transitions) to use
        start (FSM_G_Node): entry point of graph
        end (FSM_G_Node): end/exit point of graph
        def_acts (dict): node mapping to error name if any
    """

    def __init__(self):
        self.nodes = {} # represent it as a 'name' to node object
        self.edges = []
        self.functions = [] # function declaration, for merge assertion later
        self.start = None # starting point of FSM
        self.end = None # end point of FSM
        self.def_acts = {} # default action store, node : (error, int_msg)
        self.logger = XcalLogger("fsm", "__init__")

    @staticmethod
    def find_mangle_func_name(fname, ref_file):
        """matching mangled function name

        for java, find mangled function name based on the
        normal function name from the reference file.

        Args:
            fname (str): function name under concern
            ref_file (str): path to reference file

        Returns:
            str: find matching function name, None if not found
        """
        try:
            f = open(ref_file, 'r')
        except FileNotFoundError as e:
            # _logger.error("reference file not found")
            raise XcalException("fsm", "find_mangle_func_name", 
                                "file not found: %s" % ref_file,
                                err_code=ErrorNo.E_RESOURCE_NOT_FOUND)
        lines = f.readlines()
        for line in lines:
            splits = line.strip().split('|')
            if "<%s>"%fname == splits[0]:
                f.close()
                return splits[1]
        f.close()
        return None

    @staticmethod
    def find_mangle_func_name_mult(fname, *files):
        """finding mangled function name

        macro find of mangled function name based on function name
        on the reference file. Uses find_mangle_func_name under the
        hood

        Args:
            fname (str): function name under concern
            files (list): list of reference files to read from

        Returns:
            str: find matching function name, none if not found
        """
        f_to_read = list(files)
        for i in f_to_read:
            name = FSM_G_Graph.find_mangle_func_name(fname, i)
            if name:
                return name
        return None

    def check(self):
        '''check if graph is valid'''
        self.logger.debug("check", "checking whether FSM is valid")
        if self.start == None and self.end == None:
            raise XcalException("fsm", "check", "invalid fsm", 
                                er_code=ErrorNo.E_FSM_INVALID)

    def add_node(self, name):
        """adding node to graph

        adding a new node into the graph by just the name. If
        conflict of name is found (duplicate name), will report error.

        Args:
            name (str): name as identifer of the node

        Raises:
            NodeCreationError: when duplicate node is detected
        """

        self.logger.debug("add_node", "adding node %s" % name)
        if name in self.nodes:
            raise XcalException("fsm", "add_node", "name: %s already exist in graph" % name,
                                err_code=ErrorNo.E_FSM_INVALID)

        # if not exist, create node and add reference
        node_o = FSM_G_Node(name)
        self.nodes[name] = node_o
        if name == "START":
            # _logger.debug("Start node found")
            self.logger.debug("add_node", "START NODE FOUND")
            self.start = node_o
        elif name == "END":
            # _logger.debug("End node found")
            self.logger.debug("add_node", "END NODE FOUND")
            self.end = node_o


    def add_edge(self, source: str, target: str,
                fun_name, condition, key, err, msg):
        """adding edge to graph

        adding edge that connects 2 EXISTING nodes into the graph. Pass along
        necessary information regarding the transition attributes.

        Args:
            source (FSM_G_Node): node where transition starts
            target (FSM_G_Node): node where transition ends
            fun_name (str): function name that triggers transition
            condition (str): condition attached to the function
            key (str): focus of the function
            err (str): error name when this transition happens (if any)
            msg (str): id of the message presented

        Raises:
            EdgeCreationError: reported if either source or target is not found
        """
        # _logger.debug("adding edge to connect %s and %s"%(source, target))
        self.logger.debug("add_edge", "adding edge to connect %s and %s" % (source, target))

        # checks if 2 nodes exist
        if source not in self.nodes:
            raise XcalException("fsm", "add_edge", "node %s not found" % source,
                                err_code=ErrorNo.E_FSM_INVALID)
        if target not in self.nodes:
            raise XcalException("fsm", "add_edge", "node %s not found" % target,
                                err_code=ErrorNo.E_FSM_INVALID)
        # get node object, link them
        source_o = self.find_node(source)
        target_o = self.find_node(target)

        edge_o = FSM_G_Edge(source_o, target_o, fun_name,
                    condition, key, err, msg)

        self.edges.append(edge_o)
        source_o.add_edge(edge_o)
        # Add the functions used
        func = Func(fun_name, condition, key)
        self.functions.append(func)
        return "<"+fun_name+">" # adjust for annotation later

    def find_node(self, label: str):
        """getting node based on label

        Based on the identifier (label), find node that contains that name

        Args:
            label (str): identifier name to be searched

        Returns:
            FSM_G_Node: the node containing matching label
        """
        if label in self.nodes:
            return self.nodes[label]
        else:
            return None

    def add_def_acts(self, name, err, msg):
        """adding default action

        adding a new Fsm_default_action on to a certain node,
        and attach with error if any

        Args:
            name (str): identifier of node
            err (str): error string

        Raises:
            GraphCreationError: if node is not found
        """
        self.logger.debug("add_def_acts", "adding default actionn to %s" % name)
        if name in self.nodes:
            self.def_acts[name] = (err, msg)
        else:
            # not in node
            raise XcalException("fsm", "add_def_acts", "node: %s not found" % name,
                                err_code=ErrorNo.E_FSM_INVALID)

    def pointed_by_start(self):
        '''get edges pointed by the graph starting point'''
        return [node for node in self.start.edges]

    def points_to_end(self):
        '''return edges that point to end'''
        edges = []
        for edge in self.edges:
            if edge.target == self.end:
                edges.append(edge)
        return edges


    def merge(self, other):
        """merging 2 graphs together

        From 2 graphs, merge them by combining/redirecting the start
        and end node of the 2 separate graphs together. By the end, result
        should have 1 starting point and 1 end point.

        Args:
            other (FSM_G_Graph): graph object to merge with

        Raises:
            GraphMergeError: when something goes wrong during merging process
        """
        self.logger.debug("merge", "merging FSM...")
        # check between the functions if there is anything shared         
        for f1 in self.functions:
            for f2 in other.functions:
                if f1 == f2:
                    raise XcalException("fsm", "merge", "error encountered when merging",
                                        err_code=ErrorNo.E_FSM_INVALID)
        # _logger.debug("merge-ability check passed")
        self.logger.debug("merge", "merge-ability check passed")

        # self's start has to point to other's start
        edges = other.pointed_by_start()
        # _logger.debug("Edges that start points to: %s"%edges)
        for edge in edges:
            # change the start for every edge
            edge.change_source(self.start)
            self.start.edges.append(edge)

        # edges that point to end  
        edges = other.points_to_end()
        # _logger.debug("Edges that point to end: %s"%edges)
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

