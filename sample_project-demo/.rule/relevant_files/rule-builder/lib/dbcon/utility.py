#!/usr/bin/python3
# utility tools to interact with database

import psycopg2

# DEFAULT_VALUES FOR entry for database
DEF_CATEGORY='VUL'
DEF_LANGUAGE='java'
DEF_URL=''
DEF_NAME='DEFAULT_NAME'
DEF_SEVERITY='3'
DEF_PRIORITY='1'
DEF_LIKELIHOOD='LIKELY'
DEF_REMEDIATION_COST='LOW'
DEF_DETAIL='DEFAULT DETAIL'
DEF_DESCRIPTION='DEFAULT DESCRIPTION'
DEF_MSG_TEMPLATE='DEFAULT MESSAGE TEMPLATE'
DEF_CREATED_BY='system'
DEF_MODIFIED_BY='system'

class dbutils:
    # Supporting CRUD operations:
    # * Insert Rule Information
    # * Get Rule Information
    # * Update Rule Information
    # * Delete Rule Information

    def __init__(self, **kwargs):
        self.conn = psycopg2.connect(
            **kwargs
        )

    def get_version(self):
        conn = self.conn
        try:
            cur = conn.cursor()
            print("PostgreSQL Database Version:")
            cur.execute('SELECT version()')
            
            db_version = cur.fetchone()
            print(db_version)
        except(Exception, psycopg2.DatabseError) as error:
            print(error)
        finally:
            cur.close()

    def close(self):
        conn = self.conn 
        if conn is not None:
            conn.close()
            print("DB connection closed")

    def get_rule_info(self, rulecode):
        conn = self.conn
        cur = conn.cursor()
        cur.execute(f"SELECT * FROM xcalibyte.rule_information WHERE rule_code='{rulecode}'")    
        
        row = cur.fetchone()
        print(row)
        cur.close()
        return row

    def get_ruleset_from_code(self, rulecode):
        conn = self.conn
        cur = conn.cursor()
        sql_cmd = """SELECT s.name FROM xcalibyte.rule_information i 
                    INNER JOIN xcalibyte.rule_set s on i.rule_set_id=s.id 
                        where i.rule_code=%s"""
        cur.execute(sql_cmd, (rulecode,))        
        r = cur.fetchone()
        return r[0]

    def delete_rule(self, rulecode):
        conn = self.conn
        cur = conn.cursor()
        
        ruleset = self.get_ruleset_from_code(rulecode) 
        cur.execute(f"DELETE FROM xcalibyte.rule_information WHERE rule_code=%s", (rulecode,))
        fields=['description','detail', 'name', 'msg_template']
        
        for f in fields:
            self.delete_i18n_message(ruleset, rulecode, f)
        conn.commit()
        print(f"{rulecode} is removed from database")
        cur.close()

    def get_id_rule_set(self, name):
        conn = self.conn
        cur = conn.cursor()
        cur.execute("SELECT id from xcalibyte.rule_set where name=%s", (name,)) 
        row=cur.fetchone()
        cur.close()
        return row[0]
    
    def insert_rule(self, rule_set, rulecode, description="default description", name=DEF_NAME):
        conn = self.conn
        cur = conn.cursor()

        sql_statement = """ INSERT INTO xcalibyte.rule_information(rule_set_id, category, vulnerable, rule_code, language, url, name, severity, priority, likelihood, remediation_cost, detail, description, msg_template, created_by, modified_by)
        VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
        
        def_description = "${rule.Xcalibyte.%s.1.%s.description}"%(rule_set, rulecode)
        def_detail = "${rule.Xcalibyte.%s.1.%s.detail}"%(rule_set, rulecode)
        def_msg_template = "${rule.Xcalibyte.%s.1.%s.msg_template}"%(rule_set, rulecode)
        def_name = "${rule.Xcalibyte.%s.1.%s.name}"%(rule_set, rulecode) 

        # get the rule_set_id first
        rule_set_id = self.get_id_rule_set(rule_set)
        
        # sample data entry
        data = (rule_set_id, DEF_CATEGORY,
            rulecode , 
            rulecode, DEF_LANGUAGE,
            DEF_URL, def_name,
            DEF_SEVERITY, DEF_PRIORITY,
            DEF_LIKELIHOOD, DEF_REMEDIATION_COST,
            def_detail, def_description,
            def_msg_template, DEF_CREATED_BY,
            DEF_MODIFIED_BY)  
        cur.execute(sql_statement, data)
        conn.commit()
        
        # put i18n_messages
        self.insert_i18n_message( rule_set, rulecode, 'description', description)
        self.insert_i18n_message( rule_set, rulecode, 'detail', def_detail)
        self.insert_i18n_message( rule_set, rulecode, 'msg_template', DEF_MSG_TEMPLATE)
        self.insert_i18n_message( rule_set, rulecode, 'name', name)
        
        print(f"{rulecode} is inserted")
        cur.close()

    def update_rule(self, rulecode, description):
        conn = self.conn
        cur = conn.cursor()
        sql_update = """ UPDATE xcalibyte.rule_information set description = %s where rule_code = %s"""
        cur.execute(sql_update, (description, rulecode))
        conn.commit()
        print(f"{rulecode} updated")
        cur.close()
    
    def get_scan_engine_id(self):
        conn = self.conn
        cur = conn.cursor()
        cur.execute("SELECT id FROM xcalibyte.scan_engine") 
        r = cur.fetchone()
        cur.close()
        return r[0]

    def new_rule_set(self, rule_set_name="CUSTOMIZED"):
        conn = self.conn
        cur = conn.cursor()
        d_version='1'
        d_revision='1.0'
        d_description='Customer Defined Rules'
        d_lang = 'c,c++,java'
        d_url='http://google.com'
        d_provider='xcalibyte'
        d_provider_url='http://www.xcalibyte.com'
        d_license = 'Xcalibyte commercial license',
        d_license_url = ''
        d_created_by = 'system'
        d_modified_by = 'system'

        sql_cmd = """INSERT INTO xcalibyte.rule_set(scan_engine_id, name, version, revision, display_name, description, language, url, provider, provider_url, license, license_url, created_by, modified_by) 
         VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
        
        data = (
            self.get_scan_engine_id(), rule_set_name,
            d_version, d_revision, rule_set_name,
            d_description, d_lang, d_url,
            d_provider, d_provider_url, d_license, d_license_url,
            d_created_by, d_modified_by
        ) 

        cur.execute(sql_cmd, data)
        conn.commit()
        print("New Rule Set Inserted")
        cur.close()
    
    def get_rule_set(self, rule_set_name):
        conn = self.conn
        cur = conn.cursor()
        cur.execute("SELECT * FROM xcalibyte.rule_set WHERE display_name=%s", (rule_set_name,))
        r = cur.fetchone()
        cur.close()
        return r 

    def get_i18n_message(self, rulecode, ruleset, field, lang='en'):
        conn = self.conn
        cur = conn.cursor()
        cur.execute("SELECT * FROM xcalibyte.i18n_message WHERE (message_key=%s AND locale=%s)", ('rule.Xcalibyte.'+ruleset+'.1.'+rulecode +'.'+field, lang))
        r = cur.fetchone()
        cur.close()
        return r

    def insert_i18n_message(self, ruleset, rulecode, field, content, lang='en'):
        conn = self.conn
        cur = conn.cursor()
         
        sql_cmd = """INSERT INTO xcalibyte.i18n_message(locale, message_key, content, created_by, modified_by) 
                    VALUES(%s,%s,%s,%s,%s)"""
        data = (
            lang, 'rule.Xcalibyte.'+ruleset+'.1.'+rulecode +'.'+field, content, 'system', 'system'
        )
        
        cur.execute(sql_cmd, data)
        conn.commit()
        cur.close()
        print("i18n_message delivered")
    def delete_i18n_message(self, ruleset, rulecode, field, lang='en'):
        conn = self.conn
        cur = conn.cursor()
        sql_cmd = """DELETE from xcalibyte.i18n_message WHERE message_key=%s"""
        key = 'rule.Xcalibyte.'+ruleset+'.1.'+rulecode+'.'+field
        cur.execute(sql_cmd, (key,))
        conn.commit()
        cur.close()
    def get_rules_from_rule_set(self, ruleset):
        conn = self.conn
        cur = conn.cursor()

        ruleset_id = self.get_id_rule_set(ruleset)
        sql_cmd = """SELECT * FROM xcalibyte.rule_information WHERE rule_set_id=%s"""
        cur.execute(sql_cmd, (ruleset_id,))
        r = cur.fetchall()

        cur.close()
        return r
    def remove_rule_set(self, ruleset):
        conn = self.conn
        cur = conn.cursor()

        sql_cmd = """DELETE from xcalibyte.rule_set WHERE name=%s"""
        cur.execute(sql_cmd, (ruleset,)) 
        conn.commit()
        cur.close()
