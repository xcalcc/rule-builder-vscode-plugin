#!/usr/bin/python3
'''
Script to get rule information 
use -h option to see command usage
'''

import argparse
from api import API

parser = argparse.ArgumentParser(description="Get from DB")


parser.add_argument('-a', '--address', help='IP address')
parser.add_argument('code', nargs='?', help='rulecode')
parser.add_argument('ruleset', nargs='?', help='rule set')
parser.add_argument('--set', action="store_true", help="ruleset=TRUE?")

args = parser.parse_args()

# validation
if args.address:
    if not args.address.startswith('http'):
        API.URL = 'http://'+args.address # prepend http:// if not found
    else:
        API.URL = args.address

if not args.code and not args.ruleset:
    print("No arguments passed")
    exit(-1)



# API Interaction
token = API.login()

