#!/bin/bash

make_hades_tunnel () {
    ssh -fN -L 27017:hades$3.es.its.nyu.edu:27017 $1@$2
}

# if we don't just want the source execute the code
if [ "${1}" != "--source-only" ]
then
    make_hades_tunnel $1 $2 $3
fi

# tdd*
# c* http://stackoverflow.com/questions/12815774/importing-functions-from-a-shell-script
