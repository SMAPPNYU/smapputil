#!/bin/bash

# get the array length
array=( $@ )
len=${#array[@]}
dirpath=`pwd -P`

# create the ouath
bash $dirpath/makeoauth.sh $1 $4 $5 $6 $7

# create the filter criteria
basestring="bash $dirpath/makefiltercriteria.sh $1 $8"
for (( c=8; c<$len; c++ ))
do
    basestring="$basestring ${array[c]}"
done
# actually call the command to make the filter criteria
$basestring

# create the collection
~/.venvs/collector/bin/python ~/TweetCollector/start_new_collection.py -s localhost -p 27017 -u $2 -w $3 -f ~/filter_criteria/$1_fc.json -o ~/oauth/$1.oauth.json -d $1 --shard
