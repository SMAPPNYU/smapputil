#!/bin/bash

# *c http://code.tutsplus.com/tutorials/test-driving-shell-scripts--net-31487
# *c https://shunit2.googlecode.com/svn/trunk/source/2.1/doc/shunit2.html
# *c http://tldp.org/LDP/abs/html/testconstructs.html
# *c http://www.mikewright.me/blog/2013/10/31/shunit2-bash-testing/

function test_control_not_equal () {
    assertNotEquals "strings not equal" "!strings not equal"
}

function test_control_is_equal () {
    assertEquals "strings equal" "strings equal"
}


## call and run all sh tests
. "../bash_modules/shunit2-2.1.6/src/shunit2"
