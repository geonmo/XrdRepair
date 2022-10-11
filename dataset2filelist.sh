#!/bin/bash

if [[ $# -ne 2 ]]; then
    echo "Illigal arguments."
    echo "Usage) dataset2filelist.sh <Dataset list file> <Output filename>"
    echo "ex) dataset2filelist.sh input_datasetlist.txt datalist.txt"
    exit -1
fi


datasets=$(cat $1)
output=$2

while :
do
    voms-proxy-info -exists -valid 8:0 > /dev/null
    if [ $? -ne 0 ]; then
        voms-proxy-init --voms cms
    else
        echo "Found a Valid proxy certificate."
        break
    fi
done

if [ -f "$output" ] ; then
    rm "$output"
fi

for line in $datasets
do
    echo $line
    DATASET_TYPE=${line:(-4)}
    if [ ${DATASET_TYPE} == "USER" ]; then
        echo "Private Datasets!"
        ./dasgoclient --query="file dataset=$line instance=prod/phys03 |grep file.name,file.size" >> $output
    else
        echo "Global Datasets!"
        ./dasgoclient --query="file dataset=$line |grep file.name,file.size" >> $output
    fi
done





