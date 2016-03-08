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

# hades tunnel should have a keyed login setup
# into hades0.es.its.nyu.edu
function test_hadestunnel () {
    #setUp open the tunnel
    bash ../hadestunnel.sh yns207 hades0.es.its.nyu.edu
    #test search for the tunnel
    declare matchedtunnel=`ps aux | grep "ssh -fN -L 27017:localhost:27017 .*@hades0.es.its.nyu.edu" | grep -v "grep"` 
    if [ "$matchedtunnel" -a 'nc -z localhost 27017' ]
    then
        assertTrue ${SHUNIT_TRUE}
    else
        assertTrue ${SHUNIT_FALSE}
    fi

    #tearDown
    pkill -f "ssh -fN -L 27017:localhost:27017 yns207@hades0.es.its.nyu.edu"
}

function test_killhadestunnels () {
    #setUp hades tunnel
    bash ../hadestunnel.sh yns207 hades0.es.its.nyu.edu
    # kill the tunnels
    bash ../killhadestunnels.sh >/dev/null
    #no tunnels should be running
    if ps aux | grep "ssh -fN -L 27017:localhost:27017 .*@hades0.es.its.nyu.edu" | grep -v "grep"
    then
        assertTrue ${SHUNIT_FALSE}
    else
        assertTrue ${SHUNIT_TRUE}
    fi
}

function test_killtweetcollector () {
    # setuP
    # create 2 processes which has all the tweet collector keywords in it
    declare term="~~~~~~~~~~~JonSnowAzorAhai~~~~~~~~~~~~~"
    bash ./dummy.sh "tweet_collector.py $term" &
    # kill the mock collector processes
    bash ../killtweetcollector.sh "$term" >/dev/null
    # check that the mock processes are not there.
    if ps aux | grep "tweet_collector.py" | grep "$term" | grep -v "grep"
    then
        # kill processes that failed to be killed
        pkill -f ~~~~~~~~~~~JonSnowAzorAhai~~~~~~~~~~~~~
        assertTrue ${SHUNIT_FALSE}
    else
        assertTrue ${SHUNIT_TRUE}
    fi
}

function test_makefiltercriteria () {
    # setUp
    # create a test folder called filter_criteria
    # in the home directory if it don't exist
    mkdir -p ~/filter_criteria
    # try to make some filter criteria
    bash ../makefiltercriteria.sh shellscripttests track ipad socialist
    declare jsonarray=()
    # read the file and check that all the filter criteria are there
    while read -r line
    do
        jsonarray=("${jsonarray[@]}" "$line")
    done < ~/filter_criteria/shellscripttests_fc.json
    # check the json structure and fail if it isn't right
    if [ "${jsonarray[0]}" != "{" ]
    then
        fail
    elif [ "${jsonarray[1]}" != "\"track\":[\"ipad\",\"socialist\"]" ]
    then
        fail
    elif [ "${jsonarray[2]}" != "}" ]
    then
        fail
    else #otherwise the test succeeds if the format is right.
        assertTrue ${SHUNIT_TRUE}
    fi
    #tearDown
    rm ~/filter_criteria/shellscripttests_fc.json
}

function test_makeoauth () {
    # setUp
    # create a test oauth folder 
    mkdir -p ~/oauth
    # try to make an oauth file
    bash ../makeoauth.sh shellscripttests \
    kw8fRMjKAOtBvJawwugDESTLC \
    BThfBYc56pPQtLBxE9fTDxK3XClV83ScJM9539xgsNwsAunLLM \
    492864575-jOlLV0NZTit66kkoiqM8v499yoTa8ahkLMUBpBBh \
    LfXRbifrWvrqQNMU0vUvDDHfnGFa1WNNXnZzz7VdJNzEw
    declare jsonarray=()
    # read the file and make sure the oauth criteria are correct
    while read -r line
    do
        jsonarray=("${jsonarray[@]}" "$line")
    done < ~/oauth/shellscripttests.oauth.json
    # check the json structure
    if [ "${jsonarray[0]}" != "{" ]
    then
        fail
    elif [ "${jsonarray[1]}" != "\"consumer_key\": \"kw8fRMjKAOtBvJawwugDESTLC\"," ]
    then
        fail
    elif [ "${jsonarray[2]}" != "\"consumer_secret\": \"BThfBYc56pPQtLBxE9fTDxK3XClV83ScJM9539xgsNwsAunLLM\"," ]
    then
        fail
    elif [ "${jsonarray[3]}" != "\"access_token\": \"492864575-jOlLV0NZTit66kkoiqM8v499yoTa8ahkLMUBpBBh\"," ]
    then
        fail
    elif [ "${jsonarray[4]}" != "\"access_token_secret\": \"LfXRbifrWvrqQNMU0vUvDDHfnGFa1WNNXnZzz7VdJNzEw\"" ]
    then
        fail
    elif [ "${jsonarray[5]}" != "}" ]
    then
        fail
    else
        assertTrue ${SHUNIT_TRUE}
    fi
    # tearDown
    rm ~/oauth/shellscripttests.oauth.json
}

#heartbeatupdatelog method would have made more sense as a modular function you could
#put int the file names where you'd like to store stuff ,modularize later?
function test_heartbeatupdatelog () {
    #setUp
    declare originaltime=`date`
    #create a file that has an old entry in it, append if needed
    echo "test_heartbeatupdatelog $originaltime" >> ~/.collectorheartbeat.log
    sleep 1
    declare newtime=`date`

    #update the old entry with a new time
    bash ../heartbeatupdatelog.sh "test_heartbeatupdatelog" "$newtime"

    #read file for the new time to make sure it's right
    while read line
    do
        IFS=' ', read -a elementsinline <<< "$line"
        declare len=${#elementsinline[@]}
        declare basestring=""
        declare testname="test_heartbeatupdatelog"
        declare isnewline=false
        decalre shouldfail=false
        if [ "${elementsinline[0]}" = $'\n' ]
        then
            isnewline=true
        fi
        #if the 0th element is the servername
        if [ ! $isnewline ] && [ "${elementsinline[0]}" = "$testname" ]
        then
            # aggregate the remaining elements into a string
            declare aggregatetime=""
            for (( c=1; c<$len; c++ ))
            do
                aggregatetime="$aggregatetime ${array[c]}"
            done

            # check to see if the time looks like it was updated
            if [ "$aggregatetime" -eq "$newtime" ]
            then
                assertTrue ${SHUNIT_TRUE}
            else
                shouldfail=true
            fi
        fi
    done < ~/.collectorheartbeat.log

    if [ "$shouldfail" = true ]
    then
        fail
    fi

    #tearDown
    # delete lines containing test_heartbeatupdatelog
    # make a temp file
    cp ~/.collectorheartbeat.log ~/.collectorheartbeat.log.tmp
    # get rid of test lines
    sed '/test_heartbeatupdatelog/d' ~/.collectorheartbeat.log.tmp >~/.collectorheartbeat.log
    # remove the temp file
    rm ~/.collectorheartbeat.log.tmp
}

## call and run all sh tests
. "../bash_modules/shunit2-2.1.6/src/shunit2"
