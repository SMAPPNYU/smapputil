#!/bin/bash

# note* needs to be run on a computer in the nyu network

readonly one=1
readonly zero=0

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
. $DIR/../kill_hades_tunnels.sh --source-only
. $DIR/../make_hades_tunnel.sh --source-only

function test_control_not_equal () {
    assertNotEquals "strings not equal" "!strings not equal"
}

function test_control_is_equal () {
    assertEquals "strings equal" "strings equal"
}

function test_original_hades_tunnels () {
    # make the tunnel
    ( make_hades_tunnel yns207 hades$one.es.its.nyu.edu $one ) &
    
    # check for the tunnel's existence
    tunnelpids=`ps aux | grep -E "ssh -fN -L .*:localhost:.* .*@hades$one.es.its.nyu.edu" | \
    grep -v "grep" | \
    awk '{print $2}'` 
    
    # assert that tunnelpids are not
    # empty
    assertNotEquals "testing tunnel pids should be non empty" "$zero" "${#tunnelpids[@]}"

    res=$(kill_hades_tunnels $one 2>/dev/null)
    assertNotEquals "should kill non zero # of processes" "$zero" "$res"
}

# call and run all sh tests
. "../../bash_modules/shunit2-2.1.6/src/shunit2"