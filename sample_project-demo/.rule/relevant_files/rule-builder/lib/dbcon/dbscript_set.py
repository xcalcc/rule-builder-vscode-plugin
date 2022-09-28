#!/usr/bin/python3

import argparse
import psycopg2
import sys
from utility import dbutils
from configparser import ConfigParser

parser = argparse.ArgumentParser(description='rule set DB interaction')
parser.add_argument('--insert', action='store_true', help='mode insert rule set')
parser.add_argument('--delete', action='store_true', help='mode delete rule set')
parser.add_argument('name', help='rule set name')

args = parser.parse_args()
action=args.insert+args.delete

if action > 1:
    print("Too many mode on")
    sys.exit(1)
elif action < 1:
    print("No mode selected")
    sys.exit(1)

conf_parser = ConfigParser()
conf_parser.read('config.ini')
params={}
par = conf_parser.items('postgresql')
for param in par:
    params[param[0]] = param[1]

# initiate the dbutil and test to check version
dbutil = dbutils(**params)
name = args.name
# INSERTING NEW RULE SET
if args.insert:    
    print("Attempt to insert rule set %s"%name)
    dbutil.new_rule_set(name)    

# DELETING EXISTING RULE SET
elif args.delete:
    print("Attempt to delete rule set %s"%args.name)
    dbutil.remove_rule_set(name) 
