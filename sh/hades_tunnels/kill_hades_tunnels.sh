#!/bin/bash

kill_hades_tunnels () {
    #kill old tunnel sessions
    count=0
    TUNNELPIDS=`ps aux | grep -E "ssh -fN -L .*:hades.*.es.its.nyu.edu:.* .*@hades$1.es.its.nyu.edu" | grep -v "grep" | awk '{print $2}'` 
    for tunnelprocessid in $TUNNELPIDS
    do
        kill -13 $tunnelprocessid
        count=$((count + 1))
    done
    echo "Found $count hadestunnel sessions to kill"
}

if [ "${1}" != "--source-only" ]
then
    kill_hades_tunnels
fi

: '
no* 'log' - keep out of this file. 
c* http://stackoverflow.com/questions/12815774/importing-functions-from-a-shell-script
'