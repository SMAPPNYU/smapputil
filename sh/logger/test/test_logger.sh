#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
. $DIR/../logger.sh --source-only

function test_control_not_equal () {
    assertNotEquals "strings not equal" "!strings not equal"
}

function test_control_is_equal () {
    assertEquals "strings equal" "strings equal"
}

function setUp () {
    if [ -f $1 ]
    then
        rm -f $1
    fi
}

function tearDown () {
    if [ -f $1 ]
    then
        rm -f $1
    fi
}

function test_logger () {
    declare tfile="$DIR/logtest.log"
    setUp $tfile
    setlogpath $tfile
    log "blah"
    while read -r line
    do
        assertEquals 'blah' $line
    done < "$tfile"
    tearDown $tfile
}

# call and run all sh tests
. "$DIR/../../bash_modules/shunit2-2.1.6/src/shunit2"