#!/bin/bash

#make an array, get all elements in the array from the third (index 2) input on
array=( $@ )
len=${#array[@]}
afterargs=${array[@]:2:$len}

#create a structure for track, geo, or follow, can only do one with this script
if [ "$2" = "track" ]
then
    basestring=""
    for (( c=2; c<$len; c++ ))
    do
        if [ $c = $(($len - 1)) ]
        then
            basestring="$basestring\"${array[c]}\""
        else
            basestring="$basestring\"${array[c]}\","
        fi
    done
struct="{
    \"track\":[$basestring]
}"
elif [ "$2" = "follow" ]
then
    basestring=""
    for (( c=2; c<$len; c++ ))
    do
        if [ $c = $(($len - 1)) ]
        then
            basestring="$basestring\"${array[c]}\""
        else
            basestring="$basestring\"${array[c]}\","
        fi
    done
struct="{
    \"follow\":[$basestring]
}"
elif [ "$2" = "geo" ]
then
    basestring=""
    for (( c=2; c<$len; c++ ))
    do
        if [ $c = $(($len - 1)) ]
        then
            basestring="$basestring\"${array[c]}\""
        else
            basestring="$basestring\"${array[c]}\","
        fi
    done
struct="{
    \"geo\":[$basestring]
}"
fi

touch ~/filter_criteria/$1_fc.json

#create the file
cat > ~/filter_criteria/$1_fc.json << EOF1
$struct
EOF1