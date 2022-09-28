"""
main service to push new rule information
to the rule service in JSON format.
Should allow multiple read sequence
"""

import logging
import json
import os

from ruleBuildService.ruleInfo.schema import RuleInfoSchema
from ruleBuildService.ruleInfo.custom import csv_stringify, MasterCustom
from ruleBuildService.config import ErrorNo
from common.XcalException import XcalException
from common.XcalLogger import XcalLogger

class InfoPush:
    """RuleInfo push proxy

    Service for the rule builder front end (VSCode) to push the rule information.
    Read data, massage it and call rule service to handle the storage of rule information.
    Helps later on in synchronization
    
    """

    def __init__(self):
        self.logger = XcalLogger("InfoPush", "__init__")
        self.json_data = {
            "en": {
                "rulesets": [],
                "rules": [],
                "pathmsg": []
            },
            "cn": {
                "rulesets": [],
                "rules": [],
                "pathmsg": []
            }
        }

    def read_path(self, path):
        """read json file through path

        reading content of json path to convert every rule 
        into schema structure RuleInfo schema.

        Args:
            path (str): path to the json file


        """
        if not os.path.exists(path):
            raise XcalException("info_push", "read_path", 
                                "path: %s not found" % path,
                                err_code=ErrorNo.E_RESOURCE_NOT_FOUND)
        self.logger.debug("read_path", "reading from path: %s" % path)

        with open(path) as info_file:
            data = json.load(info_file)
            for d in data:
                schema = RuleInfoSchema()
                schema.read_json(d)
                self.add_to_data(schema)

    def add_to_data(self, data: RuleInfoSchema):
        """adding to json

        adding schema to list of data in json format
        Args:
            data (RuleInfoSchema): singular schema data
        """
        self.logger.debug("add_to_data", "data: %s" % data.rule_code)
        custom = MasterCustom(data) # custom rule

        master_en, master_cn = custom.master()
        ruleset = custom.ruleset()
        path_en, path_cn = custom.pathmsg()

        # adding to json_data
        self.json_data['en']['rules'].append(master_en)
        self.json_data['cn']['rules'].append(master_cn)

        self.json_data['en']['rulesets'].append(ruleset)
        self.json_data['cn']['rulesets'].append(ruleset)

        self.json_data['en']['pathmsg'] += path_en
        self.json_data['cn']['pathmsg'] += path_cn

    def dump_to_file(self, path=os.curdir, name="custom.json"):
        """dumping json content into a file

        dumping json into file that contains the master

        Args:
            path (str): path to file
            name (str): intended name of file
        """
        out_file = os.path.realpath(os.path.join(path, name))
        with open(out_file, 'w') as write_file:
            json.dump(self.json_data, write_file, indent=2) # print with format