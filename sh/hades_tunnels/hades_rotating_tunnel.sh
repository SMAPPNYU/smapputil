#!/bin/bash

read pass

# imports
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
. $DIR/../bash_modules/logger/logger.sh --source-only
. $DIR/tunnel_functions.sh --source-only

# setup constants and logging
readonly zero=0
readonly datetime=`date +"%a-%b-%d-%T-%Z-%Y"`
readonly scriptname=`basename "$0"`
readonly listenport=$1
setlogpath ~/shlogs/$scriptname-$datetime 

# set the autossh log to be a little chatty.
export AUTOSSH_LOGLEVEL=4
# log autossh to its own logfile.
touch ~/shlogs/autossh-$scriptname-$datetime
export AUTOSSH_LOGFILE=~/shlogs/autossh-$scriptname-$datetime
# try 10 times per autossh session run
# this is the max cycle we are willing to try
export AUTOSSH_MAXSTART=1

# handles what to do with the count.
handle_count () {
    # if counter is at max then reset it
    log "c $1"
    log "nodes count $2"
    if (( $1 >= ($2-1) ))
    then
        echo 0
    else
        echo $(($1+1))
    fi
}

# create an array with two values
# to add another hades node if one
# gets added, just add the node's
# number to this array

declare c=0
declare result=""
declare loginnodes=(0 1)

# we create a loop, and loop through an array with 0 or 1
# when one fails we kill the autossh session and we 
# try the next and then cycle and kill that autossh

while [  "$c" -lt "${#loginnodes[@]}" ]; do
    # try a first connect attempt
    log "trying autossh to hades$c.es.its.nyu.edu..."
    result=$(create_hades_tunnel $pass $c $listenport)

	# cleanup any old autossh processes
	# and their ssh children that may have lingered
	numkilled=$(kill_autossh $c)
    log "$numkilled tunnels needed to be cleaned up"

    #if autossh fails then log it and move on
    #zero is success so we make sure it's not 0
    # $1 is the result of an autossh call
	if (( $result != 0 ))
    then
        declare logdate=`date +"%a-%b-%d-%T-%Z-%Y"`
        log "the date is $logdate"
        log "result of connection attempt to hades$c.es.its.nyu.edu was: $result"
        log "could not setup ssh tunnel to hades$c.es.its.nyu.edu" 
        log "trying hades1.es.its.nyu.edu ..."
    fi

	#handle the count
	c=$(handle_count $c ${#loginnodes[@]})
done


# tdd*
# c* http://stackoverflow.com/questions/1405324/how-to-create-a-bash-script-to-check-the-ssh-connection
# c* http://stackoverflow.com/questions/4316730/linux-scripting-hiding-user-input-on-terminal
# c* http://stackoverflow.com/questions/22832933/what-does-stty-raw-echo-do-on-os-x
# c* http://stackoverflow.com/questions/12815774/importing-functions-from-a-shell-script
