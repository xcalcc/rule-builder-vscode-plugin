# Building Rule (CWE295 example)

The input into this tool is the rule file (CWE295.java) which is generated from the previous tool (translation). 
Located in this directory is a sample bad case file for CWE295 rule (*cwe295_bad.java*). The example case will be for testing later on. 

Here is how to build the file 


```bash
rbuild CWE295.java -j apache-mail.jar:javax-mail.jar
```

the command above passes the -j option which is to include a dependency file (.jar) file that is needed for java to compile the case file itself. 
Once process is completed, you can find 2 generated files: .a and .o file under {RULE-BUILDER-HOME}/rules/{RULE-NAME}/scan/user_def_rule.a or lib.o


In order to check whether the rule is succesfully built, try: 

```bash
rscan-py cwe295_bad.java CWE295
```

See if CWE295 is reported, then build is successful.
