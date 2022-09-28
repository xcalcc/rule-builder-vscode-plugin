# ===============================
# usr_graph.py
# graph representation of what
# the user has buil tin the UI
# ===============================
start = "START"
end = "END"
import logger

logger = logger.retrieve_log()

class Node:

    def __init__(self, name, condition, key, idn):
        self.name = name  # function name
        self.condition = condition 
        self.key = key  
        self.idn = idn # identifier
        self.edges = [] # list of adjacent nodes
    
    def __eq__(self, other):
        if isinstance(other, Node):
            return self.idn == other.idn
        return False

    def add_edge(self, edge):
        self.edges.append(edge)

    def valid_edge(self):
        # count number of edges that are not producing error
        count = 0
        for e in self.edges:
            if e.err == "none":
                count += 1     
        return count
    
    def show_adj(self):
        # show adjacent nodes
        for e in self.edges:
            print(e)

    def points_to_end(self):
        for e in self.edges:
            if e.nd_to.name == "end":
                return True 
        return False

class Edge: 

    def __init__(self, nd_from:Node, nd_to:Node, err):
        self.nd_from = nd_from
        self.nd_to = nd_to
        self.err = err

    def __eq__(self, other):
        if isinstance(other, Edge):
            return (self.nd_from==other.nd_from and self.nd_to==other.nd_to)
        return False
    
    def __repr__(self):
        return f"{self.nd_from.name}->{self.nd_to.name}" 
            
class Graph:

    def __init__(self):
        self.start = None  # start node
        self.end = None  # end node
        self.nodes = []  # node collection
        self.edges = []  # edge collection

    def add_nodes(self, *args):
        n = Node(*args)
        if n.idn=="start":
            self.start = n 
        self.nodes.append(n) 

    def add_edge(self, nd_from, nd_to, err):
        a = self.find(nd_from)
        b = self.find(nd_to) 
        e = Edge(a, b, err) 
        a.add_edge(e) 
        self.edges.append(e)
    def find(self, idn):
        for n in self.nodes:
            if n.idn==idn:
                return n
        raise Exception("Node not found")



