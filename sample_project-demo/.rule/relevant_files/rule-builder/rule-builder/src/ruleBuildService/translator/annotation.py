import os
import re
from .annotation_api import ANNOTATION_API, \
    FuncParseError, AnnotationObject, FuncParse

from . import template_h_path
#from ..logger import Logger
from ruleBuildService.config import ErrorNo
from common.XcalException import XcalException
from common.XcalLogger import XcalLogger

#_logger = Logger.retrieve_log() # pylint: disable=invalid-name

JAVA_BUILTIN = ['byte', 'short', 'int', 'long', 'float', 'double', 'char', 'void', '', 'boolean']
C_BUILTIN = JAVA_BUILTIN[:-1] + ['bool', 'signed char', 'unsigned char', 
            'short', 'short int', 'signed short', 'unsigned short', 'signed short int', 'unsigned short int', 
            'signed', 'signed int', 'unsigned int', 
            'unsigned long', 'unsigned long int', 'signed long', 'signed long int', 'long int',
            'long long', 'long long int', 'signed long long', 'signed long long int', 'unsigned long long', 
            'unsigned long long int', 'long double', 'size_t', 'ssize_t', 'FILE', 'fpos_t'] 
            # use bool instead of boolean in JAVA. size_t, FILE, fpos_t defined in stdio.h

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
        self.logger = XcalLogger("annotation", "__init__")

    def add_entry_raw(self, line):
        """add un-parsed string

        raw string un-split yet, added to the list of entries

        Args:
            line (FuncParse): complete line to be parsed
        """
        parts = line.split('|')
        self.add_entry(parts[0], *parts[1:])

    def _check_entry_exist(self, entry_list, entry):
        """annull duplicate entries

        checking if the translation of entry matches with
        every entry in the list

        Args:
            entry_list (list): list of entries
            entry (AnnotationObject): the entry type
        Returns:
            bool: True if exist, False if not
        """
        for ent in entry_list:
            if ent.translate() == entry.translate():
                return True
        return False


    def add_entry(self, action, *fields):
        """adding annotation entry

        Args:
            action (str): TAG/ASSERT/etc., first entry
            fields (str): string containing the fields
        """
        if action not in ANNOTATION_API:
            raise XcalException("annotation", "add_entry", "%s not found" % action,
                                err_code=ErrorNo.E_API_NOT_EXIST)
        api = ANNOTATION_API[action]

        try:
            entry = api(*fields)
        except XcalException as e: # func parsing exception
            raise e
        except: # any other problem dealt with incorrect api usage exception
            raise XcalException("annotation", "add_entry", "Something went wrong when adding %s" % fields,
                                err_code=ErrorNo.E_INCORRECT_API_CALL)

        self.entries.append(entry)
        if entry.parser.is_interface:
            self.is_interface.append(entry.parser.cls_name)

        # categorize for each
        entry_cls = entry.parser.cls_name
        method_sig = entry.parser.method_sig
        if entry_cls in self.classes_entry:
            cls_func = self.classes_entry[entry_cls]
            self.logger.debug("add_entry", "add_entry under %s: %s" % (entry_cls, method_sig))
            if method_sig in cls_func:
                if not self._check_entry_exist(cls_func[method_sig], entry):
                    cls_func[method_sig].append(entry) # adding entry
            else:
                cls_func[method_sig] = [entry]
        else:
            self.classes_entry[entry_cls] = {}
            temp = self.classes_entry[entry_cls]
            temp[method_sig] = [entry] # initialize new entry

    def get_entry(self):
        """getter for classes_entry"""
        return self.classes_entry

    @staticmethod
    def create_file(cls_name, out_dir='.'):
        """initialze file

        initialization of file being generated into expected directory.

        Args:
            out_dir (str): output directory, by default is current directory
        """

        with XcalLogger("annotation", "create_file") as log:
            log.debug("create_file", "arguments: %s %s" % (cls_name, out_dir))
        file_path = os.path.join(out_dir, cls_name.replace('.', os.sep)) # structure package
        file_path += '.h' # set as .h file first

        dir_name = os.path.dirname(file_path)
        if dir_name != "" and not os.path.exists(dir_name):
            os.makedirs(dir_name)
        out_file = open(file_path, 'w') # create if not exist, clear if exist
        out_file.close()
        return file_path

    def write_header(self, out_file, cls_name, dump_import):
        """writing header ingo file

        writing information from packages, imports, whether class/interface
        into the header of file

        Args:
            out_file (str): file to write out to
            cls_name (str): class name
            dump_import (str):  flag whether or not we want to include import headers
        """
        self.logger.debug("write_header", "Writing header of file %s" % out_file)
        index = cls_name.rfind('.')
        if index != -1:
            package = cls_name[:index]
            cls_name = cls_name[index+1:]
            out_file.write("PACKAGE(%s)\n"%package)
        if dump_import:
            out_file.write("IMPORT1\n")
            out_file.write("IMPORT2\n")
            out_file.write("IFDEF1\nIFDEF2\nIFDEF3\n")
        if cls_name in self.is_interface:
            out_file.write("INTERFACE(%s)\n"%cls_name)
        else:
            out_file.write("CLASS(%s)\n"%cls_name)

    @staticmethod
    def get_dep_class(sig, dep_set):
        """extract dependency files

        from the function signature, extract the dependency files required
        for this function. Store it in the shared dependency set. Dependency if
        it is not part of JAVA_BUILTIN

        Args:
            sig (FuncParse): function signature in parsed object
            dep_set (set): shared dependency set (avoiding duplicate)
        Returns:
            set: set of depencies needed from this function
        """
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
    def find_fake_types(out_file, sig):
        """ writing typedef struct for undefined types (for c)
        
            Goes through function arguments and outputs set of types that are not 
            built-in types in C (not listed in C_BUILTIN). 
            This makes sure that undefined types are not repeatedly defined.

            Args:
            out_file (str): path to output file
            sig (FuncParse): parsed object format to extract info

            Output:
            undefined (str set): set of types that need to be defined
        """
        ret_type = sig.ret_type.strip()
        args = sig.args

        undefined = set()
        for arg in args:
            if len(arg) == 0: # no arguments
                pass
            # if encounter an undefined arg type add to undefined set
            arg_name = arg.strip()
            if arg_name not in C_BUILTIN:
                # check if arg is a const or pointer of builtin type
                const_ptr_matcher = re.search(r'(const )?(\S*)( \*)?', arg_name)
                if const_ptr_matcher and const_ptr_matcher.group(2) not in C_BUILTIN:
                    undefined.add(const_ptr_matcher.group(2))

        # if return type is not a builtin type
        if ret_type not in C_BUILTIN:
            const_ptr_matcher = re.search(r'(const )?(\S*)( \*)?', ret_type.strip())
            if const_ptr_matcher and const_ptr_matcher.group(2) not in C_BUILTIN:
                undefined.add(const_ptr_matcher.group(2))

        return undefined

    @staticmethod
    def write_func_signature_c(out_file, sig):
        """writing function signature (for c)

        same logic as write_func_signature, but specific case for
        C target language rule files
        """
        fname = sig.met_name
        cls_name = sig.cls_name
        ret_type = sig.ret_type
        args = sig.args
        arg_str = ""

        # construct argument str
        num = 1
        for arg in args:
            if arg in ("void", ""):
                pass
            elif len(arg) != 0 and arg[-1] == "*": # different formatting for pointer type
                arg_str += "%sarg%s, " % (arg, num)
            else:
                arg_str += "%s arg%s, " % (arg, num)
            num += 1

        arg_str = arg_str.rstrip(", ") # remove extra ,_
        if ret_type[-1] == "*": # return type is pointer, cannot have space between * and fname
            func_str = "*%s(%s)" % (fname, arg_str)
            ret_type = ret_type[:-1].strip()
            out_file.write('        FUNC_SIG(%s,%s,%s)\n' % ("", ret_type, func_str))
        else:
            func_str = "%s(%s)" % (fname, arg_str)
            out_file.write('        FUNC_SIG(%s,%s,%s)\n' % ("", ret_type, func_str))

    @staticmethod
    def write_func_signature(out_file, sig):
        """writing function signature (for java)

        get information from the signature object and write out
        the function signature in the form of public int add(....)

        Args:
            out_file (str): path to output file
            sig (FuncParse): parsed object format to extract info
        """
        fname = sig.met_name
        cls_name = sig.cls_name
        ret_type = sig.ret_type
        pkg = sig.pkg_name
        arguments = "" # holding string


        if fname.find("<init>") != -1: # if it's not init
            names = cls_name.split('.')
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
                if arg.startswith(pkg) and pkg: # it contains package
                    arg = arg.replace(pkg+'.', '') # remove pkgname if same
                arguments += arg + " arg"+ str(i) + ","
            i += 1

        arguments = arguments.rstrip(', ')
        if sig.is_interface:
            modifiers = "default"
        else:
            modifiers = "public"
        fname = fname + '(' + arguments + ')'
        out_file.write('        FUNC_SIG(%s,%s,%s)\n'%(modifiers, ret_type, fname))

    @staticmethod
    def write_func_body(out_file, entry):
        """translation annotation

        called for every annotation entry contained into the outfile.

        Args:
            out_file (str): path to output file
            entry (AnnotationAPI): API object to be translated
        """
        if not isinstance(entry, AnnotationObject): # error if not part of API
            raise APINotFoundError()
        parsed = entry.translate()
        out_file.write("            %s;\n"%parsed)

    @staticmethod
    def write_ret(out_file, ret_type, lang):
        """writing out return statement

        depending on the ret_type expected, print out (or not)
        the return statement at the end of the function

        Args:
            out_file (str): path to output file
            ret_type (str); return type expected from function signature
        """
        to_write = ""
        if ret_type == "" or ret_type == "void":
            to_write = "" # leave empty
        elif ret_type == "boolean":
            to_write = "            return false;\n"
        elif ret_type in JAVA_BUILTIN:
            to_write = "            return 0;\n"
        elif ret_type in C_BUILTIN:
            to_write = "            return 0;\n"
        elif ret_type != "void":
            if lang == "java":
                to_write = "           return null;\n"
            else:
                if ret_type.strip()[-1] == "*":
                    to_write = "            return NULL;\n"
                else: # unknown type that is not pointer, need to return value of its type
                    to_write = "            %s var;\n            return var;\n" %ret_type


        out_file.write(to_write)

    @staticmethod
    def write_func_close(out_file):
        """write function closure for each func"""
        out_file.write('        }\n')

    @staticmethod
    def write_class_close(out_file):
        """write class end ('}' character)"""
        out_file.write("IFDEF1\n")
        out_file.write("END_RULE\n")
        out_file.write("IFDEF3\n")

    def create_dep_files(self, dep_set, out_dir='.'):
        """creating dependency files

        from dependency set, create each of them if it hasn't been created before. If
        it is purely dependency, no need to include imports.

        Args:
            dep_set (set): dependency set shared
            out_dir (str): output directory
        """
        # _logger.debug("create dep files with %s", dep_set)
        self.logger.debug("create_dep_files", "create dependency files with %s" % dep_set)
        for dep in dep_set:
            if dep not in self.classes_entry:
                file_path = Annotation.create_file(dep, out_dir)
                self.src_files.append(file_path)

                template_h = open(template_h_path)
                out_file = open(file_path, 'w')

                read = template_h.readlines()
                for ref in read:
                    out_file.write(ref) # copy header file
                template_h.close()

                self.write_header(out_file, dep, False)
                Annotation.write_class_close(out_file)
                out_file.close()

    def generate(self, lang, out_dir='.'):
        """generating from currently stored entries

        main file generator for content of each file, and returning
        a list of path to generated files

        Args:
            lang (str): target language
            out_dir (str): output directory where all files will be generated
        Returns:
            list: containing path to all generated files
        """
        # _logger.debug("target language: %s", lang)
        self.logger.debug("generate", "target language is %s" % lang)

        if lang not in ['java', 'c', 'c++']:
            raise XcalException("annotation", "generate", "target language : %s error" % lang,
                                err_code=ErrorNo.E_LANGUAGE_NOT_SUPPORTED)

        dep_set = set()  # unique collection of dependencies
        for cls in self.classes_entry:
            fpath = Annotation.create_file(cls, out_dir)
            self.src_files.append(fpath)

            out_file = open(fpath, 'w')

            template_h = open(template_h_path)

            read = template_h.readlines()
            for ref in read:
                out_file.write(ref)  # copying template.h header to out_file
            template_h.close()

            self.write_header(out_file, cls, True) # write header of file

            funcs = self.classes_entry[cls]
            if lang == 'c' or lang == 'c++': # construct typedef structs to define unknown types in C
                undefined_types = set() # use set to ensure dont repeatedly define types
                for func in funcs: # for every function in a certain class
                    sig = '<'+cls+': '+func+'>'
                    parse_sig = FuncParse(sig, lang) # get information of function in detail
                    undefined_types = undefined_types|Annotation.find_fake_types(out_file, parse_sig)
                for type in undefined_types: 
                    out_file.write('        FAKE_TYPE(%s)\n' % type)

            for func in funcs: # for every function in a certain class
                sig = '<'+cls+': '+func+'>'
                parse_sig = FuncParse(sig, lang) # get information of function in detail
                if lang == 'java':
                    Annotation.get_dep_class(parse_sig, dep_set)
                    Annotation.write_func_signature(out_file, parse_sig)
                else:
                    Annotation.write_func_signature_c(out_file, parse_sig)

                entries = funcs[func] # annotation entries

                for entry in entries: # function body and return type write out
                    Annotation.write_func_body(
                        out_file, entry
                    )
                Annotation.write_ret(out_file, parse_sig.ret_type, lang)
                Annotation.write_func_close(out_file)
            Annotation.write_class_close(out_file)

            # _logger.debug("Dependencies: %s", dep_set)
            self.create_dep_files(dep_set, out_dir)
            out_file.close()
        return self.src_files