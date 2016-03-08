#!/bin/bash

#only remove the running tweetcollector process will
#start up again in the next hour via the crontab
#first locate and kill the tweet collector process with that id

stop_tweet_collector () {
    count=0
    term=$1
    procs=`ps aux | grep "tweet_collector.py" | grep "$term" | grep -v "grep"| awk '{print $2}'`
    echo "Killing TweetCollectors at `date`"
    echo "PIDs:"
    echo "$procs"
    for p in $procs
    do
        echo "killing $p"
        kill $p
        count=$((count + 1))
    done
    echo "Killed $count processes!"
}

if [ "${1}" != "--source-only" ]
then
    stop_tweet_collector $1
fi
