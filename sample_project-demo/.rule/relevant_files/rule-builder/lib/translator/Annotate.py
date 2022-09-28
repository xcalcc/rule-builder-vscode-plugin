#!/usr/bin/python3
"""
Annotate
annotating tool as extension of translation component
"""
import os

from logger import retrieve_log
from .AnnotationApi import ANNOTATION_API, \
    FuncParseError, AnnotationObject, FuncParse

LOGGER = retrieve_log()

JAVA_BUILTIN = ['byte', 'short', 'int', 'long', 'float', 'double', 'char', 'boolean', 'void', '']

class AnnotationError(Exception):
    """General Exception specialised for Annotatio

    Parent class of exception under API: Annotate
    """
    pass
class APINotFoundError(AnnotationError):
    """Exception for API Not Found

    Exception that is raised when parsing the string and the API is not listed in
    ANNOTATION_API
    """
    pass
class IncorrectAPIUsage(AnnotationError):
    """Exception for Incorrect API Use

    Exception that is raised when one of the annotation API is incorrectly used
    """
    pass

class Annotation(object):
    """Main Annotating object

    Holds the annotation entries from input file and also have fucnctionality of
    writing it out.

    Attributes:
        entries (list): list of annotationAPI objects
        is_interface (list): classes that are of interface type
        classe_entry (dict): <described below>
        src_files: path to generated source code (.h file)

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

    """
    def __init__(self):
        self.entries = []  # line that contains annotation
        self.is_interface = [] # store for classes that are interface
        self.classes_entry = {} #
        self.src_files = []

    def add_entry_raw(self, line):
        """add un-parsed string"""
        if not isinstance(line, str):
            raise TypeError("add_entry raw expects str type")
        parts = line.split('|')
        self.add_entry(parts[0], *parts[1:])

    def add_entry(self, action, *fields):
        """adding annotation entry

        action: TAG/ASSERT/etc., first entry
        fields: all fields for each
        """
        if action not in ANNOTATION_API:
            LOGGER.error("%s not recognised as annotation", action)
            raise APINotFoundError("%s not found"%action)

        api = ANNOTATION_API[action]
        try:
            entry = api(*fields)
        except FuncParseError: # func parsing exception
            raise FuncParseError()
        except: # any other problem dealt with incorrect api usage exception
            LOGGER.error("Something wrong when using %s", api.__name__)
            raise IncorrectAPIUsage()

        self.entries.append(entry)
        if entry.parser.is_interface:
            self.is_interface.append(entry.parser.cls_name)

        # categorize for each
        entry_cls = entry.parser.cls_name
        method_sig = entry.parser.method_sig
        if entry_cls in self.classes_entry:
            cls_func = self.classes_entry[entry_cls]
            LOGGER.debug("add entry under %s: %s", entry_cls, method_sig)
            if method_sig in cls_func:
                cls_func[method_sig].append(entry) # adding entry under classes_entries' signature
            else:
                cls_func[method_sig] = [entry]
        else:
            self.classes_entry[entry_cls] = {}
            temp = self.classes_entry[entry_cls]
            temp[method_sig] = [entry] # initialize new entry
        LOGGER.debug('entry: %s', self.classes_entry)

    def get_entry(self):
        """getter for classes_entry"""
        return self.classes_entry

    @staticmethod
    def create_file(cls_name, out_dir='.'):
        """write file path"""
        LOGGER.info("Create path: %s", os.path.join(out_dir, cls_name.replace('.', os.sep)))

        file_path = os.path.join(out_dir, cls_name.replace('.', os.sep)) # structure package
        file_path += '.h' # set as .h file first

        dir_name = os.path.dirname(file_path)
        if dir_name != "" and not os.path.exists(dir_name):
            os.makedirs(dir_name)
        out_file = open(file_path, 'w') # create if not exist, clear if exist
        out_file.close()
        return file_path

    def write_header(self, out_file, cls_name, dump_import):
        """Writing header of file (packages, imports, class/interface"""
        LOGGER.debug("Writing header of file to %s", out_file)
        index = cls_name.rfind('.')
        if index != -1:
            package = cls_name[:index]
            cls_name = cls_name[index+1:]
            out_file.write("PACKAGE(%s)\n"%package)
        if dump_import:
            out_file.write("IMPORT1\n")
        if cls_name in self.is_interface:
            out_file.write("INTERFACE(%s)\n"%cls_name)
        else:
            out_file.write("CLASS(%s)\n"%cls_name)

    @staticmethod
    def get_dep_class(sig, dep_set):
        """getting dependency files from sig"""
        ret_type = sig.ret_type.replace('[]', '') # remove array possibility
        args = sig.args

        if ret_type not in JAVA_BUILTIN: # check any dependency in return type
            dep_set.add(ret_type)
        for arg in args:
            arg = arg.replace('[]', '')
            if arg not in JAVA_BUILTIN:
                dep_set.add(arg) # check dependencies in arguments
        return dep_set

    @staticmethod
    def write_func_signature(out_file, sig):
        """function signature: public int add(...)"""
        fname = sig.met_name
        cls_name = sig.cls_name
        ret_type = sig.ret_type
        pkg = sig.pkg_name
        arguments = "" # holding string

        if fname.find("<init>") != -1: # if it's not init
            names = cls_name.split('.')
            #fname = names[len(names)-1]
            fname = names[-1]
            ret_type = ""

        if ret_type.startswith(pkg):
            ret_type.replace(pkg+'.', '') # remove package name if same

        i = 1
        args = sig.args
        for arg in args:
            if arg in ("void", ""):
                arguments += arg
            else:
                if arg.startswith(pkg):
                    arg = arg.replace(pkg+'.', '') # remove pkgname if same
                arguments += arg + " arg"+ str(i) + ","

        arguments = arguments.rstrip(', ')
        if sig.is_interface:
            modifiers = "default"
        else:
            modifiers = "public"
        fname = fname + '(' + arguments + ')'
        out_file.write('        FUNC_SIG(%s,%s,%s)\n'%(modifiers, ret_type, fname))

    @staticmethod
    def write_func_body(out_file, entry):
        """put for every annotation entry"""
        LOGGER.debug('write entry into %s', out_file.name)
        if not isinstance(entry, AnnotationObject): # error if not part of API
            raise APINotFoundError()
        parsed = entry.translate()
        out_file.write("            %s;\n"%parsed)

    @staticmethod
    def write_ret(out_file, ret_type):
        """return statement for every func signature"""
        LOGGER.debug("writing return params: %s", ret_type)
        to_write = ""
        if ret_type == "" or ret_type == "void":
            to_write = "" # leave empty
        elif ret_type in JAVA_BUILTIN:
            to_write = "            return 0;\n"
        elif ret_type == "boolean":
            to_write = "            return false;\n"
        elif ret_type != "void":
            to_write = "           return null;\n"
        LOGGER.debug("to write: %s", to_write)

        out_file.write(to_write)

    @staticmethod
    def write_func_close(out_file):
        """function closure for each func"""
        out_file.write('        }\n')

    @staticmethod
    def write_class_close(out_file):
        """class end"""
        out_file.write("END_RULE\n")

    def create_dep_files(self, dep_set, rb_loc, out_dir='.'):
        """create file for dependency file if they are not part of
        classes that are tagged"""

        LOGGER.debug("create dep files with %s", dep_set)
        for dep in dep_set:
            if dep not in self.classes_entry:
                file_path = Annotation.create_file(dep, out_dir)
                self.src_files.append(file_path)

                template_h = open(os.path.join(rb_loc, 'lib/translator/template.h'))
                out_file = open(file_path, 'w')

                read = template_h.readlines()
                for ref in read:
                    out_file.write(ref) # copy header file
                template_h.close()

                self.write_header(out_file, dep, False)
                Annotation.write_class_close(out_file)
                out_file.close()

    def generate(self, rb_loc, out_dir='.'):
        """main file generator for content of each file
        also return path of generated file(s)"""
        dep_set = set()  # unique collection of dependencies
        for cls in self.classes_entry:
            fpath = Annotation.create_file(cls, out_dir)
            self.src_files.append(fpath)

            out_file = open(fpath, 'w')
            template_h = open(
                os.path.join(rb_loc, 'lib/translator/template.h'), 'r'
            )

            read = template_h.readlines()
            for ref in read:
                out_file.write(ref)  # copying template.h header to out_file
            template_h.close()

            self.write_header(out_file, cls, True) # write header of file

            funcs = self.classes_entry[cls]
            for func in funcs: # for every function in a certain class
                sig = '<'+cls+': '+func+'>'
                parse_sig = FuncParse(sig) # get information of function in detail
                Annotation.get_dep_class(parse_sig, dep_set)
                Annotation.write_func_signature(out_file, parse_sig)

                entries = funcs[func] # annotation entries

                for entry in entries: # function body and return type write out
                    Annotation.write_func_body(
                        out_file, entry
                    )
                Annotation.write_ret(out_file, parse_sig.ret_type)
                Annotation.write_func_close(out_file)
            Annotation.write_class_close(out_file)

            LOGGER.debug("Dependencies: %s", dep_set)
            self.create_dep_files(dep_set, rb_loc, out_dir)
            out_file.close()
        return self.src_files
