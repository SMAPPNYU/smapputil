#!/bin/bash

# creates a tunnel to hades given inputs
# return the result
create_hades_tunnel () {
    sshpass -p $1 autossh -M $3 -N -L 27017:hades$2.es.its.nyu.edu:27017 yns207@hpc.nyu.edu
    echo "$?"
}

# really just a precaution method
# to clear out old sessions if they linger
kill_autossh () {
    # first kill the auto ssh running with sshpass
    count=0
    TUNNELPIDS=`ps aux | grep -E "sshpass -p .* autossh -M .* -N -L .*:hades$1.es.its.nyu.edu:.* .*@hpc.nyu.edu" | grep -v "grep" | awk '{print $2}'` 
    for tunnelprocessid in $TUNNELPIDS
    do
        #silently kill
        kill -13 $tunnelprocessid
        count=$((count + 1))
    done
    # then kill the watcher autossh
    # this should automatically kill the tunnel
    # kill old tunnel sessions
    TUNNELPIDS=`ps aux | grep -E "autossh -M .* -N -L .*:hades$1.es.its.nyu.edu:.* .*@hpc.nyu.edu" | grep -v "grep" | grep -v "sshpass" | awk '{print $2}'` 
    for tunnelprocessid in $TUNNELPIDS
    do
        #silently kill
        kill -13 $tunnelprocessid
        count=$((count + 1))
    done
    echo $count
}

:'
no* 'log' - keep out of this file.
'