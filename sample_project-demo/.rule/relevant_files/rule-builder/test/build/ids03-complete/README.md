# Compiling IDS03-J 

IDS03-J: Do not log unsanitized user input.
In this directory, there are 2 important parts, Logger.java and Informer.java. One is Logger.java containing the rule assertion, while Informer.java contains the tagging for a particular function to mark that one of the arguments is "tainted".

```bash
rbuild Logger.java Informer.java
```

To try scanning for the rule:
```bash
rscan-py ids03_j.java Logger
```

It should be reporting IDS03-J. On top of that notice that it is [M]
