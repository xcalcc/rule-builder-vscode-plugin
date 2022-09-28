# Translating SER03

Example is SER03, now, there is a mix between rule and tagging. Here is how to translate this into some files.

# Steps

```bash
../translate_g.py ser03.mi -l java -r rt.o.vtable.mi --name SER03
```

After executing command above, you will find 2 files: *SER03.java* AND *Point.java*.
To build file later on, you will need both these files.

