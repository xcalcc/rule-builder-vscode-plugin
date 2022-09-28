#!/usr/bin/python3

"""
Accepting a Tag API,
can work for classes, functions or arguments
When processing, should be able to generate file where it contains
rbc Set_tag(<key>, <string>)
"""

import sys
import re
import os
try:
    import logger
    logger = logger.retrieve_log()
except:
    print("import not found")

java_builtin = ['byte', 'short', 'int', 'long', 'float', 'double', 'char', 'boolean', 'void', '']

class KeyNotRecognised(Exception):
    def __init__(self, msg=""):
        super().__init__(msg)

class FuncParse:
    def __init__(self, sig):
        logger.info("Parsing a function")
        cls_matcher = re.search(r'(?<=<).*(?=:)', sig)
        assert (cls_matcher is not None), "Can't match class name: signature: %s"%sig
        self.sig = sig
        logger.debug("sig = %s"%(self.sig))

        self.cls_name = cls_matcher.group(0)
        logger.debug("class name = %s"%(self.cls_name))
        method_sig_matcher = re.search(r'(?<=: ).*(?=>)', sig)
        assert (method_sig_matcher is not None), "Can't match method signature, signature: %s"%sig
        method_sig = method_sig_matcher.group(0)
        ret_matcher = re.search(r'^.*(?= )', method_sig)
        self.ret_type = ret_matcher.group(0)
        logger.debug("return type = %s"%self.ret_type)
        met_name_matcher = re.search(r'(?<= ).*(?=\()', method_sig)
        assert (met_name_matcher is not None), "can't match method name, method signature: %s"%method_sig
        self.met_name = met_name_matcher.group(0)
        logger.debug("method name = %s"%(self.met_name))
        args_matcher = re.search(r'(?<=\().*(?=\))', method_sig)
        assert (args_matcher is not None), "Can't match arg list, method signature: %s"% method_sig
        self.args = args_matcher.group(0).split(',')
        logger.debug("arguments = %s"%self.args)
        interface_matcher = re.search(r'^(I)', sig)
        if interface_matcher:
            self.is_interface = True
        else:
            self.is_interface = False
        logger.debug("is interface = %s"%self.is_interface)
    

# ACTUAL STEP BY STEP CREATION HERE
def parse_tag(line):
    '''
    parsing the line into tag
    '''
    fields = line.split('|') 
    fparsed = FuncParse(fields[1])
    key = fields[2]
    tag = fields[3]

    logger.info("function: %s, key: %s, tag: %s"%(fparsed.sig, key, tag))
    fpath = create_file(fparsed.cls_name)
    logger.info("Copying content of template.h into %s"%fpath)
    fpath_write = open(fpath,'w')
    template_file = open('template.h' ,'r')
    read = template_file.readlines()
    for r in read:
        fpath_write.write(r) 

    logger.info("Put content into file %s"%fpath)
    dump_cls_header(fpath_write, fparsed.cls_name, True, fparsed.is_interface) 
    dep_set = get_dep_class(fparsed)
    logger.info("dependencies: %s"%dep_set)

    logger.info("Writing Function Signature")
    write_func_signature(fpath_write, fparsed)
    write_func_body(fpath_write, key, tag)
    write_ret(fpath_write, fparsed.ret_type)
    write_func_close(fpath_write)
    write_class_close(fpath_write)
        

def dump_cls_header(out_file, cls_name, dump_import, interface_map):
    logger.info("Calling dump_cls_header with %s ,%s ,%s"%(out_file, cls_name, interface_map))
    index = cls_name.rfind('.')
    if index != -1:
        package = cls_name[:index]
        cls_only_name = cls_name[index+1:]
        out_file.write("PACKAGE(%s)\n"%package)
    if dump_import:
        out_file.write("IMPORT1\n")
    if interface_map:
        out_file.write("INTERFACE(%s)\n"%cls_only_name)
    else:
        out_file.write("CLASS(%s)\n"%cls_only_name)

def get_dep_class(sig):
    '''
    get all dependency classes from signature. javac will require dependencies
    '''
    logger.info("Getting Dependencies from the %s"%sig)
    ret_type = sig.ret_type.replace('[]', '') 
    args = sig.args
    dep_set = set()
    if ret_type not in java_builtin:
        dep_set.add(ret_type)
    for arg in args:
        arg = arg.replace('[]','')
        if arg not in java_builtin:
            dep_set.add(arg) 
    return dep_set
    

