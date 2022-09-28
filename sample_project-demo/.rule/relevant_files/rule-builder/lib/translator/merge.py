#!/usr/bin/python3

# ============
# merge
# given 2 fsm objects, combine the 2 objects into one
# while persisting the logic
# ============

from .fsm import FSM_Graph, FSM_Node, FSM_Edge
import logger
logger = logger.retrieve_log()


def combine(fsm_1:FSM_Graph, fsm_2: FSM_Graph) -> FSM_Graph:
    # rough combination of 2 fsm graph
    #start =  fsm_1.find("start")
    start = fsm_1.return_start()
    #end = fsm_2.find("end")
    end = fsm_2.return_end()
    for e in fsm_2.edges:
        if e.start.name == 'start':
            # replace the start to fsm_1.start
            e.replace_start(start)
            fsm_1.edges.append(e)
            start.add_edge(e)
            fsm_1.add_node(e.target)
        elif e.target.name == 'end':
            # replace end to fsm_1.end
            e.replace_end(end)
            fsm_1.edges.append(e)
            fsm_1.add_node(e.start)
        else:
            fsm_1.edges.append(e) 
            fsm_1.add_node(e.start)
            fsm_1.add_node(e.target) 
    fsm_1.default_action = {**fsm_1.default_action, **fsm_2.default_action}
    return fsm_1

def find_ambiguous(node):
    logger.debug("%s contains %s edges"%(node.name, len(node.edges))) 
    if len(node.edges) <= 1:
        return None 
    else:
        logger.debug("Searching for ambiguity")
        for i in range(0, len(node.edges)-1):
            for j in range(i+1, len(node.edges)):
                if node.edges[i] == node.edges[j]:
                    logger.info("AMBIGUITY DETECTED")
                    return (node.edges[i], node.edges[j])

def resolve(fsm, e1, e2):
    # resolve ambiguity between 2 edges

    # check which case it belongs to
    if e1.err == "none" and e2.err == "none":
        logger.debug("CASE 1: BOTH EDGES DOESN'T HAVE ERROR")
        # combine target of e1 and e2 together 
        fsm.remove_edge(e2)
        e2.start.remove_edge(e2)
        
        # e1.target points to all nodes e2.target points to
        for e in e2.target.edges:
            e.replace_start(e1.target)
            e1.target.add_edge(e)
        
        # whatever points to e2.target points to e1 except for e1.start
        for e in fsm.edges:
            if e.target == e2.target:
                e.start.remove_edge(e)
                fsm.remove_edge(e)
                if not e1.start == e.start:
                    e.replace_end(e1.target)

        # remove e2.target node from fsm
        fsm.remove_node(e2.target)
        if e2.target.name in fsm.default_action:
            fsm.add_def_action(e1.target, fsm.default_action[e2.target.name])
        fsm.remove_def_action(e2.target)
   
    elif (e1.err!= "none" and e2.err == "none") or (e1.err =="none" and e2.err!="none"):
        logger.debug("e1 XOR e2 has error")
        err_edge = None
        non_err_edge = None
        # get which edge gets the error
        if e1.err == "none":
            non_err_edge = e1
            err_edge = e2
        else:
            non_err_edge = e2
            err_edge = e1
        
        if err_edge.target.name == "end":
            logger.debug("CASE 2: error edge points to end state")
            # non_err_edge will remain, err_edge will be removed
            # and fsm_default_action added to non_err_edge.target with that error
            logger.debug("Error Edge: %s->%s"%(err_edge.start.name, err_edge.target.name))
            fsm.remove_edge(err_edge)

            err_edge.start.remove_edge(err_edge)
            #fsm.default_action[non_err_edge.target.name] = err_edge.err 
            fsm.add_def_action(non_err_edge.target, err_edge.err)
        else:
            logger.debug("CASE 3: error edge doesn't point to end state")        
            # err_edge will remain and non_err_edge removed
            # remove non_err_edge.target move all attr from non_err_edge.target to err_edge.target
            fsm.remove_node(non_err_edge.target)
            
            # outgoing edge transfer
            for edge in none_err_edge.target.edges:
                edge.replace_start(err_edge.target)
                err_edge.target.add_edge(edge)

            # incoming edge transfer            
            for edge in fsm.edges:
                if edge.target == non_err_edge.target:
                    if edge.start == err_edge.start:
                        continue
                    else:
                        edge.replace_end(err_edge.target)
            # default action transfer from one to another
            for i in fsm.default_action:
                if i == non_err_edge.target.name:
                    res = fsm.default_action[i]
                    if isinstance(i, list):
                        for e in res:
                            fsm.add_def_action(err_edge.target, e) 
                    else:
                        fsm.add_def_action(err_edge.target, rers)
                    fsm.remove_def_action(i)


def bfs_resolve(fsm):
    logger.debug("Doing breadth-first-search to resolve ambiguity")
    while 1:
        # do a breadth first search finding ambiguity, if not found exit
        logger.debug(fsm)
        for node in fsm.nodes:
            amb = find_ambiguous(node)
            if amb:
                resolve(fsm, amb[0], amb[1])
        if not amb:
            break
    logger.debug(fsm)

def merge(fsm_1:FSM_Graph, fsm_2:FSM_Graph) -> FSM_Graph:
    logger.debug("Merging FSM in progress ...")
    # rough combine the 2 fsm 
    comb_fsm = combine(fsm_1, fsm_2)
    logger.info("Combination of FSM completed")
    #logger.debug(comb_fsm)
    logger.debug("rough combined graph info:\n%s"%(comb_fsm))

    logger.debug("====== Reduction ======")
    # removing ambiguity iteratively 
    # example:
    bfs_resolve(comb_fsm)
    logger.debug(comb_fsm.default_action)
    return comb_fsm

