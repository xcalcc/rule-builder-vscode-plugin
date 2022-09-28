#!/usr/bin/python3

import sys
import os
import subprocess
import argparse
import logging
from usr_graph import Node, Edge, Graph
from fsm import FSM_Graph, FSM_Node, FSM_Edge

# TODO: translate only tagging in .mi file
rb_loc = subprocess.run(['which', 'rbuild'], stdout=subprocess.PIPE, universal_newlines=True)
if rb_loc.returncode != 0:
    print("RBNotFound: Library not found, you may not have included the rule builder to your PATH")
    sys.exit(1)
rb_loc = rb_loc.stdout.strip()
rb_loc = os.path.dirname(rb_loc)
# Parsing arguments
languages=['c', 'java']
parser = argparse.ArgumentParser(description="Tranlsate")
parser.add_argument('input', nargs='+', help='.mi file for input') # there may be multiple .mi file as input
parser.add_argument('-l', '--lang', help='Target language')
parser.add_argument('-r', '--ref', help='reference mi file, if multiple, concatenate with :')
parser.add_argument('-n', '--name', help='rule name')
args = parser.parse_args()

# ======= User Input validation ========
# input file .mi
for i in args.input:
    if not i.endswith('.mi'):
        print("Invalid input file: {}".format(args.input))
        sys.exit(-1)
input_files = args.input

# error name
if not args.name:
    ERROR_NAME="rule"
else:
    ERROR_NAME=args.name

if not args.lang:
    print("Please specify language with -l {c,java}")
    sys.exit(-1)

if args.lang not in languages:
    print("Invalid target language. Choose either 'c' or 'java'")
    sys.exit(-1)
lang = args.lang

print(f"converting input files: {input_files} into {ERROR_NAME}.{lang}")
references = args.ref.split(":")
print(f"references: {references}")

NODE='NODE'
EDGE='EDGE'

def create_usr_graph(f):
    # returning a usr_graph
    fopen = open(f, 'r')
    flines = fopen.readlines()
    content = []
    for f in flines:
        content.append(f.strip())
    gr = Graph()
    for i in content:
        fields = i.split('|')
        if fields[0] == NODE:
            gr.add_nodes(*fields[1:])
        elif fields[0] == EDGE:
            gr.add_edge(*fields[1:])
        else:
            raise Exception(f"Invalid field, neither node nor edge: {fields[0]}")
    return gr

def create_fsm(g):
    # converting from the usr graph into fsm mode 
    fsm_g = FSM_Graph(g)
    fsm_g.convert()
    return fsm_g

user_graphs = []
for i in input_files:
    user_graphs.append(create_usr_graph(i))

fsm_list = []
for i in user_graphs:
    fsm_list.append(create_fsm(i))

# copy macros/header to temporary .h first
#read = open('template.h', 'r')
template_path=os.path.join(rb_loc, 'lib/translator/template.h')
read = open(template_path, 'r')
write = open('rule.h', 'w')
to_read = read.readlines()
for r in to_read:
    write.write(r)

# ======== WRITING RULES ===========

def write_transitions(fsm_g):
    for edge in fsm_g.edges:
    # START
        start = edge.start.name
        # FNAME
        if lang=="java":
            # lookup to .mi file 
            reference=args.ref
            #fname = FSM_Graph.find_mangle_f(edge.fname, "org.apache.commons-commons-email.o.vtable.mi")
            #fname= FSM_Graph.find_mangle_f(edge.fname, reference)
            fname = FSM_Graph.find_mangle_f_multifile(edge.fname, *references)
        else:
            fname = edge.fname    
        # KEY
        if edge.key == "this":
            key = "THIS_POINTER"
        elif edge.key == "return":
            key = "GET_RET"     
        else:
            key = "NULL"
        # CONDITION
        temp = edge.cond_parse()
        if len(temp) == 0: # no condition
            condition = "1"
        else:
            if temp[0][1] == 'true':
                condition=f"GET_VALUE(GET_ARG({temp[0][0]}))"
            elif temp[0][1] == 'false':
                condition =f"NOT(GET_VALUE(GET_ARG({temp[0][0]})))"
            elif temp[0][1] == 'sensitive':
                condition=f"NOT(IS_SENSITIVE_DATA({temp[0][0]}))"
            elif temp[0][1] == 'not_sensitive':
                condition=f"IS_SENSITIVE_DATA({temp[0][0]})"
        # NEXT STATE
        target=f"\"{edge.target.name}\""
        # ERROR EXIST
        if edge.err == "none":
            error = f"\"\"" 
        else:
            error= f"\"{edge.err}\""
        write.write(f"\t\tADD_TRANSITION(\"{start}\", \"{fname}\", {key}, {condition}, {target}, {error})\n")
      
    for e in fsm_g.default_action:
        if fsm_g.default_action[e] == "none":
            rep = ""
        else:
            rep = fsm_g.default_action[e]
        state_name = fsm_g.find(e).name
        write.write(f"\t\tSET_DEFAULT_ACTION(\"{state_name}\",\"{rep}\")\n");


# BEGIN PART (common to all fsm)
write.write("IMPORT1\nIMPORT2\n")
write.write(f"CLASS({ERROR_NAME})\n")
write.write(f"\tSTART_RULE({ERROR_NAME})\n")
write.write(f"\t\tBUILD_BEGIN(\"{ERROR_NAME}\")\n")
write.write(f"\t\tNEW_START_STATE\n")
write.write(f"\t\tNEW_FINAL_STATE\n")
# WRITE TRANSITIONS
for i in fsm_list:
    write_transitions(i)
# END PART (also common to all fsm)
write.write(f"\t\tBUILD_END(\"{ERROR_NAME}\")\n")
write.write(f"\t\tRULE_INFO(\"{ERROR_NAME}\", \"DEFAULT\")\n")
write.write(f"\tEND_RULE\n")
write.write(f"END_CLASS\n")

# depending on language need to check
if lang == 'c':
    command = f"cpp -P rule.h > {ERROR_NAME}.cxx"
    #command = ["cpp", "-P", "rule.h", '>', f"{ERROR_NAME}.cxx"]
else:
    command = f"cpp -P -DLANG_JAVA rule.h > {ERROR_NAME}.java"
    #command = ["cpp", "-P", "-DLANG_JAVA", "rule.h", '>', f"{ERROR_NAME}.java"]

os.popen(command)
print(f"Check your {ERROR_NAME}.{'cxx' if lang=='c' else 'java'}")

sys.exit(0) # exit with command 0 shows success
