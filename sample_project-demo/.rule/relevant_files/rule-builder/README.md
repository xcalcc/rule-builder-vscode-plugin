# Rule Builder

Rule Builder is a tool that is used to faciliate users in building their own rule. Rules can be created as an FSM model or just simply an assertion.

## Prerequisites
- python >= 3.6
- java 
- xvsa

Please set *JAVA_HOME* and *XVSA_HOME* environment path variable. 
Also, add the directory for rule builder into PATH environment variable.

## Components 

1. Translation 
Translation is the first phase of the building process. It takes user input as logic (.mi) file and convert into source code whether it is in a form of FSM Or just simple TAG or ASSERT.

2. Building
Building comes right after translation. Translation will generate some source file where it will be used in order to create a .a and .o file, to be mounted to xvsa. 

For demonstrative purposes, you can look under test/ for some examples.

## Directory Structure
To view source codes that contribute to the API, you can access the lib/ directory. 
A rework of directory with its corresponding auto documentation is already planned.

