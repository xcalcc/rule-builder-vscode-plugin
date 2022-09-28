#!/usr/bin/python3

# =================
# dbtest
# connection to postgresql test
# see if any query can be done and get stuff
# =================

import psycopg2
from utility import dbutils
from configparser import ConfigParser

def connect():
    conn = psycopg2.connect(
        host="127.0.0.1",
        database="xxx",
        user="xxx",
        password="xxx"
    )
    return conn

def get_version(conn):
    try:
        cur = conn.cursor()
        print('PostgreSQL database version:')
        cur.execute('SELECT version()')


        db_version = cur.fetchone()
        print(db_version)
        cur.close()
    except psycopg2.DatabaseError as error:
        print(error)
    #finally:
    #   if conn is not None:
    #       conn.close()
    #       print("Database connection closed.")

def close(conn):
    if conn is not None:
        conn.close()
        print("Database connection closed.")

def get_users(conn):
    cur = conn.cursor()
    cur.execute("SELECT * from xcalibyte.user_group")
    row = cur.fetchall()

    for i in row:
        print(i)
    cur.close()

def get_rule_info(conn):
    cur = conn.cursor()
    cur.execute("SELECT rule_code,name FROM xcalibyte.rule_information")
    rows = cur.fetchall()

    for r in rows:
        print(r)
    cur.close()

def get_rule(conn, rulecode):
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM xcalibyte.rule_information WHERE rule_code='{rulecode}'")
    row = cur.fetchone()

    print(row)
    cur.close()

def insert_rule(conn, data):
    sql="""INSERT INTO xcalibyte.rule_information(rule_set_id, category, vulnerable, certainty, rule_code, language, url, name, severity, priority, likelihood, remediation_cost, detail, description, msg_template, created_by, modified_by) 
            VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
    try:
        cur = conn.cursor()
        cur.executemany(sql,data)
        conn.commit()
        cur.close()
    except psycopg2.DatabaseError as error:
        print(error) 

def get_rule_set(conn):
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM xcalibyte.rule_set")
    row = cur.fetchall()
    for i in row:
        print(i)

def get_id_rule_set(conn, name):
    cur = conn.cursor()
    cur.execute(f"SELECT id FROM xcalibyte.rule_set where name='{name}'")
    row = cur.fetchone()
    print(row)
    return row[0]
    cur.close()

def get_scan_engine(conn):
    pass
    cur = conn.cursor()
    cur.execute(f"SELECT id FROM xcalibyte.scan_engine")
    rows=  cur.fetchone()
    print(rows[0])
    cur.close()

def get_rule_sets(conn):
    cur = conn.cursor()
    cur.execute("SELECT * FROM xcalibyte.rule_set")
    rows = cur.fetchall()
    for i in rows:
        print(i)
    cur.close()

conf_parser = ConfigParser()
conf_parser.read('config.ini')
params = {}
par = conf_parser.items('postgresql')
for param in par:
    params[param[0]] = param[1]

# initiate the dbutil and test to check version
dbutil = dbutils(**params)

#info=dbutil.get_rule_set('CUSTOM')
#dbutil.new_rule_set("CUSTOM")
#info = dbutil.get_i18n_message("TEST01-J", "CUSTOMIZED", "description")
#print(info)
#dbutil.insert_i18n_message("CUSTOMIZED", "TEST01-J", "description", "ABCDESCRIPTION")
#dbutil.insert_rule("BUILTIN", "TEST02-J", "Default Description",  "Test Rule in Java")
#print(dbutil.get_rule_info("TEST02-J"))
#print(dbutil.get_i18n_message("TEST02-J", "BUILTIN", "description"))
#print(dbutil.get_ruleset_from_code("AOB"))
#print(dbutil.delete_i18n_message("BUILTIN", "TEST02-J", "description"))
#dbutil.delete_rule("TEST02-J")
#print(dbutil.get_id_rule_set("CUSTOMIZED"))
#print(dbutil.get_rules_from_rule_set("CUSTOMIZED"))
#dbutil.remove_rule_set('CUSTOM')

