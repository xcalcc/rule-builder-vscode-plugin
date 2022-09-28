#!/usr/bin/python3
"""
annotate.py

script for annotation.
Input: .mi file ( '|' separated format)
Output: file structure (containing library etc.)
"""

import os
import argparse
from translator.read import read_annotation, read_file
from logger import get_log

LOGGER = get_log()

def main():
    """main function of script"""
    open('rule_builder.log', 'w') # clear page

    # define rb_loc
    fpath = os.path.dirname(os.path.realpath(__file__))
    rb_loc = os.path.dirname(fpath)

    parser = argparse.ArgumentParser(description="Translation Component")
    parser.add_argument('input', nargs='+', help='.mi file for input')
    parser.add_argument('-l', '--lang', help='target langauge')
    parser.add_argument('-o', '--out', help='output target directory', default='.')

    args = parser.parse_args()
    LOGGER.debug("arguments passed: %s", args)

    #### VALIDATION
    possible_lang = ['c', 'c++', 'java']

    for file_input in args.input:
        if not os.path.exists(os.path.realpath(file_input)):
            LOGGER.error("input file %s doesn't exist", file_input)

    if args.lang not in possible_lang:
        LOGGER.error("Target language not supported. Currently only 'c', 'c++', and 'java'")
        exit(-1)
    if not os.path.exists(os.path.realpath(args.out)):
        LOGGER.error("Output target directory path not exist, %s", args.out)
        exit(-1)

    LOGGER.info("validation check passed")
    LOGGER.debug("input(s): %s, language: %s, output path: %s", args.input, args.lang, args.out)

    #### READ
    lines = []
    for f_input in args.input:
        lines += read_file(f_input) # contain all lines from multiple lines into 1

    #### GENERATE .h FILE
    annotator = read_annotation(lines)
    paths = annotator.generate(
        rb_loc, os.path.realpath(args.out)
    ) # lib/translator/Annotate.generate()

    LOGGER.debug('generated files: %s', paths)

    #### GENERATE SOURCE FILE

    if args.lang == 'java':
        template_cmd = "cpp -P -DLANG_JAVA %s > %s"
        for f_path in paths:
            rule_file = f_path.replace('.h', '.java')
            os.popen(template_cmd%(f_path, rule_file))
            LOGGER.debug("%s generated", rule_file)

    else: # c/c++
        template_cmd = "cpp -P %s > %s"
        for f_path in paths:
            rule_file = f_path.replace('.h', '.cxx')
            os.popen(template_cmd%(f_path, rule_file))
            LOGGER.debug("%s generted", rule_file)

    LOGGER.info("Annotation Completed!") # success

if __name__ == "__main__":
    main()
