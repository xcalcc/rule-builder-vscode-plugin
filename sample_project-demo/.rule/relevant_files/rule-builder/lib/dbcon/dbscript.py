#!/usr/bin/python3

import argparse
import psycopg2
import sys
from utility import dbutils
from configparser import ConfigParser
# Script for executing database CRUD operations
parser = argparse.ArgumentParser(description='database interaction')
parser.add_argument('--insert', action='store_true', help='mode insert')
parser.add_argument('--update',  action='store_true', help='mode update')
parser.add_argument('--delete', action='store_true', help='mode delete')
parser.add_argument('--get', action='store_true', help='mode get')
parser.add_argument('-d', '--description', help='description', nargs='?')
parser.add_argument('-n', '--name', help='rule name')
parser.add_argument('code',  help='rule code')
parser.add_argument('ruleset', help='rule set', nargs='?')


args = parser.parse_args()
action=args.insert+args.update+args.delete+args.get
if not action == 1:
    print("Too many mode on")
    sys.exit(1)


conf_parser = ConfigParser()
conf_parser.read('config.ini')
params={}
par = conf_parser.items('postgresql')
for param in par:
    params[param[0]] = param[1]

# initiate the dbutil and test to check version
dbutil = dbutils(**params)

# INSERT
if args.insert:
    if not args.ruleset:
        print("rule set information not provided")
        sys.exit(-1)
    # all valid information here
    description = args.description
    name = args.name 
    if not description:
        description = 'DEFAULT DESCRIPTION'
    if not name:
        name = 'DEFAULT NAME'
    dbutil.insert_rule(args.ruleset, args.code, description, name)
     
# GET
elif args.get:
    res=dbutil.get_rule_info(args.code)

# UPDATE
elif args.update:    
    if not args.description:
        print("You do not specify the new description")
        sys.exit(-1)
    dbutil.update_rule(args.code, args.description)    
# DELETE
elif args.delete:
    dbutil.delete_rule(args.code)

dbutil.close()
