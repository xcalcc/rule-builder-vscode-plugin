#!/usr/bin/python3
'''
Script to insert rule information
use -h option to see command usage
'''

import argparse
from api import API

parser = argparse.ArgumentParser(description="Insertion to DB")

parser.add_argument('-a', '--address', help='IP address')
parser.add_argument('-d', '--description', help='modify description', default='Some description ...')
parser.add_argument('-n', '--name', help='rule name', default="User Custom Rule")

parser.add_argument('code', help='rule code to insert')
parser.add_argument('ruleset', nargs='?', help='Rule set content', default="CUSTOM")

args = parser.parse_args()

if args.address:
    if not args.address.startswith('http'):
        API.URL = 'http://'+args.address
    else:
        API.URL = args.address

# EXECUTION
token = API.login()
res = API.insert_rule(token, args.code, args.ruleset, args.name, args.description)

if res.ok:
    print("Successful Insertion")
else:
    print("Insertion failure")
