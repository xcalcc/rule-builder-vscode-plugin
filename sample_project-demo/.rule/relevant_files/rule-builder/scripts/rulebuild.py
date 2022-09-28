#!/usr/bin/env python3
"""
Script for building a rule
taking .mi file and dependency files(.jar for example) and 
convert to .a or .o file
"""

import sys
import os
import argparse

import_src = os.path.realpath(os.path.join(
    __file__, os.pardir, os.pardir,
    'rule-builder/src/'
    )
)
if import_src not in sys.path:
    sys.path.insert(0, import_src) # include path
from ruleBuildService.build import RuleBuildService

def parse_argument():
    parser = argparse.ArgumentParser(description="rule building")
    parser.add_argument('lang', help='target rule language')
    parser.add_argument('input', nargs='+', help='.mi input file(s)')
    parser.add_argument('-o', '--out', help='output target directory', default='.')
    parser.add_argument('-d', '--depend', help='dependency files')    
    parser.add_argument('-n', '--name', help='rule name', default='user_rule')
    parser.add_argument('-r', '--ref', help='references')
    parser.add_argument('--xvsa_home', help='xvsa directory', default='user_rule')

    args = parser.parse_args() # fill in args

    return args.lang, args.input, args.out, args.depend, args.name, args.xvsa_home, args.ref

def main():
    lang, input_file, out_dir, depend_files, name, xvsa, ref = parse_argument() # parse
    # setup
    service = RuleBuildService(lang, out_dir)
    service.add_inputs(*input_file)
    if depend_files:
        service.add_dependencies(*(depend_files.split(':'))) # split by : and put as references
    if ref:
        service.add_references(*(ref.split(':')))
    service.name_rule(name)

    # activate
    service.translate()
    service.xvsa_compile(xvsa)


if __name__ == "__main__":
    main()
