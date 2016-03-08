#!/bin/bash

# imports
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
. $DIR/../tunnel_monitor.sh --source-only

function test_control_not_equal () {
    assertNotEquals "strings not equal" "!strings not equal"
}

function test_control_is_equal () {
    assertEquals "strings equal" "strings equal"
}

# call and run all sh tests
. "../../bash_modules/shunit2-2.1.6/src/shunit2"
