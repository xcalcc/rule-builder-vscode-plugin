#!/usr/bin/python3
'''
translation script

takes in input .mi file and generate rule files
'''
import sys
import os
import subprocess
import argparse

from translator.read import read_file, create_fsm
from translator.RuleFileGen import RuleFileGen

import logger
logger = logger.get_log()


logger.debug('------ Translation Start------')

# parsing
parser = argparse.ArgumentParser(description="translation component")
parser.add_argument('input', nargs='+', help='.mi file for input')
parser.add_argument('-l', '--lang', help='target language')
parser.add_argument('-r', '--ref', help='reference mi file, if multiple, use : as separator')
parser.add_argument('-n', '--name', default='rule', help='rule name')
parser.add_argument('--out', default='.', help='output directory')
args = parser.parse_args()

# mi file validation
for i in args.input:
    if not i.endswith('.mi'):
        logger.error("Invalid Input file: %s"%args.input)
        sys.exit(-1)
input_files = args.input
logger.debug('input files: %s'%input_files)

# error
err = args.name
logger.debug('error name: %s'%err)

# lang
if not args.lang:
    logger.error("Target language not specified")
    sys.exit(-1)

lang = args.lang
logger.debug('target language: %s'%lang)

# references
references = args.ref
logger.debug('references: %s'%references)

# out directory
out_dir = args.out
logger.debug('output directory: %s'%out_dir)

# create 1 fsm from >= 1 input files
fsm_list = []
for f in args.input:
    lines = read_file(f)
    fsm = create_fsm(lines)
    fsm_list.append(fsm)


# merge if >1 input files
main_fsm = fsm_list[0]

if len(fsm_list) > 1:
    for i in range(1, len(fsm_list)):
        main_fsm.merge(fsm_list[i])

# combined fsm for rule generation
file_gen = RuleFileGen(lang, references, out_dir, name=err)
file_gen.attach_fsm(main_fsm)

file_gen.generate()
