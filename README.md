```
                                       _   _ _ 
 ___ _ __ ___   __ _ _ __  _ __  _   _| |_(_) |
/ __| '_ ` _ \ / _` | '_ \| '_ \| | | | __| | |
\__ \ | | | | | (_| | |_) | |_) | |_| | |_| | |
|___/_| |_| |_|\__,_| .__/| .__/ \__,_|\__|_|_|
                    |_|   |_|
```

⚙ smapputil that contains utility scripts in python, bash or javascript. Javascript run here will be of the variety node.js 5.0.0. Python is generally python 2.7.11 moving to python 3. Shellscript/bash is expected to be in bash 3.2. A lot of the code here are refined, modularized, improved versions of scripts that used to be in Sandbox and smappPy.

- [py](https://github.com/SMAPPNYU/smapputil#py)
    - [merge_bson](https://github.com/SMAPPNYU/smapputil#merge_bson)
    - [merge_json](https://github.com/SMAPPNYU/smapputil#merge_json)
    - [csv_to_json](https://github.com/SMAPPNYU/smapputil#csv_to_json)
    - [date_filter_bson](https://github.com/SMAPPNYU/smapputil#date_filter_bson)
    - [list_collections](https://github.com/SMAPPNYU/smapputil#list_collections)
    - [query_user_tweets](#query_user_tweets)
    - [query_search_tweets](#query_search_tweets)
    - [query_user_objects](#query_user_objects)
    - [query_user_friends](#query_user_friends)
    - [query_user_friends_ids](#query_user_friends_ids)
    - [query_tweet_distribution](#query_tweet_distribution)
    - [query_user_id_distribution](#query_user_id_distribution)
    - [query_user_follower_ids](#query_user_follower_ids)
    - [query_tweet_objects](#query_tweet_objects)
    - [transfer_collection](https://github.com/SMAPPNYU/smapputil#transfer_collection)
    - [ssh_tunnel](https://github.com/SMAPPNYU/smapputil#ssh_tunnel)
    - [rotating_tunnel](https://github.com/SMAPPNYU/smapputil#rotating_tunnel)
    - [mail_tweet_counts](https://github.com/SMAPPNYU/smapputil#mail_tweet_counts)
    - [username_id_convert](https://github.com/SMAPPNYU/smapputil#username_id_convert)
    - [dump_database](#dump_database)
    - [check_dump_integrity](#check_dump_integrity)
    - [make_tar](#make_tar)
- [pbs](#pbs)
    - [merge_dataset_files](#merge_dataset_files)
    - [make_sqlite_db](#make_sqlite_db)
- [sh](#sh)
    - [logger](#logger)

#environments

py2.7env.yml is for back compatibility and support only. in regular day to day you shold use the python 3 environment in py/environment.yml

#logging

Logging is required on all scripts. A few reasons:

1. Easier to spot and identify bugs while performing daily tasks
2. Easier to debug the immediate problem and deliver, bugs are never expected but they always happen.
3. By default the logs go into a folder path at ~/pylogs ~/shlogs or ~/jslogs with the name of the script and the date it was run.

I recommend creating these log folders in your home directory `pylogs` `jslogs` `shlogs`. Scripts with no logging will not be allowed into the repository.

mkdir ~/pylogs ~/jslogs ~/shlogs

That said you can specify whatever log path  you want. Just know that you must have one.

[Python Logging Example](https://github.com/SMAPPNYU/smapputilities/blob/master/py/merge_bson/merge_bson.py)

[Javascript Logging Software w/ Examples](https://github.com/trentm/node-bunyan)

[Bash Logging Example]() 

#tests

You must write tests for every function in every script. Whenever you add a new script you need to run your unit tests. Scripts with no tests will not be allowed into the repository. 

[Python Testing Framework (unittest)](http://docs.python-guide.org/en/latest/writing/tests/)

[Python Testing Tutorial](http://docs.python-guide.org/en/latest/writing/tests/)

[Bash Testing Framework (shunit2)](https://shunit2.googlecode.com/svn/trunk/source/2.1/doc/shunit2.html)

[Bash Testing Tutorial](https://wiki.umn.edu/UmmCSci3401f09/VerySimpleExampleOfShellScriptingAndTestingWithShunit2)

[Javascript Testing Framework/ Test Runner (mocha)](http://mochajs.org/)

[The co-wrapper for mocha](https://github.com/blakeembrey/co-mocha)

[The chai assertion library](http://chaijs.com/)

[Chai cheat sheet](http://ricostacruz.com/cheatsheets/chai.html)

[Javascript Testing Example](https://github.com/SMAPPNYU/smapputilities/blob/master/js/mailtweetcounts/test/test_mailtweetcounts.js)

#py

python utilities / scripts that do useful things. Built in python 2.7.X. To ru nthe python scripts I suggest activating the scriptsenv virtual environment with `source smapputil/bin/activate`. You should see a `(smapputil)` appear at the beginning of your consode prompt. (you can deactivate by typing `source deactivate` anytime)

environment.yml - for anaconda users to be able to create an environment easily, installs things from pip. to replicate the environment run `conda env create -f environment.yml` or simply `conda env create` in the `py` directory. [see this page.](http://conda.pydata.org/docs/using/envs.html#export-the-environment-file)
requirements.txt - a file containing dependencies smapputilities needs

#tests:

to test your scripts create a file called `test_NAME_OF_YOUR_SCRIPT.py` following the format of files like [test_date_filter.py](https://github.com/SMAPPNYU/smapputilities/blob/master/py/test/test_date_filter.py) then run `python test/test_NAME_OF_YOUR_SCRIPT.py`, not all scripts are tested, notably twitter queries, although that may change.

#resources:

[Python Unit Test Framework](https://docs.python.org/2/library/unittest.html#assert-methods)

[Adding imports to python sys path](http://askubuntu.com/questions/470982/how-to-add-a-python-module-to-syspath/471168)

#[merge_bson](https://github.com/SMAPPNYU/smapputilities/blob/master/py/merge_bson)

takes arbitrary number of bson files and merges them.

abstract:
```python
/path/to/scriptsvenv/bin/python merge_bson.py -i /path/to/bson1.bson /path/to/bson2.bson -o /path/to/output.bson -l /path/to/log.log
```

practical:
```python
python merge_bson.py -i ~/bson1.bson ~/bson2.bson -o ~/output.bson -l ~/log.log
# or if you want to ensure a unique field
python merge_bson.py -i ~/bson1.bson ~/bson2.bson -o ~/output.bson -l ~/log.log -f '_id'
```

*returns* a bson file that writes to disk in the output.

test: `python -m unittest test.test_merge_bson`

#[ssh_tunnel](https://github.com/SMAPPNYU/smapputil/tree/master/py/ssh_tunnel)

creates an ssh tunnel.

abstract:
```python
python py/ssh_tunnel/ssh_tunnel.py -lo LOGIN_HOST -u LOGIN_USERNAME -p LOGIN_PASSWORD -rh REMOTE_HOST -rp REMOTE_PORT -lh localhost -lp LOCAL_PORT
```

practical:
```python
python py/ssh_tunnel/ssh_tunnel.py -lo hpc.nyu.edu -u LOGIN_USERNAME -p LOGIN_PASSWORD -rh REMOTE_HOST -rp 27017 -lp 27017
# or w/ a keyed login
python py/ssh_tunnel/ssh_tunnel.py -lo hpc.nyu.edu -u LOGIN_USERNAME -rh REMOTE_HOST -rp 27017 -lp 27017
# or in a script
from ssh_tunnel import start_ssh_tunnel, stop_ssh_tunnel

ssh_tunnel.start_ssh_tunnel(args.loginhost, args.username, args.password, args.localhost, args.localport, args.remotehost, args.remoteport)
```

`-lh` is optional

*returns* an ssh tunnel

test: `python test/test_ssh_tunnel LOGIN_USER LOGIN_PASSWORD`


#[rotating_tunnel](https://github.com/SMAPPNYU/smapputil/tree/master/py/ssh_tunnel)

creates a keyed login only rotating tunnel. less general than ssh_tunnel, rotates the tunnels among
login nodes and remote ports provided in input. basically therer are two modes of use. 1. to create a single tunnel that 
goes through a bastion host to hades. 2. to create tunnels to hades on alternate login nodes, and then run a separate scripts that connect to those tunnels.

abstract:
```python
python py/ssh_tunnel/rotating_tunnel.py -op OPERATION -i /PATH/TO/TUNNEL/CONFIG.JSON -p LOCAL_BIND_PORT
```

practical:
```python
python py/ssh_tunnel/rotating_tunnel.py -op start -i ~/tunnel_config.json -p 49999
```

Use a screen daemon to start persistant rotating tunnels on smapp hosts:
```bash
screen -dmS rotating_tunnel ~/miniconda/envs/tunnel_env/bin/python ~/smapprepos/smapputil/py/ssh_tunnel/rotating_tunnel.py -op start -i ~/smappconfig/tunnel_config_alt.json -p 49999
```

*returns* a tunnel that maps your local port to a rotating set of remote ports and hosts

*input* a file that contains a set of login hosts and a set of remotehosts

```

{
    "loginhosts":[
        {
            "host":"host1",
            "user":"user1"
        },
        {
            "host":"host2",
            "user":"user2"
        }
    ],
    "remotehosts":[
        {
            "host":"host3",
            "port":port
        },
        {
            "host":"host4",
            "port":port
        }
    ],
    "altloginhosts":[
        {
            "host":"althost2",
            "user":"usr"
        },
        {
            "host":"althost1",
            "user":"usr"
        }
    ],
    "altremotehosts":[
        {
            "host":"localhost",
            "port":altport
        },
        {
            "host":"localhost",
            "port":altport
        }
    ]
}
```

`loginhosts` are the set of hosts you want your script to treat as logins

`remotehosts` is only the set of hosts you want login hosts to look at

`altloginhosts` is optional, are the set of hosts you want to try to login to after exhausting all loginhosts

`altremotehosts` is optional, is the set of alternate remote hosts you want to map to on the alt login hosts.

basically alt login and remote hosts are for making "double tunnels" to get where you need to go. you setup a tunnel on the login host, then you connect directly to the login host tunnel. this was the cleanest and easiest way to get a tunnel maker that alternated between different kinds of tunnels. the other ways make it very awkward to setup double tunnels.

note: if using the tunnel to connect to nyu bastion host contact the sys admin there to add your public keys to the authorized_hosts file for your account on that machine.

#[merge_json](https://github.com/SMAPPNYU/smapputilities/blob/master/py/merge_json)

merges two files where each file has a json object on each line, or each file i a list of json objects

abstract:
```python
python merge_json.py -i /path/to/json1.json /path/to/json2.json -o /path/to/output.json -l /path/to/log.log
```

practical:
```python
python merge_json.py -i ~/json1.json ~/json2.json -o ~/output.json -l ~/merge_json_log.log
# or if you want to ensure a unique field
python merge_json_unique.py -i ~/json1.json ~/json2.json -o ~/output.json -l ~/merge_json_log.log -f '_id'
# or with flags
python merge_json_unique.py -i ~/json1.json ~/json2.json -o ~/output.json -l ~/merge_json_log.log --jsonload --jsonlist
```

*returns* a json file that writes to disk with the original input files merged

test: `python -m unittest test.test_merge_json`

`--jsonload`: loads input files as entire json objects, not line by line (useful for a jsonlist input or file w/ one object spaced over multiple lines)

`--jsonlist`: outputs a json list instead of a json object on each line

#[csv_to_json](https://github.com/SMAPPNYU/smapputilities/tree/master/py/csv_to_json)

take a csv and make it into a json file or a json list

abstract:
```python
python csv_to_json.py -i /path/to/csv1.csv /path/to/csv2.json -o /path/to/output.json -l /path/to/log.log
```

practical:
```python
python csv_to_json.py -i ~/csv1.csv ~/csv2.csv -o ~/output.json -l ~/csv_to_json.log
# or if you want the output as a json list
python csv_to_json.py -i ~/csv1.csv ~/csv2.csv -o ~/output.json -l ~/csv_to_json.log --jsonlist
# or if you want to skip the header
python csv_to_json.py -i ~/csv1.csv ~/csv2.csv -o ~/output.json -l ~/csv_to_json.log --skipheader
```

*returns* a json file that has a json object on each line or it returns a json list file.

test: `python -m unittest test.test_csv_to_json`

`--skipheader`: skips the first line of every input file

`--jsonlist`: outputs a json list instead of a json object on each line

#[date_filter_bson](https://github.com/SMAPPNYU/smapputilities/blob/master/py/date_filter/date_filter_bson.py)

Uses the [smapp-toolkit](https://github.com/SMAPPNYU/smapp-toolkit) to filter by date.

Make sure to convert between UTC and EST (or wtvr time zone you're in). Use this [site.](http://www.wsanford.com/~wsanford/exo/TCT.html)

Ex:

`2016-01-17 09:00:00 PM EST` to `2016-01-17 11:00:00 PM PM EST`

goes to

`2016-01-18 02:00:00 AM UTC` to `2016-01-18 04:00:00 AM UTC`

Takes two date times of format `2016-01-19 09:47:00` and produces a new bson file filtered by the date we want. A quick trick is add 5 hours to new york time (eastern standard time) to get the right time/date in utc. Do not forget to roll over the day.

abstract:
```python
/path/to/scriptsvenv/bin/python date_filter_bson.py -i /path/to/bson1.bson -d1 '2016-01-18 02:00:00' -d2 '2016-01-18 04:00:00' -o /path/to/output.bson -l /path/to/log.log
```
practical:
```python
python date_filter_bson.py -i ~/bson1.bson -d1 '2016-01-18 02:00:00' -d2 '2016-01-18 04:00:00' -o ~/output.bson -l ~/log.log
```

`d1` the first date (applied via [since](https://github.com/SMAPPNYU/smapp-toolkit#since) in the smapp-toolkit)

`d2` the second date (applied via [until](https://github.com/SMAPPNYU/smapp-toolkit#until) in smapp-toolkit)

*returns* a bson file that writes to disk. Filtered by the dates given.

test: `python test/test_date_filter.py`

#[list_collections](https://github.com/SMAPPNYU/smapputilities/tree/master/py/list_collections)

a way to list the running collections on a machine by logging in and listing that machine's crontab, would be nice to add a name field to the script input and output files, would also be nice to have the number per machine running.

abrstact:
```python
/path/to/scripts/env/bin/python /path/to/list_collections.py -i ~/serverlist.csv -o ~/pylogs/collections.json 
```

practical:
```python
python ~/smapputilities/py/list_collections/list_collections.py -i ~/serverlist.json -o ~/pylogs/collections.json 
```

*inputs* a csv or json file that is a list of ip addresses or severnames

csv should look like so:
```txt
sever1,user1
server2,user2
```
json should look like:
```json
{
    'server_one': 'user_one',
    'server_two': 'user_two'
}
```

*returns* a json file with servernames as keys and a list of collections as the value for each key

note: logging is only used for errors and paramiko automatically taps into our logger.

note: make sure you have `~/pylogs` directory before running this script.

test: `python test/test_list_collections.py SERVER_IP_OR_NAME SERVER_USERNAME`

#[query_user_tweets](https://github.com/SMAPPNYU/smapputilities/blob/master/py/query_twitter/query_user_tweets.py)

take a list of users and get each of their 3200 most recent tweets. Works on the twitter api with tweepy.

abstract:
```python
/path/to/scriptsenv/bin/python query_user_tweets.py -i /path/to/input.json -o /path/to/output.json -a /path/to/auth.json -l /path/to/log.log
```

practical:
```python
python query_user_tweets.py -i ~/input.json -o ~/output.json -a ~/auth.json -l ~/log.log
```

*input* input is json or csv, csv must be a one column csv with `id` as the column:

```
id
12321323
12321312321
23232323
.
.
.
```

or a json list:
```
[
    'id_one',
    'id_two'
     .
     .
     .
]
```

*output* a json file that writes to disk, with the 3200 (or less) of a user's most recent tweets.

note: input is json or csv, csv must be a one column csv with `id` as the column, json is just a json list ['id_one', 'id_two']

note: `smapp_count` term added to each tweet object to tell you which count of a particular user's tweets you are looking at.

#[query_search_tweets](https://github.com/SMAPPNYU/smapputilities/blob/master/py/query_twitter/query_search_tweets.py)

queries the twitter search api for any list of terms.

abstract:
```python
/path/to/scriptsenv/bin/python query_search_tweets.py -i /path/to/input.json -o /path/to/output.json -a /path/to/auth.json -l /path/to/log.log
```

practical:
```python
python query_search_tweets.py -i ~/input.json -o ~/output.json -a ~/auth.json -l ~/log.log
```

*input* input is json or csv, csv must be a one column csv with `id` as the column:

```
term
dog
cat
germany
.
.
.
```

or a json list:
```
[
    'dog',
    'cat',
    'germany'
     .
     .
     .
]
```

*output* a json file that writes to disk with the resulting tweet objects in JSON format

note: fields `smapp_term` and `smapp_count` are added to each tweet object to tell you which term the tweet war queried for and what its count in the query was.

#[query_user_objects](https://github.com/SMAPPNYU/smapputilities/blob/master/py/query_twitter/query_user_objects.py)

queries the twitter api for any list of user objects. takes a list of twitter user ids as input.

abstract:
```python
/path/to/scriptsenv/bin/python query_user_objects.py -i /path/to/input.json -o /path/to/output.json -a /path/to/auth.json -l /path/to/log.log
```

practical:
```python
python query_user_objects.py -i ~/input.json -o ~/output.json -a ~/auth.json -l ~/log.log
```

input is json or csv, csv must be a one column csv with `id` as the column:
```
id
12321323
12321312321
23232323
.
.
.
```

or a json list:
```
[
    'id_one',
    'id_two'
     .
     .
     .
]
```
*output* a json file that writes to disk with the resulting user objects in JSON format

#[query_user_friends](https://github.com/SMAPPNYU/smapputilities/blob/master/py/query_twitter/query_user_friends.py)

queries the twitter api for  the 'friends' (users a userid follows) of a particular twitter user id 

abstract:
```python
/path/to/scriptsenv/bin/python query_user_friends.py -i /path/to/input.json -o /path/to/output.json -a /path/to/auth.json -l /path/to/log.log
```

practical:
```python
python query_user_friends.py -i ~/input.json -o ~/output.json -a ~/auth.json -l ~/log.log
```

*input* a one column csv with `id` as the coulmn name or a json list:

```
id
12321323
12321312321
23232323
.
.
.
```

or a json list:
```
[
    'id_one',
    'id_two'
     .
     .
     .
]
```

*output* a json file that writes to disk with the resulting user objects in JSON format

note:

a field `smapp_original_user_id` gets added to the user object that tells us what the original user used to query for that friend was.

#[query_user_friends_ids](https://github.com/SMAPPNYU/smapputilities/blob/master/py/query_twitter/query_user_friends_ids.py)

queries the twitter api for the ids of 'friends' (users a userid follows) of a particular twitter user id 

abstract:
```python
/path/to/scriptsenv/bin/python query_user_friends_ids.py -i /path/to/input.json -o /path/to/output.json -a /path/to/auth.json -l /path/to/log.log
```

practical:
```python
python query_user_friends_ids.py -i ~/input.json -o ~/output.json -a ~/auth.json -l ~/log.log
```

*input* input is json or csv, csv must be a one column csv with `id` as the column:

```
id
12321323
12321312321
23232323
.
.
.
```

or a json list:
```
[
    'id_one',
    'id_two'
     .
     .
     .
]
```

*output* a json file that writes to disk with the resulting user id objects in JSON format, fields on output are:

`smapp_original_user_id` - the id from the original list of input ids

`id` - the twitter id returned by twitter, the id of a follower or friend of the original id

note:

a field `smapp_original_user_id` gets added to the user object that tells us what the original user used to query for that friend was.

#[query_tweet_distribution](https://github.com/SMAPPNYU/smapputil/blob/master/py/query_twitter/query_tweet_distribution.py)

checks a dumped file with a tweet json object on each line to and returns a count file the count file tells us how many tweets there are for each user id in the tweet file. (if all 0 or all the same the query should probably be investigated, logs checked, rerun)

abstract:
```bash
/path/to/scriptsenv/bin/python query_tweet_distribution.py -i INPUT_TWEETS_FILE -o OUTPUT_COUNTS_FILE
```

practical:
```bash
python py/query_twitter/query_tweet_distribution.py -i ~/smappwork/temp/joanna-user-tweets-1st-10k.json -o ~/smappwork/temp/joanna_dist_test.csv
```

*input* a file with a tweet object on each line (AKA a [JsonCollection](https://github.com/SMAPPNYU/smappdragon#json_collection)) like so:

```
{"text": "blah", "user":{"id_str":"44343432"}, etc, more fields}
{"text": "doggy", "user":{"id_str":"5332277"}, etc, more fields}
```

*output* a count file with the user id and the number of tweets by that user id in the jsoncollection/tweetfile:

```
id,smapp_queried_tweet_count
593292175,391
287235831,549
218820163,232
575384734,2958
368743969,908
1669189994,216
.
.
.
average_per_user,1342.0117647058823
all_users_total,80606331
```
fields on output are:

`id` - the original twitter id whose friends, followers, or related ids were queried

#[query_user_id_distribution](https://github.com/SMAPPNYU/smapputil/blob/master/py/query_twitter/query_user_id_distribution.py)

checks a dumped file with a tweet json object on each line to and returns a count file the count file tells us how many ids there are for each original user id in the tweet file. (if all 0 or all the same,i.e. every user has 250 followers/friends the query should probably be investigated, logs checked, rerun)

abstract:
```bash
/path/to/scriptsenv/bin/python query_user_id_distribution.py -i INPUT_ID_LIST_FILE -o OUTPUT_COUNTS_FILE
```

practical:
```bash
python py/query_twitter/query_user_id_distribution.py -i ~/smappwork/temp/EgyptGeo_and_Egypt_users_merged_friends_ids_output.json -o ~/smappwork/temp/id_distribution.csv
```

*input* a file with a json object on each line, containing at least fields `'id'` and `'smapp_original_user_id'` like so:

```
{"id": 216289357, "smapp_original_user_id": "2655698902"}
{"id": 19923144, "smapp_original_user_id": "2655698902"}
```

*output* a count file with the user id and the number of ids for each original id in the file:

```
id,smapp_queried_id_count
593292175,391
287235831,549
218820163,232
575384734,2958
368743969,908
1669189994,216
.
.
.
average_per_user,1342.0117647058823
all_users_total,80606331
```

fields on output are:

`id` - the original twitter id for a user whose tweets were queried

#[query_user_follower_ids](https://github.com/SMAPPNYU/smapputil/blob/master/py/query_twitter/query_user_follower_ids.py)

takes a list of user ids and returns a file with the followers of each id listed in the file.

abstract:
```
/path/to/scriptsenv/bin/python query_user_follower_ids.py -i PATH_TO_INPUT -o PATH_TO_OUTPUT -a PATH_TO_AUTH_POOL
```

practical:
```
python ~/smapprepos/smapputil/py/query_twitter/query_user_follower_ids.py -i ~/smappwork/data/egypt_secular_elites.csv -o ~/smappwork/data/egypt_secular_elites_follower_ids_output.json -a ~/pool.json
```

*input* a json or csv, must be a one column csv with `id` as the column:

```
id
12321323
12321312321
23232323
.
.
.
```

or a json list:
```
[
    'id_one',
    'id_two'
     .
     .
     .
]
```

*output* a json file where each lin etakes the form `{"id": 750640012102864896, "smapp_original_user_id": "443789042"}`, fields on output are:

`id` - the twitter id from the list of ids

`smapp_original_user_id` - the id sent to twitter to get this id

for example if yo uwanted the friends of user id '12344333' `id` fields would be their friends and `smapp_original_user_id` fields would be '12344333'

note:

a field `smapp_original_user_id` gets added to the id object that tells us what the original user used to query for that follower was

#[query_tweet_objects](https://github.com/SMAPPNYU/smapputil/blob/master/py/query_twitter/query_tweet_objects.py)

takes a list of tweet ids and returns full tweet objects, the number of inputs should equal the numer of outputs

abstract:
```
/path/to/scriptsenv/bin/python query_tweet_objects.py -i PATH_TO_INPUT -o PATH_TO_OUTPUT -a PATH_TO_AUTH_POOL
```

practical:
```
python ~/smapprepos/smapputil/py/query_twitter/query_tweet_objects.py -i ~/smappwork/data/tweet_ids.csv -o ~/smappwork/data/output_tweets.json -a ~/pool.json
```

*output* a json file with a json object on each line, each json object is a tweet.

#[transfer_collection](https://github.com/SMAPPNYU/smapputilities/tree/master/py/transfer_collection)

*warning* bulk inserts will create a surge of pending deletes on a sharded mongo cluster. this will stop shards from rebalancing properly and they will have to be stepped down or reset.

transfers a smapp tweet collection from one db to another. updating all necessary metadata documents.

abstract:
```python
/path/to/scripts/env/bin/python /path/to/transfer_collection.py -s SOURCE_HOST -p SOURCE_HOST_PORT -u SOURCE_USERNAME -w SOURCE_USER_PASSOWRD -d SOURCE_DB_NAME -ts TARGET_HOST -tp TARGET_HOST_PORT -tu TARGET_USERNAME -tw TARGET_USER_PASSWORD -td TARGET_DB_NAME -au AUTHENTICATION_USER -aw AUTHENTICATION_USER_PASSWORD -adb AUTHENTICATION_DATABASE
```

practical:
```python
~/pyenvs/bin/python ~/smapputilities/py/transfer_collection/transfer_collection.py -s localhost -p 27017 -u db_user -w supersecret_pwd -d germany_election -ts foreign.host.org -tp 27017 -tu foreign_usr -tw foreign_usr_secret_pwd5 -td new_germany_election -au auth_user_Admin_of_some_kind -aw super_secret_yo -adb admin
```

*returns* nothing but instead transfers data fro one running mongo instance to another

note: requires at least mongo 3.0

#[mail_tweet_counts](https://github.com/SMAPPNYU/smapputilities/tree/master/py/mail_tweet_counts)

mails tweet counts daily from our db

abstract:
```python
python py/mail_tweet_counts/mail_tweet_counts.py -ho HOSTNAME -p PORT
```

practical:
```python
python py/mail_tweet_counts/mail_tweet_counts.py -ho localhost -p 27017
```

*returns* an email to the specified address with the tweet counts in the db.

needs config.py that looks like so in mail_tweet_counts dir:

```
config = \
{ \
    'ignore_dbs': ['admin', 'config', 'test', 'EgyptToleranceUsersNetworks', 'OWSUsers', 'FilterCriteriaAdmin'], \
    'ignore_collections':['tweets_limits', 'tweets_filter_criteria', 'system.indexes', 'smapp_metadata', 'tweets_deletes'], \
    'mail': {
        'toemail': 'email',
        'gmailuser': 'smappmonitor@gmail.com', \
        'gmailpass': 'PWD' \
    } \
}
```

#[username_id_convert](https://github.com/SMAPPNYU/smapputilities/tree/master/py/username_id_convert)

convert twitter ids to usernames and vice versa.

abstract:
```python
python py/username_id_convert/username_id_convert.py -op OPERATION -i PATH/TO/INPUT.JSON -o PATH/TO/OUTPUT.json -a PATH/TO/OAUTH.json
```

practical:
```python
python py/username_id_convert/username_id_convert.py -op users_ids -i py/test/test_handles.csv -o ~/pylogs/username_id_convert_output_2.json -a ~/misc/oauthpools/pool.json
```

OPERATION - ids_users, users_ids

*returns* a json file with a json object on each line.

takes a json 
```
[
22997097, 14281853, 20686582, 19977542
]
```


or csv input:

```
screen_name
yvanscher
Jonathan_Nagler
j_a_tucker
RichBonneauNYU
```

#[dump_database](https://github.com/SMAPPNYU/smapputilities/tree/master/py/archive_tools)

mongodumps a list of dbs fo a specified place

abstract:
```python
python py/archive_tools/dump_database.py -i PATH_TO_INPUT_JSON -ho DB_HOSTNAME_OR_IP -p DB_HOST_PORT -u DB_USERNAME -w DB_PASSWORD -o PATH_TO_OUTPUT_DIR

python py/archive_tools/dump_database.py -i DB_NAME1 DB_NAME2 ... -ho DB_HOSTNAME_OR_IP -p DB_HOST_PORT -u DB_USERNAME -w DB_PASSWORD -o PATH_TO_OUTPUT_DIR
```

practical:
```python
python py/archive_tools/dump_database.py -i ~/pylogs/dump_dbs_input.json -ho 100.100.100.100 -p 27017 -u some_db_user -w some_db_password -o ~/dumps/ &>/dev/null

python py/archive_tools/dump_database.py -i germany_election mike_brown -ho localhost -p 49999 -u some_db_user -w some_db_password -o ~/dumps/ --querydump
```

-i should provide names corresponding to mongo databases

-i with `DB_NAME1 DB_NAME2 ...` directly takes the db names separated by spaces

-i with `PATH_TO_DUMPS_INPUT_JSON` takes a path to json file with a list of db names:
```
[
"germany_election", "mike_brown", "blah" 
]
```

-ho `DB_HOSTNAME_OR_IP` and -p `DB_HOST_PORT` is the hostname or ip of the remote host running the mongodb instance, and the remote port that mongodb is running on. Otherwise, if using a tunnel to the remote host, localhost and the local port that is mapped to the remote host's mongodb port.

-o `PATH_TO_OUTPUT_DIR` - is a path to a directory that wll contain a directory named after the database that will contain the dump

-q `--querydump` dumps the database collections to json by querying mongodb using smappdragon's MongoCollection and dump_to_json tools, the idea is taht sometimes mongodump doesnt work that great, it has issues where it misses data in the db, queries are more likely to return data

`&>/dev/null` - runs the script quietly instaed of printing mongodumps output

*returns* a series of running mongodump processes that dump the specified databases

takes a json input
```
[
"germany_election", "mike_brown", "blah" 
]
```

#[check_dump_integrity](https://github.com/SMAPPNYU/smapputilities/tree/master/py/archive_tools)

Checks whether one or more mongo databases from [dump_database](#dump_database) were dumped successfully at a specified location. Dumps can be in .bson or .json format.

abstract:
```python
python check_dump_integrity.py -i PATH_TO_DUMPS_INPUT_JSON -d PATH_TO_DUMPS_DIRECTORY -ho DB_HOSTNAME_OR_IP -p DB_HOST_PORT -u DB_USERNAME -w DB_PASSWORD 

python check_dump_integrity.py -i DUMP_NAME1 DUMP_NAME2 ... -d PATH_TO_DUMPS_DIRECTORY -ho DB_HOSTNAME_OR_IP -p DB_HOST_PORT -u DB_USERNAME -w DB_PASSWORD
```

practical:
```python
python check_dump_integrity.py -i ~/smappconfig/dump_dbs_input.json -d ~/dumps/ -ho 100.100.100.100 -p 27017 -u some_db_user -w some_db_password

python check_dump_integrity.py -i US_Mass_Protests Iran_Deal_2015 -d ~/dumps/ -ho localhost -p 49999 -u some_db_user -w some_db_password
```

-i should provide names of dumps that have corresponding mongo databases of the same name

-i with `DUMP_NAME1 DUMP_NAME2 ...` directly takes the dump names separated by spaces

-i with `PATH_TO_DUMPS_INPUT_JSON` takes a path to json file with a list of dump names:
```
[
"US_Mass_Protests", "Iran_Deal_2015", "blah" 
]
```

-d `PATH_TO_DUMPS_DIRECTORY` is the path to the directory containing the dumps, not the path to a dump itself. If you want to check the integrity of a dump located at ~/dumps/US_Mass_Protests, then you would pass in `-d ~/dumps/`. Likewise, if you want to check the integrity of multiple dumps like ~/dumps/US_Mass_Protests and ~/dumps/Iran_Deal_2015, you would also pass in `-d ~/dumps/`.

-ho `DB_HOSTNAME_OR_IP` and -p `DB_HOST_PORT` is the hostname or ip of the remote host running the mongodb instance, and the remote port that mongodb is running on. Otherwise, if using a tunnel to the remote host, localhost and the local port that is mapped to the remote host's mongodb port.

-u `DB_USERNAME` and -w `DB_PASSWORD`. If checking one dump, these must be the user credentials for the mongo database corresponding to that dump. E.g. If checking the ~/dumps/US_Mass_Protests dump, the user credentials must be for the US_Mass_Protests mongo database. If checking more than one dump, they must be credentials for an admin user with readall permissions for all mongo databases.

*returns* 

Reports to terminal and log file whether or not the dumps are missing any collections or documents.
Report provides separate sections for each dump input.

Report sections are of the form:

```
******************************
*   USElection2016_DTrumps   *
******************************

DUMP FOR USElection2016_DTrumps IS OK ON COLLECTIONS. Number of collections in database: 2, Number of collections dumped: 2

Counting number of documents in USElection2016_DTrumps database
Database USElection2016_DTrumps tweets_1 document count: 6000000
Database USElection2016_DTrumps tweets_2 document count: 3000000

Counting number of documents in USElection2016_DTrumps dump
Dump USElection2016_DTrumps tweets_1.bson document count: 6000000 (Missing 0, 0.00%)
Dump USElection2016_DTrumps tweets_2.bson document count: 2800000 (Missing 200000, 6.67%)

DUMP FOR USElection2016_DTrumps IS MISSING DOCUMENTS. Total documents in database: 9000000, Total documents dumped: 8800000 (Missing 200000, 2.27%)

Collections Missing Documents: ['tweets_2']

```

#[make_tar](https://github.com/SMAPPNYU/smapputilities/tree/master/py/archive_tools)

makes multiple tar file from a list of input files and makes a separate tar for each file

abstract:
```python
python py/archive_tools/make_tar.py -i INPUT_FILES_LIST -o PATH_TO_OUTPUT_DIRECTORY
```

practical:
```python
python py/archive_tools/make_tar.py -i file1.bson germany_election_2013/ tweets_3.bson -o ~/archives/
```

`PATH_TO_OUTPUT_DIRECTORY` - is a directory where all the archives will go to.

*returns* a .tar.gz file on disk for each input file or folder

#transform_dataset_to_pre

#pbs

job files to run on the cluster, see [nyu hpc wiki](https://wikis.nyu.edu/display/NYUHPC/Running+jobs)

quick overview:

qsub - submit a job

qstat -u mynetid -> check the status of my jobs, C (complete), Q(wiaiting to be processed), R (running), T (terminated and didnt complete)

qdel myjobid -> delete or cancel the job

practical:
```sh
qsub name_of_pbs_job_file.pbs
# or if its a cront job
/share/apps/admins/torque/qsub.sh /path/to/pbs_job_file.pbs
```

#merge_dataset_files

`merge_dataset_files_nix.pbs.sh` (for the cluster), `merge_dataset_files_osx.pbs.sh` (for personal use), a job file that will merge unzip and merge json file of a dataset, the two scripts differ in their use of date, as its different on osx and linux/*nix

abstract:
```sh
qsub merge_dataset_files.pbs /path/to/data/folder /path/to/output/file startdate enddate
```
pratical:
```sh
# run the job, getting data files from nov 8 2016 to nov 10 2016
qsub merge_dataset_files.pbs /archive/smapp/olympus/germany_elec_2016/data/
/scratch/mynetid560/germany_elec_merged.json.bz2 11_08_2016 11_10_2016
```

then in `/scratch/mynetid560/` you will find the merged file, `germany_elec_merged.json.bz2`

note: one alternative is to just bzip2 -d /scratch/mynetid560/germany_elec_2016/data/*.bz2 and then jsut use cat or [merge_json](#merge_json) as a job to merge the dataset.

note: if you omit startdate and enddate it get all the data files that have been bzipped (.bz2 files)

note: if you want several discreet dates you can easily merge them with:
```sh
cat file1.json.bz2 file2.json.bz2 > /scratch/mynetid560/merged_file.json.bz2
```

#make_sqlite_db

*not done*

make an sqlite database from a .json file, using json1 to make it behave like a document store see the [mini guide here](https://github.com/SMAPPNYU/smapphowto/blob/master/howto_get_going_with_sqlite_json1.md). you can see sqlite docs for json1 and what you can do with [sqlite json1 docs here](https://www.sqlite.org/json1.html). check out some pointers on how to do it in R [here](http://stackoverflow.com/questions/18107336/load-spatialite-extension-in-rsqlite-crashes-r-os-x-ubuntu) and check out the [RSQLite](https://cran.r-project.org/web/packages/RSQLite/index.html).

abstract:
```sh
qsub make_sqlite_db.pbs -i /path/to/data_file.json
```

practical:
```sh
qsub make_sqlite_db.pbs -i /scratch/mynetid560/germany_elec_2016/data/germany_elec_2016_merged_all_data.json
```

after its done you should find a file called something like `germany_elec_2016_data_json1.db` (its a .db file). this is your sqlite database, copy it, back it up, build indexes on it. do whatever you want to it.

#sh 

bash utilities / scripts that do useful thngs. Built in bash 3.2.X. You may notice many of the scripts are clones of scripts in [shellscripts repo](https://github.com/SMAPPNYU/shellscripts). This is temporary. Their final reting place will be here. The difference will be modularized testing, modularized scripts, each script will get its own tests (instead of the single file), the tests will be unit tests and as little as porrible system state tests, etc. As soon as the move is done and we're sure these scripts work we will phase out shellscripts repo (it was originally an experiment and we're going to wrangle it under control now before it becomes a legacy).

#testing:

[Download the shunit2 framework](https://storage.googleapis.com/google-code-archive-downloads/v2/code.google.com/shunit2/shunit2-2.1.6.tgz), put it in `sh/bash_modules`. Go into the `smapputilities/sh/test` folder using `cd test` and run `bash test_*.sh` this should run a series of shunit2 tests. You should only run tests on a system that isn't running any hades tunnels currently.

For now check out the [shellscripts repository](https://github.com/SMAPPNYU/shellscripts).

For bash testing we could try to use [maybe] (https://github.com/p-e-w/maybe) with the bash [`test` builtin](http://www.gnu.org/software/bash/manual/html_node/Bourne-Shell-Builtins.html#Bourne-Shell-Builtins).

i know that testing with bash is hard and can be very sketchy. just do your best to modularize the code and test each piece that is important.

#logging:

you'll want to import the logger into your bash script:

```bash
source "/Users/yvan/smapprepos/smapputilities/sh/hades_tunnels/bash_modules/logger.sh" --source-only
```

and then use it like so:
```bash
log "blah"
log "blah $c"
```

#resources:

[run a bash program in the back ground] (http://stackoverflow.com/questions/13676457/how-can-i-put-the-current-running-linux-process-in-background)

[bash docs / reference](http://tldp.org/HOWTO/Bash-Prog-Intro-HOWTO.html#toc7)

[how to write a for loop in bash](http://tldp.org/HOWTO/Bash-Prog-Intro-HOWTO-7.html)

[bash exit codes](http://www.tldp.org/LDP/abs/html/exitcodes.html)

#[logger](https://github.com/SMAPPNYU/smapputilities/tree/master/sh/logger)

this is a logger that can log output to a file, written in bash.

abstract:
```sh
# in your bash script write
setlogpath /path/to/your/log/file
log "LOG_TEXT"
```

practical:
```sh
# in your bash script write
readonly datetime=`date +"%a-%b-%d-%T-%Z-%Y"`
readonly scriptname=`basename "$0"`
setlogpath ~/shlogs/$scriptname-$datetime
log "hey it works, nvm, error, error, oh man this is baaadddd"
```

*returns* the ability to log in your bash script mad easily

test: `bash sh/logger/test/test_logger.sh`

#author

[yvan](https://github.com/yvan)
