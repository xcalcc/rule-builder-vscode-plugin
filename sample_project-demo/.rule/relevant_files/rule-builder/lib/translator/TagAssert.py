#!/usr/bin/python3

"""
API for Tagging and Asserting,
useful to tag classes or functions or arguments
"""

import sys
import re
import os 
import logger
from .ConditionParse import ConditionParse

logger = logger.retrieve_log()

class ActionNotRecognised(Exception):
    pass

class FuncParse:
    '''
    get information of class
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
        self.method_sig = method_sig
        logger.debug("method_sig = %s"%method_sig)
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


class Tag:
    def __init__(self, function, key, tag):
        logger.debug("Creating tag")
        self.parser = FuncParse(function)
        self.key = key
        self.tag = tag
    
    def __repr__(self):
        return "(Tag, %s, %s, %s)"%(self.parser.met_name, self.key, self. tag)

class Assert:
    def __init__(self, function, condition, error):
        logger.debug("Creating assert")
        self.parser = FuncParse(function)
        #self.condition = ConditionParse.parse(condition)
        self.condition = condition
        self.error = error
    
    def __repr__(self):
        return "(Assert, %s, %s, %s)"%(self.parser.met_name, self.condition, self.error)

class TagAssert:
    '''
    parsing strings with pattern of either:
    TAG|<FUNCTION_NAME>|KEY|TAG_STR
    ASSERT|<FUNCTION_NAME>|CONDITION|ERR
    '''
    entries = []
    is_interface = []
    classes_entry = {} # record for each class, what are the entries
    java_builtin = ['byte', 'short', 'int', 'long', 'float', 'double', 'char', 'boolean', 'void', '']
    src_files = []

    '''
    classes_entry = {
        class1: {
            func1(): [...]
            func2(): [...]
        }
        class2: {
            func3(): [...]
            func4(): [...]
        }

    }
    '''
    @staticmethod
    def add_entry_raw(line):
        '''
        adding an entry but based from a string
        '''
        if not isinstance(line, str):
            raise TypeError("expected a str type")
        parts = line.split('|') 
        TagAssert.add_entry(parts[0], *parts[1:])
        

    @staticmethod
    def add_entry(action, *fields):
        '''
        action: TAG/ASSERT
        fields: all fields respective of each
        '''
        if action == "TAG":
            logger.debug("Tag detected")
            entry = Tag(*fields)
        elif action == "ASSERT":
            logger.debug("Assert detected")
            entry = Assert(*fields)
        else:
            logger.error("Action not recognised")
            raise ActionNotRecognised()
        TagAssert.entries.append(entry)            
        if entry.parser.is_interface:
            TagAssert.is_interface.append(entry.parser.cls_name)

        entry_cls = entry.parser.cls_name
        method_sig = entry.parser.method_sig  
        if entry_cls in TagAssert.classes_entry:
            cls_func = TagAssert.classes_entry[entry_cls]
            logger.debug("adding %s under %s: %s"%(entry, entry_cls, method_sig))
            if method_sig in cls_func:
                cls_func[method_sig].append(entry)
            else:
                cls_func[method_sig] = [entry]
        else:
            TagAssert.classes_entry[entry_cls] = {}
            temp = TagAssert.classes_entry[entry_cls]
            temp[method_sig] = [entry]
        logger.debug(TagAssert.classes_entry)
        
    @classmethod
    def create_file(cls, class_name, out_dir='.'):
        logger.info("Create path for %s"%os.path.join(out_dir,class_name))
        file_path = os.path.join(out_dir, class_name.replace('.', os.sep))
        file_path += '.h'  # i.e. java/io/PrinStream.h
        logger.debug("file is %s"%file_path)
        
        dir_name = os.path.dirname(file_path)
        if dir_name != "" and not os.path.exists(dir_name):
            os.makedirs(dir_name) # create if not exist
        out_file = open(file_path, 'w') # to ensure creation
        out_file.close()
        return file_path

    @classmethod
    def write_header(cls, out_file, cls_name, dump_import):
        '''
        Write header of file
        '''
        logger.debug("write header file of %s"%out_file)
        index = cls_name.rfind('.')
        if index != -1:
            package = cls_name[:index]
            cls_name = cls_name[index+1:]
            out_file.write("PACKAGE(%s)\n"%package)   
        if dump_import:
            out_file.write("IMPORT1\n")
        if cls_name in cls.is_interface:
            out_file.write("INTERFACE(%s)\n"%cls_name)
        else:
            out_file.write("CLASS(%s)\n"%cls_name)

    @classmethod
    def get_dep_class(cls, sig, dep_set):
        '''
        get all dependency files from sig
        ''' 
        ret_type = sig.ret_type.replace('[]', '')
        args = sig.args 
        
        # check all arguments and get the dependency
        # check to see if it is in java_builtin
        if ret_type not in cls.java_builtin:
            dep_set.add(ret_type)
        for arg in args:
            arg = arg.replace('[]', '')
            if arg not in cls.java_builtin:
                dep_set.add(arg)
        return dep_set

    @classmethod
    def write_func_signature(cls, out_file, sig):
        '''
        func_sig: public int add(...)
        ''' 
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

    @classmethod
    def write_func_body(cls, out_file, entry):
        '''
        write content after func signature
        uses condparse
        '''
        logger.debug("writing %s into %s"%(entry, out_file.name)) 
        
        if isinstance(entry, Tag):
            raw_str = "tag(%s, \"%s\")"%(entry.key, entry.tag)
        elif isinstance(entry, Assert):
            raw_str =  'assert(%s,"%s")'%(entry.condition, entry.error)
        else:
            raise APIError()
        logger.debug('raw string %s'%raw_str)
        parsed = ConditionParse.parse(raw_str)
        logger.debug(parsed.translate())
        out_file.write("            %s;\n"%parsed.translate())

    @classmethod
    def write_ret(cls, out_file, ret_type):
        '''
        return statement for every func body
        '''
        logger.debug("write_ret params: %s"%ret_type)
        to_write = ""
        if ret_type == '' or ret_type == 'void':
            to_write = ''
        elif ret_type in cls.java_builtin:
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

    @classmethod
    def write_func_close(cls, out_file):
        '''
        writing the closure of function
        '''
        out_file.write('        }\n')

    @classmethod
    def write_class_close(cls, out_file):
        out_file.write("END_RULE\n")

    @classmethod
    def create_dep_files(cls, dep_set, rb_loc, out_dir='.'):
        '''
        create file for dependency file if they are not part of 
        classes that are tagged
        '''
        logger.debug("creating dep files with %s"%dep_set)
        for dep in dep_set:
            if dep not in cls.classes_entry:
                file_path = cls.create_file(dep, out_dir)
                cls.src_files.append(file_path)
                template_h = open(os.path.join(rb_loc, 'lib/translator/template.h'))
                out_file = open(file_path, 'w')
                read = template_h.readlines()
                for r in read:
                    out_file.write(r)
                template_h.close()

                cls.write_header(out_file, dep, False)
                cls.write_class_close(out_file)

    @classmethod
    def generate(cls, rb_loc, out_dir='.'):
        '''
        generating files and its content
        '''
        dep_set = set()
        for c in cls.classes_entry:
            fpath = cls.create_file(c, out_dir)
            cls.src_files.append(fpath)
            
            out_file = open(fpath, 'w')
            # copy header of template.h 
            template_h = open(os.path.join(rb_loc, 'lib/translator/template.h'), 'r')
            read = template_h.readlines()
            for r in read:
                out_file.write(r)

            # write header of file
            cls.write_header(out_file, c, True) 

            func = cls.classes_entry[c]
            for f in func:
                sig = '<'+c+': '+f+'>'
                parse_sig = FuncParse(sig)
                cls.get_dep_class(parse_sig, dep_set) # get dependencies
                cls.write_func_signature(out_file, parse_sig)                 
                entries = func[f]
                for entry in entries:
                    cls.write_func_body(out_file, entry)
                    cls.write_ret(out_file, parse_sig.ret_type)
                cls.write_func_close(out_file)
            cls.write_class_close(out_file)
            logger.debug("Dependencies: %s"%dep_set)
            
            cls.create_dep_files(dep_set, rb_loc, out_dir)
            template_h.close()
            out_file.close()
