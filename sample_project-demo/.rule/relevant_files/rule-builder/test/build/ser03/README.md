# Building SER03

In this part we are doing build with 2 files. 1 file contains the FSM rule file while the other is a class file with tagging involved. 

## Steps

```bash
rbuild SER03.java Point.java
```

We are not passing -j parameter here because no additional dependency is needed. 
To scan it:

```bash
rscan-py j_ser_03_0.java SER03
```

Check whether or not SER03 is reported after doing the scan
