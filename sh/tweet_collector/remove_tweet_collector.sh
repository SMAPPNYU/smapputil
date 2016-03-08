#!/bin/bash

#completely pemove a running tweet collector from the system
#leaves its oauth and filter criteria...
#maybe it could move them somewhere and then delete them from system

remove_tweet_collector () {
    #first locate and kill the tweet collector process with that id
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

    #and then remove the cron job from crontab
    #https://sudipta05.wordpress.com/linux/bashshell-script-tips/
    crontab -l | grep -v  $term | crontab -
}

if [ "${1}" != "--source-only" ]
then
    remove_tweet_collector $1
fi
