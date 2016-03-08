#!/bin/bash

# script takes an exising collcetion and redirects 
# tweets into a new db.

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
. $DIR/../bash_modules/logger/logger.sh --source-only
. $DIR/remove_tweet_collector.sh --source-only

# change filter criteria to the new ones
mv ~/filter_criteria/$1_fc.json ~/filter_criteria/$2_fc.json
mv ~/oauth/$1.oauth.json ~/oauth/$2.oauth.json 

# kill process and delete crontab entry
remove_tweet_collector $1

# create the collection
~/.venvs/collector/bin/python ~/TweetCollector/start_new_collection.py -s localhost -p 27017 -u $3 -w $4 -f ~/filter_criteria/$2_fc.json -o ~/oauth/$2.oauth.json -d $2 --shard