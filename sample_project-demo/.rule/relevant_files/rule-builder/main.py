#!/usr/bin/python3

'''
main script
'''
import os
import time
import sys
import argparse
import configparser
import json
import subprocess
import pexpect
from pathlib import Path
from glob import glob
from lib import get_log

logger = get_log()

rb_loc = os.path.dirname(os.path.abspath(__file__))
space = ' '
def get_file(path):
    return os.path.join(rb_loc, path)

tmp_dir = get_file('tmp')
remote_dir = 'xxx@127.0.0.1:/home/xxx/server/xcalibyte/xcalscan/2020-12-25/data/volume/rules'

def main(in_file, conf):
    '''main function for execution'''
    
    #### CHECK
    logger.debug('#### checking system ####')
    checker_script = get_file('bin/checker')
    check_status = subprocess.call([checker_script])
    if check_status != 0:
        logger.error('check failed')
        exit(-1)
    logger.debug('system check passed') 

    #### SETUP
    logger.debug('#### setup ####')
    setup_script = get_file('bin/setup')
    if not os.path.exists(get_file('lib/rt.o')):
        setup_status = subprocess.call([setup_script])
        if setup_status != 0:
            logger.error('setup failed')
            exit(-1)
        logger.debug('setup passed')
    else:
        logger.debug('setup skipped')

    #### INSTALL
    logger.debug('#### install dependencies ####')
    req_txt = get_file('requirements.txt')
    install_status = subprocess.call(
        [
            'pip3',
            'install',
            '-r',
            req_txt
        ]
    )
    if install_status != 0:
        logger.error('dependency installation faile')
        exit(-1)
    logger.debug('installation successful')

    #### TRANSLATION
    logger.debug('#### translation ####')
    translate_script = get_file('lib/translate.py')
    translate_cmd = [
        'python3',
        translate_script,
        in_file,
        '-l', conf['lang'],
        '-r', conf['references'],
        '--name', conf['name'],
        '--out', tmp_dir
    ]
    logger.info(space.join(translate_cmd))
    translate_status = subprocess.call(translate_cmd)
    if translate_status != 0:
        logger.error('translation failed')
        exit(-1)
    main_rule_file = '%s.%s'%(conf['name'], conf['lang'])

    if not os.path.exists(os.path.join(tmp_dir, main_rule_file)):
        time.sleep(2)

    logger.debug('translation successful')
    

    #### RULE COMPILATION
    logger.debug('#### rule compilation ####')
    build_script = get_file('rbuild-py')
    dep_files = conf['dependency']
    logger.debug('dependency files: %s'%dep_files)
    #rule_files = [i for i in os.listdir(tmp_dir)
    #                if i.endswith('.%s'%conf['lang'])] # rule files according to extension
    rule_files = [i for i in Path(tmp_dir).rglob('*.%s'%conf['lang'])]
    logger.debug('main rule file: %s'%main_rule_file)
    for i in range(len(rule_files)):
        if os.path.basename(rule_files[i]) == main_rule_file and i != 0:
            rule_files.insert(0, rule_files.pop(i)) # ordering main_rule_file to be put on first index
    logger.debug('rule_files: %s'%rule_files)

    build_cmd = [build_script]
    #build_cmd += rule_files
    #build_cmd += [os.path.join(tmp_dir, i) for i in rule_files]
    build_cmd += [os.path.join(rb_loc, i) for i in rule_files]
    if dep_files:
        build_cmd += ['-j']
        build_cmd += [dep_files] # add dependency files if exist
    build_cmd += ['--name', conf['name']]
    logger.debug("build command: %s"%' '.join(build_cmd))
    build_status = subprocess.call(build_cmd)
    if build_status != 0:
        logger.error("build failed")
        exit(-1)
    logger.debug("build success")

    #### INSERT RULE INFORMATION
    logger.debug('#### rule info insertion ####')
    db_host = conf['host']
    db_user = conf['user']
    db_port = conf['port']
    db_password = conf['password']
    insert_script = get_file('lib/api/insert.py') # rule insertion script
    logger.debug('insert script located in %s'%insert_script)
    
    for rule in conf['rules']: # insert rules 1 by 1
        logger.debug('rule: %s'%rule)
        insert_cmd = [
            insert_script,
            rule['rulecode'],
            rule['ruleset'],
            '-a', db_host,
            '-d', '"%s"'%rule['description'],
            '-n', '"%s"'%rule['name']
        ]
        logger.debug(" ".join(insert_cmd))
        insert_status = subprocess.call(insert_cmd)

        if insert_status != 0:
            logger.error('insertion failure')
            break
        logger.debug('rule %s inserted'%rule['rulecode'])

    #### MOVING .a AND .o FILE
    logger.debug('#### copying compiled file to server ####')

    err_name = conf['name'] # err_name
    err_scan_dir = get_file('rules/%s/scan'%err_name)
    logger.debug('out_dir = %s'%err_scan_dir)

    scan_files = os.listdir(err_scan_dir)
    if len(scan_files) < 1:
        logger.error("no files to move")
        exit(-1)
    logger.debug('scan_files: %s'%scan_files)
    scan_files = [os.path.join(err_scan_dir, i) 
                    for i in scan_files] # path
    target_dir = conf['target'] # target directory of copy
    if not os.path.isdir(target_dir):
        logger.error("target directory doesn't exist")
        exit(-1)

    for i in scan_files:
        f = os.path.join(err_scan_dir, i)
        subprocess.call(
            [
                'cp',
                f,
                target_dir
            ]
        )

if __name__ == '__main__':
    log_path = get_file('rule_builder.log')
    log_file = open(log_path, 'w')
    log_file.close()

    subprocess.call(['rm', '-r', tmp_dir])
    os.mkdir(tmp_dir)

    logger.info('main script called')
    logger.debug('path to rb: %s'%rb_loc)
    # clean log and tmp directory  
    
    # argument parse
    parser = argparse.ArgumentParser(description='main script')
    parser.add_argument('input', help='input .mi file')
    parser.add_argument('conf', help='config file with parameters')
    args = parser.parse_args()
    
    if not os.path.exists(args.input):
        logger.error('input file not found')
        exit(-1)
    if not os.path.exists(args.conf):
        logger.error('config file not found') 
        exit(-1)
    
    # configuration parsing
    config_parser = configparser.ConfigParser()
    config_parser.read(args.conf)
    config = {}

    for param in config_parser.items('config'):
        config[param[0]] = json.loads(param[1])

    logger.debug('parameters: %s'%config)
    main(args.input, config)

