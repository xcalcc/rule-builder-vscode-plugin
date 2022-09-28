import requests

class API:
    URL = "http://127.0.0.1:8080"
    
    @classmethod
    def login(cls):
        link = cls.URL+'/api/auth_service/v2/login'
        data = {
            "username": "xxx",
            "password": "xxx"
        }
        response = requests.post(url=link, json=data)

        # return the token expected from here
        return response.json()['accessToken'] # return the bearer token

    @classmethod
    def get_rule_sets(cls, token):
        link = cls.URL + '/api/rule_service/v2/rule_sets'
        
        # call with header authorization of bearer token
        response = requests.get(url=link, headers={'Authorization': 'Bearer '+token})
        return response.json()

    @classmethod
    def insert_rule(cls, token, ruleCode, ruleset="CUSTOM", name="default name", description="default description"):
        link = cls.URL + '/api/rule_service/v2/rule_set/' 

        # clean-up, avoid having content between double-quotes
        if description.startswith('"'): 
            description = description[1:]
        if description.endswith('"'):
            description = description[:-1]

        if name.startswith('"'):
            name = name[1:]
        if name.endswith('"'):
            name = name[:-1]

        data = {
            "name": "Xcalibyte",
            "version": "1",
            "rulesets": [
                {"name": ruleset,
                "version": "1",
                "revision": "1.0.0",
                "display_name": ruleset,
                "description": "Customized rule set",
                "language": "c,c++,java",
                "url": "",
                "provider": "Xcalibyte",
                "provider_url": "http://xcalibyte.com",
                "license": "Xcalibyte commercial license",
                "license_url": "",
                "rules": [
                    {
                        "code": ruleCode,
                        "name": name,
                        "description": description,
                        "details": "${rule.Xcalibyte.%s.1.%s.detail}"%(ruleset,ruleCode),
                        "languages": "java",
                        "category": "VUL",
                        "severity": "HIGH",
                        "priority": "HIGH",
                        "likelyhood": "LIKELY",
                        "fix_cost": "LOW",
                        "rule_url": "http://google.com"
                    }
                ]
        }
        ]
    }
    
        try:
            response = requests.post(url=link, json=data, headers={'Authorization': 'Bearer '+token})
        except:
            print("Insertion fail")
        return response
    

