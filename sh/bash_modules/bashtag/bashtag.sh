#!/bin/bash


# if the user is trying to kill a group of tagged processes
if [ "$1" == "kill" ]
then
    # get pids of parent
    declare parentpids=`ps aux | grep "$2" | grep -v "grep" | grep -v "bashtag.sh kill" | grep -v "bashtag kill" | awk '{print $2}'`
    echo "Parent ID: $parentpids"
    # for each selected pid get the group ids
    for pid in $parentpids
    do 
        for pgid in $(ps -o pgid= "$pid" | grep -o '[0-9]*')
        do
            echo "Killing Group ID: $pgid"
        done
        # kill all the group ids associated with '$pid'
        kill -- -$(ps -o pgid= "$pid" | grep -o '[0-9]*')
    done
# if the user is trying to start a process with a tag
# run the command as a subprocess
else
   eval $1 & 
fi

# c* http://stackoverflow.com/questions/13038143/how-to-get-pids-in-one-process-group-in-linux-os
# c* http://stackoverflow.com/questions/392022/best-way-to-kill-all-child-processes
# c* http://stackoverflow.com/questions/17290872/create-a-child-process-by-fork-a-parent-process-in-shell-script
# c* http://www.freebsd.org/cgi/man.cgi?query=ps&manpath=SuSE+Linux/i386+11.3
