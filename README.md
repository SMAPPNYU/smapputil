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
    - [merge_bson](#merge_bson)
    - [merge_json](#merge_json)
    - [merge_dataset_files](#merge_dataset_files)
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
    - [generate_random_twitter_potential_ids](#generate_random_twitter_potential_ids)
    - [transfer_collection](https://github.com/SMAPPNYU/smapputil#transfer_collection)
    - [ssh_tunnel](https://github.com/SMAPPNYU/smapputil#ssh_tunnel)
    - [rotating_tunnel](https://github.com/SMAPPNYU/smapputil#rotating_tunnel)
    - [mail_tweet_counts](https://github.com/SMAPPNYU/smapputil#mail_tweet_counts)
    - [username_id_convert](https://github.com/SMAPPNYU/smapputil#username_id_convert)
    - [dump_database](#dump_database)
    - [check_dump_integrity](#check_dump_integrity)
    - [make_tar](#make_tar)
    - [make_sqlite_db](#make_sqlite_db)
    - [launch_pbs_job](#launch_pbs_job)
    - [launch_parallel_pbs_jobs](#launch_parallel_pbs_jobs)
    - [launch_sbatch_job](#launch_sbatch_job)
    - [launch_parallel_sbatch_jobs](#launch_parallel_sbatch_jobs)
    - [olympus2scratch](#olympus2scratch)
- [pbs](#pbs)
    - [pbs_merge_dataset_files](#pbs_merge_dataset_files)
- [sbatch](#sbatch)
    - [cpu-jupyter](#cpu-jupyter)
    - [gpu-jupyter](#gpu-jupyter)
    - [olympus2scratch_ex](#olympus2scratch_ex)
    - [set_olympus_permissions](#set_olympus_permissions)
- [nbs](#nbs)
    - [olympus2scratch](https://github.com/SMAPPNYU/smapputil/blob/master/nbs/olympus2scratch.ipynb)
- [sh](#sh)
    - [logger](#logger)
    - [interactive_prince](#interactive_prince)
    - [term_search](#term_search)

# environments

py2.7env.yml is for back compatibility and support only. in regular day to day you shold use the python 3 environment in py/environment.yml

# logging

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

# tests

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

# py

python utilities / scripts that do useful things. Built in python 2.7.X. To ru nthe python scripts I suggest activating the scriptsenv virtual environment with `source smapputil/bin/activate`. You should see a `(smapputil)` appear at the beginning of your consode prompt. (you can deactivate by typing `source deactivate` anytime)

environment.yml - for anaconda users to be able to create an environment easily, installs things from pip. to replicate the environment run `conda env create -f environment.yml` or simply `conda env create` in the `py` directory. [see this page.](http://conda.pydata.org/docs/using/envs.html#export-the-environment-file)
requirements.txt - a file containing dependencies smapputilities needs

## tests

to test your scripts create a file called `test_NAME_OF_YOUR_SCRIPT.py` following the format of files like [test_date_filter.py](https://github.com/SMAPPNYU/smapputilities/blob/master/py/test/test_date_filter.py) then run `python test/test_NAME_OF_YOUR_SCRIPT.py`, not all scripts are tested, notably twitter queries, although that may change.

## resources

[Python Unit Test Framework](https://docs.python.org/2/library/unittest.html#assert-methods)

[Adding imports to python sys path](http://askubuntu.com/questions/470982/how-to-add-a-python-module-to-syspath/471168)

## [merge_bson](https://github.com/SMAPPNYU/smapputilities/blob/master/py/merge_bson)

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

## [ssh_tunnel](https://github.com/SMAPPNYU/smapputil/tree/master/py/ssh_tunnel)

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


## [rotating_tunnel](https://github.com/SMAPPNYU/smapputil/tree/master/py/ssh_tunnel)

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

## [merge_json](https://github.com/SMAPPNYU/smapputilities/blob/master/py/merge_json)

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

## [csv_to_json](https://github.com/SMAPPNYU/smapputilities/tree/master/py/csv_to_json)

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

## merge_dataset_files

merges files in a dataset of .json.bz2 files

abstract:
```
python merge_dataset_files.py -i file1.json.bz2 file2.json.bz2 -o merged.json
```

practical:
```
python merge_dataset_files.py -i vp_debate_2016_1_data__10_04_2016__00_00_00__23_59_59.json.bz2 vp_debate_2016_1_data__10_05_2016__00_00_00__23_59_59.json.bz2 -o vp_debate_2016_1_data__merged.json
```

*returns* a new merged file from the input files

## [date_filter_bson](https://github.com/SMAPPNYU/smapputilities/blob/master/py/date_filter/date_filter_bson.py)

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

## [list_collections](https://github.com/SMAPPNYU/smapputilities/tree/master/py/list_collections)

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

## [query_user_tweets](https://github.com/SMAPPNYU/smapputilities/blob/master/py/query_twitter/query_user_tweets.py)

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

## [query_search_tweets](https://github.com/SMAPPNYU/smapputilities/blob/master/py/query_twitter/query_search_tweets.py)

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

## [query_user_objects](https://github.com/SMAPPNYU/smapputilities/blob/master/py/query_twitter/query_user_objects.py)

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

## [query_user_friends](https://github.com/SMAPPNYU/smapputilities/blob/master/py/query_twitter/query_user_friends.py)

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

## [query_user_friends_ids](https://github.com/SMAPPNYU/smapputilities/blob/master/py/query_twitter/query_user_friends_ids.py)

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

## [query_tweet_distribution](https://github.com/SMAPPNYU/smapputil/blob/master/py/query_twitter/query_tweet_distribution.py)

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

## [query_user_id_distribution](https://github.com/SMAPPNYU/smapputil/blob/master/py/query_twitter/query_user_id_distribution.py)

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

## [query_user_follower_ids](https://github.com/SMAPPNYU/smapputil/blob/master/py/query_twitter/query_user_follower_ids.py)

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

## [query_tweet_objects](https://github.com/SMAPPNYU/smapputil/blob/master/py/query_twitter/query_tweet_objects.py)

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

## [generate_random_twitter_potential_ids](https://github.com/SMAPPNYU/smapputil/blob/master/py/query_twitter/generate_random_twitter_potential_ids.py)

get random user objects gets a bunch of random twitter user objects and puts them line by line in a json file.

abstract:
```
python generate_random_twitter_potential_ids.py -n NUMBER_IDS -o /path/to/output/file.json
```

practical:
```
python generate_random_twitter_potential_ids.py -n 2000 -o data/2000_twitter_ids.json
```

*returns* a json list of twitter ids written to file

note: https://dev.twitter.com/overview/api/twitter-ids-json-and-snowflake

## [transfer_collection](https://github.com/SMAPPNYU/smapputilities/tree/master/py/transfer_collection)

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

## [mail_tweet_counts](https://github.com/SMAPPNYU/smapputilities/tree/master/py/mail_tweet_counts)

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

## [username_id_convert](https://github.com/SMAPPNYU/smapputilities/tree/master/py/username_id_convert)

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

## [dump_database](https://github.com/SMAPPNYU/smapputilities/tree/master/py/archive_tools)

mongodumps a list of dbs fo a specified place

abstract:
```python
python py/archive_tools/dump_database.py -i PATH_TO_INPUT_JSON -ho DB_HOSTNAME_OR_IP -p DB_HOST_PORT -u DB_USERNAME -w DB_PASSWORD -o PATH_TO_OUTPUT_DIR

python py/archive_tools/dump_database.py -i DB_NAME1 DB_NAME2 ... -ho DB_HOSTNAME_OR_IP -p DB_HOST_PORT -u DB_USERNAME -w DB_PASSWORD -o PATH_TO_OUTPUT_DIR
```

practical:
```python
python py/archive_tools/dump_database.py -i ~/pylogs/dump_dbs_input.json -ho 100.100.100.100 -p 27017 -u some_db_user -w some_db_password -o ~/dumps/ &>/dev/null

python py/archive_tools/dump_database.py -i germany_election mike_brown -ho localhost -p 49999 -u some_db_user -w some_db_password -o ~/dumps/ -au admin -aw 'YOUR_ADMIN_USER_PASS' --querydump
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

-q `--querydump` dumps the database collections to json by querying mongodb using smappdragon's MongoCollection and dump_to_json tools, the idea is taht sometimes mongodump doesnt work that great, it has issues where it misses data in the db, queries are more likely to return data. query dump requires the use of an admin user/pass.

`&>/dev/null` - runs the script quietly instaed of printing mongodumps output

*returns* a series of running mongodump processes that dump the specified databases

takes a json input
```
[
"germany_election", "mike_brown", "blah" 
]
```

## [check_dump_integrity](https://github.com/SMAPPNYU/smapputilities/tree/master/py/archive_tools)

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

## [make_tar](https://github.com/SMAPPNYU/smapputilities/tree/master/py/archive_tools)

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

#make_sqlite_db

*not done*

make an sqlite database from a .json file, first it uses the same underlying code as [dump_to_csv](https://github.com/SMAPPNYU/smappdragon#dump_to_csv) to pull out columns that you specify, then it puts those columns into an sqlite db file.

abstract:
```sh
python make_sqlite_db.py /path/to/data_file.json /path/to/sqlite/db/file.db
```

practical:
```sh
# from json
python make_sqlite_db.py -i /scratch/yournetid/test.json -o /scratch/yournetid/test.db -t json -f 'id_str' 'user.id_str' 'text' 'entities.urls.0.expanded_url' 'entities.urls.1.expanded_url'

# or from csv, with header/fieldnames at the top
python make_sqlite_db.py -i /scratch/yournetid/test.csv -o /scratch/yournetid/test.db -t csv
```

use:
```sh
sqlite3 /scratch/mynetid443/test.db
# or 
sqlite test.db
```

*input* a csv or json line by line file
```
#example json input, each line looks like so
{"_id":{"$oid":"56949f8758ca5622d0a320d9"},"contributors":null,"coordinates":null,"created_at":"Tue Jan 12 06:39:03 +0000 2016","entities":{"hashtags":[],"symbols":[],"urls":[],"user_mentions":[{"id":107837944,"id_str":"107837944","indices":[0,7],"name":"Tess Rinearson","screen_name":"_tessr"},{"id":{"$numberLong":"2208027565"},"id_str":"2208027565","indices":[8,20],"name":"Product Hunt","screen_name":"ProductHunt"}]},"favorite_count":0,"favorited":false,"filter_level":"low","geo":null,"id":{"$numberLong":"686799531875405824"},"id_str":"686799531875405824","in_reply_to_screen_name":"_tessr","in_reply_to_status_id":{"$numberLong":"686798991166550016"},"in_reply_to_status_id_str":"686798991166550016","in_reply_to_user_id":107837944,"in_reply_to_user_id_str":"107837944","is_quote_status":false,"lang":"en","place":{"attributes":{},"bounding_box":{"coordinates":[[[-74.026675,40.683935],[-74.026675,40.877483],[-73.910408,40.877483],[-73.910408,40.683935]]],"type":"Polygon"},"country":"United States","country_code":"US","full_name":"Manhattan, NY","id":"01a9a39529b27f36","name":"Manhattan","place_type":"city","url":"https://api.twitter.com/1.1/geo/id/01a9a39529b27f36.json"},"random_number":0.24758333772157703,"retweet_count":0,"retweeted":false,"source":"\u003ca href=\"http://twitter.com\" rel=\"nofollow\"\u003eTwitter Web Client\u003c/a\u003e","text":"@_tessr @ProductHunt No one has stolen me yet. Security through obscurity.","timestamp":{"$date":"2016-01-12T06:39:03.000Z"},"timestamp_ms":"1452580743174","truncated":false,"user":{"contributors_enabled":false,"created_at":"Mon Feb 13 07:00:10 +0000 2012","default_profile":false,"default_profile_image":false,"description":"I am a tan white dot on a pale blue dot.","favourites_count":1028,"follow_request_sent":null,"followers_count":216,"following":null,"friends_count":300,"geo_enabled":true,"id":491074580,"id_str":"491074580","is_translator":false,"lang":"en","listed_count":16,"location":"NYC","name":"Yvan Scher","notifications":null,"profile_background_color":"9AE4E8","profile_background_image_url":"http://pbs.twimg.com/profile_background_images/513013156122087424/ycK_CMAU.jpeg","profile_background_image_url_https":"https://pbs.twimg.com/profile_background_images/513013156122087424/ycK_CMAU.jpeg","profile_background_tile":true,"profile_banner_url":"https://pbs.twimg.com/profile_banners/491074580/1399645051","profile_image_url":"http://pbs.twimg.com/profile_images/655145248616783873/bjsSKAcb_normal.jpg","profile_image_url_https":"https://pbs.twimg.com/profile_images/655145248616783873/bjsSKAcb_normal.jpg","profile_link_color":"D60916","profile_sidebar_border_color":"FFFFFF","profile_sidebar_fill_color":"DDEEF6","profile_text_color":"333333","profile_use_background_image":true,"protected":false,"screen_name":"yvanscher","statuses_count":2733,"time_zone":"Eastern Time (US \u0026 Canada)","url":"https://about.me/yvanscher","utc_offset":-18000,"verified":false}}

#example csv input
id_str,coordinates.coordinates.0,coordinates.coordinates.1,user.id_str,user.lang,lang,text,user.screen_name,user.location,user.description,created_at,user.friends_count,user.followers_count,retweet_count,entities.urls.0.expanded_url,entities.urls.1.expanded_url,entities.urls.2.expanded_url,entities.urls.3.expanded_url,entities.urls.4.expanded_url
790040318603329536,,,767465035815723008,en,en,#TrumpNavyShipNames USS Hillary Loves Yoko Ono   https://t.co/sHMLE50jvF,SpitfireSuzy,,"Outspoken opinions on Politics, Government & Media",Sun Oct 23 04:01:04 +0000 2016,151,121,0,http://worldnewsdailyreport.com/yoko-ono-i-had-an-affair-with-hillary-clinton-in-the-70s/,,,,
790040319882514432,,,485310129,en,en,RT @MikePenceVP: Photo of Bill Clinton giving a speech in Moscow for $500K right before Hillary sold 20% of US uranium to Russia. https://t?<80>?,WickedBecks,No Kaep fan in 49er Territory,TRUMP: Cuz You'd be in Jail #TRUMPPENCE #MAGA #AmericaFirst #CAIndieVoter Pro-OEXIT,Sun Oct 23 04:01:05 +0000 2016,5844,5794,0,,,,,
```

*output* after its done you should find a a `.db` file. this is your sqlite database, copy it, back it up, build indexes on it. do whatever you want to it.
```
sqlite> .schema
CREATE TABLE data (id_str,user__id_str,text,entities__urls__0__expanded_url,entities__urls__1__expanded_url,entities__media__0__expanded_url,entities__media__1__expanded_url);
sqlite> .tables
data
sqlite> select * from data;
686799531875405824|491074580|@_tessr @ProductHunt No one has stolen me yet. Security through obscurity.|NULL|NULL|NULL|NULL
686661056115175425|491074580|Predictions of peach's demise already starting. Nice.|NULL|NULL|NULL|NULL
686956278099349506|491074580|When was the state of the union first started? Ok wow since the office has existed. https://t.co/Cqgjkhr3Aa|https://en.wikipedia.org/wiki/State_of_the_Union#History|NULL|NULL|NULL
687115788487122944|491074580|RT @lessig: Looks like the @citizenequality act got a supporter tonight. Thank you @POTUS|NULL|NULL|NULL|NULL
686661056115175425|491074580|Predictions of peach's demise already starting. Nice.|NULL|NULL|NULL|NULL
687008713039835136|491074580|#GOPDebate approaching. Can't wait to observer a trump in its natural habitat!|NULL|NULL|NULL|NULL
687208777561448448|18673945|@yvanscher hey! saw u upvoted Cubeit on ProductHunt. Any feedback on how we can make Cubeit better for you? :) Thanks!|NULL|NULL|NULL|NULL
686662539913084928|491074580|RT @PopSci: iOS 9.3 update will tint your screen at night, for your health https://t.co/zrDt4TsoXB https://t.co/yXCEGQPHWp|http://pops.ci/cJWqhM|NULL|http://twitter.com/PopSci/status/686661925267206144/photo/1|NULL
```

r-links:
[RSQLite](https://cran.r-project.org/web/packages/RSQLite/index.html)
[sqlite extensions](http://stackoverflow.com/questions/18107336/load-spatialite-extension-in-rsqlite-crashes-r-os-x-ubuntu)

note: user fields are input with dot notation (as they come from json), all input field dots are converted to double underscores `__` in their respective sqlite database columns. this is because using dots `.` is troublesome on sqlite (as its a builtin). so an input field `entities.urls.0.expanded_url` would be `'entities__urls__0__expanded_url` in its sqlite column. double underscore is the only good option to represent one level of depth.

## launch_pbs_job

abstract:
```
python launch_pbs_job.py -c 'python myscript.py -a arg1 -b arg2'
```

practical:
```
python launch_pbs_job.py -c 'python merge_dataset_files.py 
-i vp_debate_2016_1_data__10_04_2016__00_00_00__23_59_59.json.bz2 vp_debate_2016_1_data__10_05_2016__00_00_00__23_59_59.json.bz2 
-o vp_debate_2016_1_data__merged.json'
```

*starts* one running job

note:

'-a' and '-b' are arguments to your myscript.py they are totally optional and depend on the
script you are running on each inputfile.

note:

make sure you are using anaconda python, ~/anaconda/bin/python

## launch_parallel_pbs_jobs

very similar to 'launch_job' the difference is its meant to be used on split up datasets so yo ucan parallelize whatever script you are calling. this is good for when your job is long running and 1 - will last more than 100 hrs (which is the walltime limit on hpc) 2 - is big and you want to finish faster. will start several jobs equivalent to running commands:
```
python myscript.py -a arg1 -b arg2 -i input_file_1.json
python myscript.py -a arg1 -b arg2 -i input_file_2.json
...
etc
```

abstract:
```
python launch_parallel_pbs_jobs.py -i inputfile_*.json -c 'python myscript.py -a arg1 -b arg2'
```

practical:
```
# makes a database for each input file
python launch_parallel_pbs_jobs.py -i vp_debate_2016_1_data__merged.json venezuela_2016_data__merged.json -c 'python make_sqlite_db.py -o /scratch/yournetid/test.db -t json -f 'id_str' 'user.id_str' 'text'
```

*starts* one job per input file specified by `-i`

note:

in the practical exmaple the call to `-c 'python make_sqlite_db.py ...` does not contain a -i as it should, this is bceause our -i is already covered by launch_parallel_jobs.py -i (input). this would start several process and craete several separate sqlite db files.

## launch_sbatch_job

abstract:
```sh
# with required options
python launch_sbatch_job.py -c PARALLEL_COMMAND 

# with additional unrequired options
python launch_sbatch_job.py -c PARALLEL_COMMAND  -no NUMBER_OF_NODES -nt NUMBER_OF_TASKS -cp CPUS_PER_TASK -o JOB_LOG -e JOB_ERROR_LOG -w JOB_HOURS -m JOB_MINUTES -s JOB_SECONDS -me JOB_MEMORY -j JOB_NAME -ma EMAIL_TO_MESSAGE
```

practical:
```sh
# example with minimal inputs
python launch_sbatch_job.py -c 'python my_script.py -a arg1 -b arg2 -i my_file.json'

#example with all optional inputs, inputs will be set to a default if you do not set them
#these defaults automatically detect your email and put log files in your home directory ~/
python launch_sbatch_job.py -c 'python my_script.py -a arg1 -b arg2 -i my_file.json' -no 2 -nt 4 -cp 1 -o ~/logfile.out -e ~/errorfile.err -w 100 -m 00 -s 05 -me 15GB -j my_job_name -ma my_mail_addr
```

## launch_parallel_sbatch_jobs

abstract:
```sh
# with required options
python launch_sbatch_job.py -c PARALLEL_COMMAND -i INPUTS_FOR_EACH_JOB -t INPUT_FLAG_FOR_YOUR_SCRIPT

# with additional unrequired options
python launch_sbatch_job.py -c PARALLEL_COMMAND -i INPUTS_FOR_EACH_JOB -t INPUT_FLAG_FOR_YOUR_SCRIPT -no NUMBER_OF_NODES -nt NUMBER_OF_TASKS -cp CPUS_PER_TASK -o JOB_LOG -e JOB_ERROR_LOG -w JOB_HOURS -m JOB_MINUTES -s JOB_SECONDS -me JOB_MEMORY -j JOB_NAME -ma EMAIL_TO_MESSAGE
```

practical:
```sh
# example with minimal inputs
python launch_parallel_sbatch_jobs.py -i ~/* -c 'ls -lah'

#example with all inputs
python launch_parallel_sbatch_jobs.py -i ~/* -c 'python my_script.py -a arg1 -b arg2' -t 'i' -no 1 -nt 1 -cp 1 -o ~/my_job_log.out -e ~/my_error_log.err -w 50 -m 10 -s 05-me 10GB -j parallel_job_apr7 -ma dtjp67443@nyu.edu
```

note: the -t flag tells the parallelizer what the script in -c takes as its input argument, it can be omitted if there is no special flag (as seen above in the caes of the `ls` command which takes inputs without a flag telling it to). 

so for a single job you would do:

```sh
python launch_sbatch_job.py -c 'python my_script.py -a arg1 -b arg2 -i my_file.json'
```

but if you needed to run several of these in parallel you would do:

```sh
python launch_parallel_sbatch_jobs.py -c 'python my_script.py -a arg1 -b arg2' -t 'i' -i ~/*
```

the `-i` from inside the -c in the first command gets pulled out and turns into -i and -t 'i'. if myscript.py instead takes its inputs as `-a` then the command would be written as so the first time for a single job:

```sh
python launch_sbatch_job.py -c 'python my_script.py -a arg1 -b arg2 -a my_file.json'
```

```sh
python launch_parallel_sbatch_jobs.py -c 'python my_script.py -a arg1 -b arg2' -t 'a' -i ~/*
```

note the substiuttion of i with a in two places.

## [olympus2scratch](https://github.com/SMAPPNYU/smapputil/blob/master/py/olympus_2_scratch/olympus2scratch.py)

moves the specified dataset to your personal scratch space, unzips it, and cleans it, there is also a [notebook version](https://github.com/SMAPPNYU/smapputil/blob/master/nbs/olympus2scratch.ipynb) that does the same thing.

abstract:
```sh
python olympus2scratch.py -c COLLECTION_NAME -n NUMBER_OF_CPUS
```

practical:
```sh
# move the data set inside the folder called 'mike_brown' using 1 cpu
python olympus2scratch.py -c mike_brown -n 1
```

*output* a copied set of files for the dataset requested

note: you will need to run this inside a job using either sbatch, or our [job script, launch_sbatch_job](#launch_sbatch_job)

note: do not try to use more CPUs than your job has allocated

note: cleaning scipt used is [smappdragon's tweet cleaner](https://github.com/SMAPPNYU/smappdragon#tweet_cleaner)

# pbs

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

## pbs_merge_dataset_files

`merge_dataset_files_nix.pbs.sh` (for the cluster), `merge_dataset_files_osx.pbs.sh` (for personal use), a job file that will merge unzip and merge json file of a dataset, the two scripts differ in their use of date, as its different on osx and linux/*nix, merges files from a dataset into one file

abstract:
```sh
qsub merge_dataset_files_nix.pbs -v 1="/path/to/data/folder",2="/path/to/output/file",3="startdate",4="enddate"
```
pratical:
```sh
# run the job, getting data files from nov 8 2016 to nov 10 2016
# on hpc
qsub ~/smapprepos/smapputil/pbs/merge_dataset_files_nix.pbs -v 1="/scratch/olympus/us_election_trump_2016/data/",2="/scratch/smapp/us_election_trump_2016.json.bz2",3="2016-08-11",4="2016-10-11"

# in normal bash 
bash merge_dataset_files_osx.pbs /archive/smapp/olympus/germany_elec_2016/data/ /scratch/mynetid560/germany_elec_merged.json.bz2 2016-08-11 2016-10-11
```

then in `/scratch/mynetid560/` you will find the merged file, `germany_elec_merged.json.bz2`

note: input dates are year-month-day or %Y-%m-%d, filenames have their dates as month_day_year. this is because of the way linux date demands date formats

note: one alternative is to just bzip2 -d /scratch/mynetid560/germany_elec_2016/data/*.bz2 and then jsut use cat or [merge_json](#merge_json) as a job to merge the dataset.

note: if you omit startdate and enddate it get all the data files that have been bzipped (.bz2 files)

note: if you want several discreet dates you can easily merge them with:
```sh
echo /path/to/data_folder/date1.bz2 /path/to/data_folder/date1.bz2 | xargs bzip2 -dc | bzip2 >/path/to/merged/file.json.bz2
```

or if you want to merge things manually
```sh
#unzip the files
bzip2 -d /path/to/data_folder/*.bz2
#merge the files
cat /path/to/data_folder/*.json > /path/to/merged_file.json
```

# sbatch 

## cpu-jupyter

an sbatch script that runs a jupyter notebook on hpc, using a cpu to compute on

**step 1 - run:**
```
sbatch cpu-jupyter.sbatch
```

**step 2:**

then get your connection url and save it somewhere (in a note or text file). you can find this connection url in the slurm-PROCESSID.out (where process id is the id returned when you submitted the job on the command line) file in the working directory where you were when you ran the sbatch command above. this url will contain the connection port you will need for the next step. the URL is something like: `http://localhost:PORT/?token=XXXXXXXX`

**step 3:**

create a tunnel to map the notebook on hpc to your local computer's port. in a local (non-hpc) terminal window you will want to follow one of these paths:

if you are working in NYU campus, please open a terminal window, run command

`ssh -L PORT:localhost:PORT NET_ID@prince.hpc.nyu.edu`

where `PORT` is the port you found in the connection url (in output file) and `NET_ID` is your nyu netid.

if you are working off campus, you should already have ssh tunneling setup through HPC bastion host. please open a terminal window, run command

`ssh -L PORT:localhost:PORT NET_ID@prince`

keep the iTerm windows from this step open. 

**step 4:**

Now open browser you should be able to connect to jupyter notebook running remotely on prince compute node with above url you procured above of the format: 

http://localhost:PORT/?token=XXXXXXXX

notes:

This is a variation of the instructions offered by HPC 
see: https://wikis.nyu.edu/display/NYUHPC/Running+Jupyter+on+Prince
located here: /share/apps/examples/jupyter/run-jupyter.sbatch

Make sure SSH-authentication is enabled on Prince see: 
https://wikis.nyu.edu/display/NYUHPC/Configuring+SSH+Key-Based+Authentication

This implementation also assumes you use your own distro of Python (and Jupyter) via Anaconda.
To download Anaconda (https://www.continuum.io/downloads), 
you can the run the following in your Prince home:
```
wget https://repo.continuum.io/archive/Anaconda3-4.3.1-Linux-x86_64.sh
bash Anaconda3-4.3.0-Linux-x86_64.sh
```

if working off campus setup an hpctunnel (before the prince tunnel to the notebook), your ~/.ssh/config file should have the lines like so:

Host hpctunnel
   HostName hpc.nyu.edu
   ForwardX11 yes
   LocalForward 80237 prince.hpc.nyu.edu:22
   User YOUR_NET_ID

Host prince
  HostName localhost
  Port 8027
  ForwardX11 yes
  User YOUR_NET_ID

Troubleshooting:
- If a session quits, you may need to increase the allocated memory (--mem).
- If you parallelize tasks you will need to increase the --cpus-per-task.

## gpu-jupyter

an sbatch script that runs a jupyter notebook on hpc, using a gpu to compute on

absract/practical:
```
sbatch gpu-jupyter.sbatch
```

note: everything from the [cpu-jupyter](#cpu-jupyter) guide applies

## [olympus2scratch_ex](https://github.com/SMAPPNYU/smapputil/blob/master/sbatch/olympus2scratch_ex.sbatch)

An example [slurm/sbatch](https://wikis.nyu.edu/display/NYUHPC/Slurm+Tutorial) script using [olympus2scratch.py](#olympus2scratch) to copy, decompress, and clean files from `/scratch/olympus/` to your personal scratch space `/scratch/$USER/`.

abstract/practical:
```
sbatch olympus2scratch_ex.sbatch
```

Note:<br>
The sbatch script assumes you're using conda distributed Python.
You can get this using the following command in your HPC Prince home
```
wget https://repo.continuum.io/archive/Anaconda3-4.3.1-Linux-x86_64.sh
bash Anaconda3-4.3.0-Linux-x86_64.sh
```

You're also going to need smappdragon, for the tweet cleaner
https://github.com/SMAPPNYU/smappdragon
```
pip install smappdragon
```

## [set_olympus_permissions](https://github.com/SMAPPNYU/smapputil/blob/master/sbatch/set_olympus_permissions.sbatch)

this script sets the permissions on olympus and makes sure they stay the way we want them.

abstract/practical:
```
sbatch set_olympus_permissions.sbatch
```

# sh 

bash utilities / scripts that do useful thngs. Built in bash 3.2.X. You may notice many of the scripts are clones of scripts in [shellscripts repo](https://github.com/SMAPPNYU/shellscripts). This is temporary. Their final reting place will be here. The difference will be modularized testing, modularized scripts, each script will get its own tests (instead of the single file), the tests will be unit tests and as little as porrible system state tests, etc. As soon as the move is done and we're sure these scripts work we will phase out shellscripts repo (it was originally an experiment and we're going to wrangle it under control now before it becomes a legacy).

## testing

[Download the shunit2 framework](https://storage.googleapis.com/google-code-archive-downloads/v2/code.google.com/shunit2/shunit2-2.1.6.tgz), put it in `sh/bash_modules`. Go into the `smapputilities/sh/test` folder using `cd test` and run `bash test_*.sh` this should run a series of shunit2 tests. You should only run tests on a system that isn't running any hades tunnels currently.

For now check out the [shellscripts repository](https://github.com/SMAPPNYU/shellscripts).

For bash testing we could try to use [maybe] (https://github.com/p-e-w/maybe) with the bash [`test` builtin](http://www.gnu.org/software/bash/manual/html_node/Bourne-Shell-Builtins.html#Bourne-Shell-Builtins).

i know that testing with bash is hard and can be very sketchy. just do your best to modularize the code and test each piece that is important.

## logging

you'll want to import the logger into your bash script:

```bash
source "/Users/yvan/smapprepos/smapputilities/sh/hades_tunnels/bash_modules/logger.sh" --source-only
```

and then use it like so:
```bash
log "blah"
log "blah $c"
```

## interactive_prince

starts an interactive session on prince

```bash
bash sh/interactive_prince.sh CPUS HOURS RAM
# starts an interactive session with 1 cpu, for 1 hour, and 1 GB RAM
bash sh/interactive_prince.sh 1 1 1

# starts an interactive session with 1 cpu, for 7 hours, and 10 GB RAM
bash sh/interactive_prince.sh 1 7 10
```

## [term_search](https://github.com/SMAPPNYU/smapputil/blob/master/sh/term_search.sh)

searches for a term among all filter files on /scratch/olympus (active datasets)

```bash
bash sh/term_search.sh 'hillary'
```

would return:
```
{"value": "#aleppo", "date_added": "Tue Dec 13 10:10:25 +0000 2016", "date_removed": null, "turnoff_date": null, "active": true, "filter_type": "track"}
```

## resources

[run a bash program in the back ground] (http://stackoverflow.com/questions/13676457/how-can-i-put-the-current-running-linux-process-in-background)

[bash docs / reference](http://tldp.org/HOWTO/Bash-Prog-Intro-HOWTO.html#toc7)

[how to write a for loop in bash](http://tldp.org/HOWTO/Bash-Prog-Intro-HOWTO-7.html)

[bash exit codes](http://www.tldp.org/LDP/abs/html/exitcodes.html)

## [logger](https://github.com/SMAPPNYU/smapputilities/tree/master/sh/logger)

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
