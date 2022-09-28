#!/usr/bin/python3

# ===================================================
# FileGenerate
# Class To Generate the file
# ===================================================

from .Function import Function
import sys
import os
import shutil
import logger

logger = logger.retrieve_log()

class FileGenerate:
    # Attributes
    # ----------
    # pk_fn: mapping of package name to list of function names
    # rule: what rule this is (i.e. cwe295)

    def __init__(self, classname, functions, error_name):
        self.classname = classname
        logger.debug("Generating for %s.java"%(classname))
        self.functions = functions
        self.error_name = error_name
        self.getImports()

    def format(self):
        # previewing how the file would look like
        print("-------------------{}.java-------------------".format(self.classname))
        # Header (package and imports)
        print("package {}".format(self.functions[0].pkgname+";"))
        for i in self.imports:
            print("import {};".format(i))
        print("import io.xc5.RBC_ENGINE;")
        print('\n')
        # head (class declaration)
        print("public final class {} {{".format(self.classname))
        
        # for each function
        for f in self.functions:
            print("\tpublic {} {}({}) {{ ".format(
                f.retvalue, f.fsignature, f.paramstr
            ))
            print("\t\tRBC_ENGINE.Model_decl(RBC_ENGINE.Fsm_use(\"{}\"));".format(self.error_name))
            if f.retvalue=="" or f.retvalue=="void" :
                print("")
            else:
                print("\t\treturn null;")
            print("\t}")
        print("}") 
        
    def getImports(self):
        # get import list from every function
        self.imports = []
        for f in self.functions:
           self.imports += f.importlist
    
    @staticmethod
    def clean():
        outputdir=os.getcwd() +'/output'
        if os.path.exists(outputdir):
            shutil.rmtree(outputdir)
        os.mkdir('output')
 
    def write(self):
        # writing content into a file (given filename)
        fname = self.classname+".java.rule"
        # check if output directory exist
        outputdir = os.getcwd() + '/output'
 
        
        # create new file within the directory
        with open(outputdir + '/' + fname, 'w') as fi:
            fi.write("package {}\n".format(self.functions[0].pkgname+";"))
            for i in self.imports:
                fi.write("import {};\n".format(i))
            fi.write("import io.xc5.RBC_ENGINE;\n")
            fi.write('\n')
            fi.write("public final class {} {{\n".format(self.classname))
        
            # for each function
            for f in self.functions:
                fi.write("\tpublic {} {}({}) {{\n ".format(
                    f.retvalue, f.fsignature, f.paramstr
                ))
                fi.write("\t\tRBC_ENGINE.Model_decl(RBC_ENGINE.Fsm_use(\"{}\"));\n".format(self.error_name))
                if f.retvalue=="" or f.retvalue=="void" :
                    fi.write("\n")
                else:
                    fi.write("\t\treturn null;\n")
                fi.write("\t}\n")
            fi.write("}\n") 

 
