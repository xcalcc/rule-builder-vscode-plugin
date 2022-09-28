#!/usr/bin/python3

# =============================================
# Script to Generate A Source Based on rule file
# =============================================
from Function import Function
import sys
import re
import os
import subprocess
from FileGenerate import FileGenerate
import logger

logger = logger.retrieve_log()
arg = sys.argv

logger.info("Compilation part 1, generating sources from fsm")
if len(arg) < 2:
    print("Usage is {} <rulename>".format(arg[0]))
    exit(1)

filename = os.path.basename(arg[1])
filename = filename.split('.')[0]
print("Scanning for rule {}   ...".format(filename))

pattern="_ZN"
functions=[] # store the raw 
filtered_functions=[] # contain all the c++filtered

file = open(arg[1], "r")
for line in file:
    if re.search(pattern, line):
        functions.append(line.strip())
# res = os.popen('c++filt _ZN10GSemaphore6UnlockEv').read() # get the result of the c++filt
def cppfilt(s):
    return os.popen('c++filt '+ s).read()
# For each, extract only the _Zn part
for i in functions:
    filtered_functions.append(cppfilt(i.split('"')[3]).strip().replace('*',''))

filtered_functions = list(set(filtered_functions)) # create unique list of functions

# Attach Functions to Classes
package_map_function = {}

for i in filtered_functions:
    f = Function(i)
    print("====")
    print('fullname = ', f.fullname)
    print('return value = ', f.retvalue)
    print('return value package = ', f.retvaluepackage)
    print('class name = ', f.clsname)
    print('package name = ', f.pkgname)
    print('function signature = ', f.fsignature)
    print('function parameter = ', f.params)
    print('Import list = ', f.importlist)
    print('Parameter String = ', f.paramstr)
    
    clname = f.clsname
    if clname in package_map_function:
        package_map_function[clname].append(f)
    else:
        package_map_function[clname] = [f]

print(package_map_function)

# Create files for each class
#generated = FileGenerate("Email", package_map_function["Email"], "cwe295")
#generated.format()
#generated.write()
FileGenerate.clean()
for i in package_map_function:
    print(i)
    generated = FileGenerate(i, package_map_function[i], filename)
    generated.write() 
