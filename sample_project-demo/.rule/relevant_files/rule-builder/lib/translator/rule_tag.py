#!/usr/bin/python3

"""
Tagging API, 
useful to tag classes or functions, or arguments
"""

import sys
import re
import os
import logger
logger = logger.retrieve_log()
    
class FuncParse:
    '''
    class to store function attributes like ret_type, signature, method name, arguments
    '''
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

class KeyNotRecognised(Exception):
    def __init__(self, msg=""):
        super().__init__(msg)

class Tag():
    def __init__(self, function, key, tag):
        self.parser = FuncParse(function) 
        self.key = key
        self.tag = tag


class Tagging:
    #TODO: get the dependencies and create files for them as well 

    tags = [] # storage
    is_interface = [] # which classes are an interface
    classes_tag = {} # contain classes and the tags associated to it 
    java_builtin = ['byte', 'short', 'int', 'long', 'float', 'double', 'char', 'boolean', 'void', '']

    def __init__(self):
        pass
    
    @staticmethod
    def add_tags_entry(field, function, key, tag ):
        '''
        adding into list of tags
        '''
        logger.debug(
            """adding a tag entry: 
            field: %s\nfunction:%s\nkey:%s\ntag:%s  
            """%(field, function, key, tag)
        ) 
        t_entry = Tag(function, key, tag)
        logger.debug("entry class name: %s"%t_entry.parser.cls_name)
        Tagging.tags.append(t_entry)
        
        # append to tags and classes_tag 
        entry_cls = t_entry.parser.cls_name
        if entry_cls in Tagging.classes_tag:
            Tagging.classes_tag[entry_cls].append(t_entry)
        else:
            Tagging.classes_tag[entry_cls] = [t_entry]  
        if t_entry.parser.is_interface:
            is_interface.append(entry_cls) 

    @staticmethod
    def show_tags():
        logger.info("%s"%Tagging.classes_tag) 

    @staticmethod
    def write_header(out_file, cls_name, dump_import):
        logger.debug("write_header() with params: (%s, %s, %s"%(out_file, cls_name, dump_import))
        index = cls_name.rfind('.')
        if index != -1:
            package = cls_name[:index]
            cls_name = cls_name[index+1:]
            out_file.write("PACKAGE(%s)\n"%package)   
        if dump_import:
            out_file.write("IMPORT1\n")
        if cls_name in Tagging.is_interface:
            out_file.write("INTERFACE(%s)\n"%cls_name)
        else:
            out_file.write("CLASS(%s)\n"%cls_name)

    @staticmethod
    def create_file(cls_name):
        logger.info("Creating path to %s"%cls_name)
        file_path = cls_name.replace('.', os.sep)
        file_path += '.h'
        logger.debug("file is %s"%(file_path))

        dir_name = os.path.dirname(file_path)
        if dir_name!="" and not os.path.exists(dir_name):
            os.makedirs(dir_name) # create temp directories to path
        out_file = open(file_path, 'w')

        logger.info("%s created"%file_path)
        out_file.close()
        return file_path
    
    @staticmethod
    def get_dep_class(sig, dep_set):
        '''
        getting all dependency classes from sig
        '''
        logger.debug("Getting dependencies from the %s"%sig)
        ret_type = sig.ret_type.replace('[]', '')
        args = sig.args
        #dep_set = set()

        if ret_type not in Tagging.java_builtin:
            dep_set.add(ret_type)
        for arg in args:
            arg = arg.replace('[]' ,'')
            if arg not in Tagging.java_builtin:
                dep_set.add(arg)
        return dep_set

    def write_func_signature(out_file, sig):
        '''
        function signature: public int add(...)  
        '''
        logger.debug("""calling func_signature with
        (%s, %s)"""%(out_file, sig))

        fname = sig.met_name
        cls_name = sig.cls_name
        ret_type = sig.ret_type
        arguments = ""
        
        if fname.find("<init>") != -1:
            logger.debug("init detect")
            names = cls_name.split('.')
            fname = names[len(names)-1]
            ret_type = ""
            
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
 
    def create_dep_files(dep_set, rb_loc):
        '''
        create file for dependency file if they are not part of 
        classes that are tagged
        '''
        logger.debug("create_dep_files with %s"%dep_set)
        for cls in dep_set:
            if cls not in Tagging.classes_tag:
                file_path = Tagging.create_file(cls)
                template_h = open(os.path.join(rb_loc,'lib/translator/template.h' ), 'r')
                out_file = open(file_path, 'w')
                read = template_h.readlines()
                for r in read:
                    out_file.write(r)
                template_h.close()

                Tagging.write_header(out_file, cls, False)                 
                Tagging.write_class_close(out_file)
     
    @staticmethod
    def generate(rb_loc):
        '''
        from the classes_tag, create files as well as the entry for each
        '''
        dep_set = set()
        for cls in Tagging.classes_tag:
            fpath = Tagging.create_file(cls)
            out_file = open(fpath, 'w')
            template_h = open(os.path.join(rb_loc,'lib/translator/template.h' ), 'r')
            read = template_h.readlines()
            for r in read:
                out_file.write(r)
            template_h.close()
            Tagging.write_header(out_file, cls, True)
            
            tags =  Tagging.classes_tag[cls]
            logger.debug("Some tags are %s"%tags)
            for tag in tags:
                Tagging.get_dep_class(tag.parser, dep_set)
                Tagging.write_func_signature(out_file, tag.parser)        
                Tagging.write_func_body(out_file, tag.key, tag.tag)
                Tagging.write_ret(out_file, tag.parser.ret_type)
                Tagging.write_func_close(out_file)
            Tagging.write_class_close(out_file)
        logger.debug("Dependencies: %s"%dep_set)
        Tagging.create_dep_files(dep_set, rb_loc)
