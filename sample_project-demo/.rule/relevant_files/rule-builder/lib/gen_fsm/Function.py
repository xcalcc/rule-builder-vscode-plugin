#Class File for Function
# Parsing Function Prototype into important parts


class Function:
    # ATTRIBUTES
    # ----------
    # fullname: full function name    
    # retvalue: return value 
    # retvaluepackage: return value's package
    # clsname = class name
    # pkgname = package name
    # fsignature = function signature
    # params = string of parameter inside fsignature (..)
    # importlist = list of packages need to be imported
    # paramstr = string of list of parameters to be put inside function later on 
    # ----------
    
    # some fixes to data type
    type_correction = {
        "bool": "boolean"
    }

    def __init__(self, fullname):
        self.fullname = fullname.replace('*', '').replace('::','.')
        self.parse()
    def parse(self):
        temp = self.fullname.split(' ')
        # return value and its package (if need to import)
        if len(temp) == 1: # constructor
            self.retvalue = ""
            self.retvaluepackage = ""
        else:
            self.retvalue = temp[0].split('.')[-1]
            if self.retvalue in Function.type_correction:
                self.retvalue = Function.type_correction[self.retvalue]
            self.retvaluepackage = temp[0]
        
        # set the function part for further parsing
        func = ""
        if len(temp) ==1:
            func = temp[0] 
        else:
            func = temp[1]
        # get package name, class name, function name, function parameter from func
        split = func[:func.find('(')]
        
        split = split.split('.')
        self.clsname = split[-2]
        self.pkgname = '.'.join(split[:-2])
        self.fsignature = split[-1]
        #self.params = split[-1][ split[-1].find('(')+1 : split[-1].find(')')]
        self.params= func[func.find('(')+1: func.find(')')]
        params = self.params # temporary 

        # From the function parameter, get the paramstr, and supposed import
        param_split = params.split(',')
        for i in range(len(param_split)):
            if param_split[i] in Function.type_correction:
                param_split[i] = Function.type_correction[param_split[i]]
        if param_split[0] == '':
            param_split = []
        self.importlist = []
        temp = []
        self.paramstr = ""
        for i in param_split:
            if '.' in i: # means not builtin
                self.importlist.append(i)
        for idx, p in enumerate(param_split):
            temp.append('{} var{}'.format(p.split('.')[-1], idx+1))
        self.paramstr = ', '.join(temp)

