#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
. $DIR/tunnel_functions.sh --source-only

one=1
zero=0
count=0
# kill any roating tunnels parent processes that are running...
TUNNELPIDS=`ps aux | grep "hades_rotating_tunnel.sh" | grep -v "grep" | grep -v "kill_hades_rotating_tunnel.sh" | awk '{print $2}'`
echo "$TUNNELPIDS" 
for tunnelprocessid in $TUNNELPIDS
do
    #silently kill
    kill -13 $tunnelprocessid
    count=$((count + 1))
done
echo "killed $count rotating hades tunnels"

# kill potentially lingering sessions
res=$(kill_autossh $zero)
echo $res
secres=$(kill_autossh $one)
echo $secres

# author @yvan
# no* 'log' - keep out of this file.
