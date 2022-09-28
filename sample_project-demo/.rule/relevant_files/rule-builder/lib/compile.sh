#!/bin/bash

if [ -z $1 ]
then
    echo "Provide the directory where .java.rule files are in"
    echo "Usage: $0 <directory>"
    exit 0
fi

if [ ! -d $1 ]
then
    echo "$1 is not a directory"
    exit 0
fi

project_dir=$1
cd ${project_dir}

# clean up 
rm -f *.java
rm -f *.a
rm -f *.o

# xvsa get
xvsa_home=`which xvsa`
bin_dir=`dirname $xvsa_home`
rbc_engine=$bin_dir/../include/RBC_ENGINE.java

compile()
{
    cp $rbc_engine ./
    rule_files=$1
    rule_archive=$2
    for rule_file in ${rule_files}
    do
        cp ${rule_file} "${rule_file%.*}"
    done
    javac -g -d . *.java
    class_files=`find . -name "*.class"`

    xvsa -INLINE:none -Wf,-RBC=true -c ${class_files}
    object_files=`find . -name "*.o"`
    ar cr $rule_archive ${object_files}

    rm -f *.java
    rm -f *.o
    rm -rf io
}

compileMultiple()
{
    rule_files="$1"
    rule_archive=user_def_rule.a
    echo "cocmpiling $rule_files into $rule_archive"
    compile "$rule_files" $rule_archive
}

compileAll()
{
    for comb in `ls *.rule`
    do
        rule_file="$rule_file $comb"
    done
    compileMultiple "$rule_file"
}

compileAll
