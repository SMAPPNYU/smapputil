#!/bin/bash

read pass
readonly one=1
listenport=40121

# imports
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
. $DIR/../tunnel_functions.sh --source-only

function test_control_not_equal () {
    assertNotEquals "strings not equal" "!strings not equal"
}

function test_control_is_equal () {
    assertEquals "strings equal" "strings equal"
}

function test_tunnel_functions () {
    # create hades tunnel in background
    # in a subshell
    ( create_hades_tunnel "$pass" "$one" "$listenport" ) &

    # sleep for 10 sec to give ssh time to connect
    sleep 10
    autosshpid='nil'
    autosshpid=`ps aux | \
    grep -E "sshpass -p .* autossh -M .* -N -L .*:hades$one.es.its.nyu.edu:.* .*@hpc.nyu.edu" | \
    grep -v "grep" | \
    awk '{print $2}'`

    # assert that the pid is not blank, process started    
    assertNotEquals "" "$autosshpid"


    # kill the session and assert that
    # 2 processes, sshpass and autossh
    # were directly killed, one extra child
    # port waching process will be killed
    # it will not appeasr in count
    count=$(kill_autossh $one 2>/dev/null)
    assertEquals 2 "$count"
}

# call and run all sh tests
. "../../bash_modules/shunit2-2.1.6/src/shunit2"
