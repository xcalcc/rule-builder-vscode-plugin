"""
Generator for the masterfile and ruleset for custom rules
in JSON data format.
"""

import logging
import json

from common.XcalLogger import XcalLogger
from common.XcalException import XcalException
from ruleBuildService.ruleInfo.schema import RuleInfoSchema

def csv_stringify(code):
    """shorten code

    shorten the rule code into a string
    that is acceptable by code
    options for codes:
    * CSV: {3char} -> CSV
    * CSV01: {3char}{2digit} -> C010
    * CSV01-J: {3char}{2digi}-{J/C/CPP} -> C01J0

    Args:
        code (str): rule code
    """
    if len(code) == 3: # all char
        return code+'0'
    elif len(code) == 5:
        return code[0] + code[-2:] + '0'
    else:
        return code[0] + code[3:5]  + code[-1] + '0'


class MasterCustom:
    """create masterfile and ruleset json files

    hold schema and generate json for both the masterfile and ruleset
    file of JSON.

    Args:
        info_schema (RuleInfoSchema): extract from information schema
    """
    GLOBAL_ID = 0 # initialised GLOBAL_ID to send
    PATHMSG_ID = 1
    def __init__(self, info_schema: RuleInfoSchema):
        self.info = info_schema
        self.logger = XcalLogger("MasterCustom", "__init__")
        self.master_id = MasterCustom.GLOBAL_ID
        MasterCustom.GLOBAL_ID = MasterCustom.GLOBAL_ID + 1

    def master(self):
        """generate the masterfile

        returns the json format 
        """
        self.logger.debug("master", "generating masterfile dictionary")
        info = self.info
        en_master = {
            "master_id": self.master_id,
            "category": info.category,
            "language": info.language,
            "code": info.rule_code,
            "name": info.rule_name_eng,
            "desc": info.rule_desc_eng,
            "detail": info.rule_detail_eng,
            "msg_templ": info.msg_template_eng,
            "owasp": ""
        }
        
        cn_master = {
            "master_id": self.master_id,
            "category": info.category,
            "language": info.language,
            "code": info.rule_code,
            "name": info.rule_name_cn,
            "desc": info.rule_desc_cn,
            "detail": info.rule_detail_cn,
            "msg_templ": info.msg_template_cn,
            "owasp": ""
        }

        return en_master, cn_master

    def ruleset(self):
        """generating ruleset

        returns json format
        """
        self.logger.debug("ruleset", "generating ruleset JSON")
        info = self.info
        ruleset = {
            "core_string": info.rule_code,
            "csv_string": csv_stringify(info.rule_code),
            "severity": info.severity[0],
            "likelihood": info.likelihood[0],
            "cost": info.remediation_cost[0],
            "master_id": self.master_id,
            "id": self.master_id # not important, can ignore
        }
        return ruleset

    def pathmsg(self):
        """generating pathsg json

        returns a pathmsg.json file
        """
        self.logger.debug("pathmsg", "generating pathmsg JSON")
        info = self.info
        en_paths = []
        cn_paths = []

        for _, msg in info.path.items():
            path_id = MasterCustom.PATHMSG_ID
            MasterCustom.PATHMSG_ID = MasterCustom.PATHMSG_ID + 1
            en_paths.append(
                {
                    "id": path_id,
                    "msg": msg
                } # json
            )
            cn_paths.append(
                {
                    "id": path_id,
                    "msg": msg
                }
            )
        return en_paths, cn_paths