"""
Schema for the rule information
"""
import logging
import json

from common.XcalLogger import XcalLogger
from common.XcalException import XcalException
from ruleBuildService.config import ErrorNo

class RuleInfoSchema:
    """Schema for rule information

    rule information structure of json, some have a default value
    """

    def __init__(self):
        self.category = "VUL"
        self.language = ""
        self.rule_code = ""
        self.rule_name_eng = ""
        self.rule_name_cn = ""
        self.rule_desc_eng = ""
        self.rule_desc_cn = ""
        self.rule_detail_eng = ""
        self.rule_detail_cn = ""
        self.msg_template_eng = ""
        self.msg_template_cn = ""
        self.severity = "HIGH"
        self.likelihood = "LIKELY"
        self.remediation_cost = "HIGH"
        self.path = {}
        self.logger = XcalLogger("schema", "__init__")
    
    def read_json(self, content):
        """reading json file

        Read the JSON file containing rule information with mini validation
        if any mussing fields are encountered

        Args:
            content (str): JSON content
        """
        self.logger.debug("read_json", "reading JSON content: \n%s" % content)
        #json_dict = json.loads(content)
        json_dict = content
        self.logger.debug("read_json", "content in dictionary: %s" % json_dict)
        try:
            self.category = json_dict["category"] if json_dict["category"] else "VUL"
            self.language = json_dict["language"]
            self.rule_code = json_dict["rule_code"]
            self.rule_name_eng = json_dict["rule_name_eng"]
            self.rule_name_cn = json_dict["rule_name_cn"]
            self.rule_desc_eng = json_dict["rule_desc_eng"]
            self.rule_desc_cn = json_dict["rule_desc_cn"]
            self.rule_detail_eng = json_dict["rule_detail_eng"]
            self.rule_detail_cn = json_dict["rule_detail_cn"]
            self.msg_template_eng = json_dict["msg_template_eng"]
            self.msg_template_cn = json_dict["msg_template_cn"]
            self.severity = json_dict["severity"] if json_dict["severity"] else "HIGH"
            self.likelihood = json_dict["likelihood"] if json_dict["likelihood"] else "LIKELY"
            self.remediation_cost = json_dict["remediation_cost"] if json_dict["remediation_cost"] else "HIGH"
            self.path = json_dict["path"]
        except KeyError as e:
            self.logger.error("schema", "read_json", "%s not found on the json" % e.args[0])
            raise XcalException("schema", "read_json", "Field missing from JSON passed: %s" % e.args[0],
                                err_code=ErrorNo.E_INFO_FIELD_MISSING)

