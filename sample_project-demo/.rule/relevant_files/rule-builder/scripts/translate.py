#!/usr/bin/env python3
"""
script for translation
take .mi file into rule files
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
from common.XcalLogger import XcalLogger
from common.XcalException import XcalException

def parse_argument():
    parser = argparse.ArgumentParser(description="translation")
    parser.add_argument('lang', help='target rule language')
    parser.add_argument('input', nargs='+', help='.mi files')
    parser.add_argument('-o', '--out', help='output target dir', default='.')
    parser.add_argument('-n', '--name', help='rule name', default='user_rule')
    parser.add_argument('-r', '--ref', help='references')

    args = parser.parse_args() # fill in args
    return args.lang, args.input, args.out, args.name, args.ref

def main():
    """main func"""
    lang, in_file, out_dir, name, ref = parse_argument()

    # setup
    service = RuleBuildService(lang, out_dir)
    service.add_inputs(*in_file)

    # small checks
    if ref:
        service.add_references(*(ref.split(':'))) # split with : if needed
    service.name_rule(name)

    # translate
    service.translate()

if __name__ == "__main__":
    main()
