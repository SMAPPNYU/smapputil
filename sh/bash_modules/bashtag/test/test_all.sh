#!/bin/bash


# c* http://stackoverflow.com/questions/17743879/how-to-get-child-process-from-parent-process
# c* http://www.grymoire.com/Unix/Awk.html

function test_control_not_equal () {
    assertNotEquals "strings not equal" "!strings not equal"
}

function test_control_is_equal () {
    assertEquals "strings equal" "strings equal"
}

function test_start_bashtag_process () {
    # start a bashtag process
    bash ../bashtag.sh '../test/dummy.sh' 'test_start_bashtag_process' &

    # create a boolean and match the test_start_bashtag_process string in a running process
    declare matchedprocessid=`ps aux | grep "test_start_bashtag_process" | grep -v "grep" | awk '{print $2}'`

    # there should be one match and it should have the string test_start_bashtag_process inside it
    if [ "${#matchedprocessid[@]}" -eq 1 ] && [ "$matchedprocessid" ]
    then
        declare subchildpid=`pgrep -P "$matchedprocessid"`
        if [ "$subchildpid" ]
        then
            assertTrue ${SHUNIT_TRUE}
        fi
    else 
        fail
    fi
    #tearDown
    echo "tearing down..."
    pkill -f "test_start_bashtag_process" 
    pkill -f "../test/dummy.sh"
}

function test_kill_bashtag_process () {
    # start a bashtag process
    bash ../bashtag.sh '../test/dummy.sh' 'test_kill_bashtag_process' &
    # record pids of parent and child
    declare matchedprocessid=`ps aux | grep "test_kill_bashtag_process" | grep -v "grep" | awk '{print $2}'`
    declare subchildpid=`pgrep -P "$matchedprocessid"`
    declare matchedprocesspresent=`kill -0 "$matchedprocessid"` 
    declare subchildpidpresent=`kill -0 "$subchildpid"`
    # kill that process and its child
    bash ../bashtag.sh kill test_kill_bashtag_process &
    #now neither that process nor its child should be running
    if [ "$matchedprocesspresent" ] || [ "$subchildpidpresent"  ]
    then
        fail
    else
        assertTrue ${SHUNIT_TRUE}
    fi
    #tearDown
    pkill -f test_kill_bashtag_process
    pkill -f "dummy.sh"
}

# call and run all tests
. "../bash_modules/shunit2-2.1.6/src/shunit2"