def create_file(cls_name):
    '''
    based on class name,create the java file with package
    '''
    logger.info("creating path for %s"%cls_name)

    file_path = cls_name.replace('.', os.sep)
    file_path += '.h'
    logger.debug("path: %s"%(file_path))
    dir_name = os.path.dirname(file_path)
    if dir_name!="" and not os.path.exists(dir_name):
        os.makedirs(dir_name)
    out_file = open(file_path, 'w')

    logger.info("Created %s"%file_path)
    out_file.close()
    return file_path

def write_func_signature(out_file, sig):
    '''
    write function signature: public int add(int arg1, int arg2)
    '''
    # extract return type, function signature name and arguments
    fname = sig.met_name
    cls_name = sig.cls_name
    ret_type = sig.ret_type 
    arguments = ""
    logger.debug("initial fname=%s, cls_name=%s, ret_type=%s"%(fname,cls_name, ret_type))

    if fname.find("<init>") != -1:
        # in java this will turn <init> into public Point(...)
        logger.debug("init detected")
        names = cls_name.split('.')
        fname = names[len(names) - 1]
        ret_type = ""
        logger.debug('init mode: fname: %s'%fname)
    
    i = 1
    args = sig.args
    for arg in args:
        if arg in ("void", ""):
            arguments += arg
        else:
            arguments += arg + " arg"+ str(i) + ", "
            i = i + 1
    arguments = arguments.rstrip(', ') 

    if sig.is_interface:
        modifiers = "default"
    else:
        modifiers = "public"
    fname = fname+'('+arguments+')'
    logger.debug("writing")
    out_file.write('        FUNC_SIG(%s,%s,%s)\n'%(modifiers, ret_type, fname))

def write_func_body(out_file, key, tag):
    '''
    write content of function, using the key and tag
    i.e. RBC_ENGINE.Model_decl(RBC_ENGINE.Set_tag(...))
    '''
    logger.debug("calling write_func_body with (%s, %s, %s)"%(out_file, key, tag))
    
    # key => string to be replace with START
    key_str = ""
    if key == "this":
        key_str = "THIS_POINTER" 
    elif key == "return":
        key_str = "GET_RET"
    elif key[0:3].upper() == "ARG":
        key_str = "GET_ARG(%s)"%key[3:]
        pass
    else:
        raise KeyNotRecognised("%s is not a key"%key)
    logger.debug("key_str: %s"%key_str) 

    out_file.write("            DECLARE(RBC_SET_TAG(%s, \"%s\"));\n"%(key_str, tag))
    logger.debug("func body written")
    
def write_ret(out_file, ret_type):
    '''
    return statement for every function
    '''
    logger.debug("calling write_ret with params: (out_file=%s, ret_type=%s)"%(out_file, ret_type))
    to_write = ""
    if ret_type == '' or ret_type == 'void':
        to_write = ''
    elif ret_type in java_builtin:
        #out_file.write("return 0;\n")
        to_write = "            return 0;\n"
    elif ret_type == "boolean":
        #out_file.write("return false;\n")
        to_write = "            return false;\n"
    elif ret_type != "void":
        #out_file.write("return null;\n")
        to_write = "            return null;\n"
    logger.debug("to write: %s"%to_write)

    out_file.write(to_write)
    
def write_func_close(out_file):
    '''
    writing the closure of function
    '''
    out_file.write('        }\n')

def write_class_close(out_file):
    out_file.write("END_RULE\n")




'''
testing purpose
'''
if __name__ == "__main__":
    sys.path.insert(0, '../')
    import logger
    logger = logger.get_log()
    data = "<Point: void <init>(double,double)>"
    data2 = "<java.net.Socket: int getPort()>"
    data3 = "<java.net.Socket: void <init>()>"
    f = FuncParse(data) 
    
    line = "TAG|<Point: void <init>(double,double)>|this|sensitive"
    line2 = "TAG|<java.net.Socket: void connect(java.net.SocketAddress)>|this|tainted"
    parse_tag(line2)
