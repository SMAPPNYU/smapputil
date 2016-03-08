from smappPy import tweepy_pool
from tweepy import Cursor, TweepError

import argparse
import logging
import time
import json
import csv
import os

# c* http://stackoverflow.com/questions/22242181/csv-row-import-into-python-array

def twitter_query(args):
    logger = logging.getLogger(__name__)
    
    id_list_one = get_id_list(filename, file_extension)

    logger.info('creating oauth pool...')

    #create the api pool
    json_data = open(args.auth).read()
    oauth = json.loads(json_data)
    api_pool = tweepy_pool.APIPool(oauth)

    #query the tweets
    query_write_tweets(args)

def query_write_tweets(args):
    tweets_id_json = {}
    num_users_queried = 0

    for userid in id_list_one:
        logger.info('number of users queried so far: %s', num_users_queried)
        num_users_queried = num_users_queried + 1
        # even though the count is 200 we can cycle through 3200 items.
        # if you put a count variable in this cursor it will iterate up 
        # to about 3200
        if not userid == '':
            try:
                count = 0
                for item in Cursor(api_pool.user_timeline, user_id=userid, count=200).items():
                    logger.debug('tweet text: %s', item.text) 
                    count = count + 1
                    if not userid in tweets_id_json:
                        tweets_id_json[userid] = {}
                    tweets_id_json[userid][str(count)] = item.text
            except TweepError as e:
                logger.info('tweepy error: %s', e) 

    write_fd = open(args.output, 'w')
    write_fd.write(json.dumps(tweets_id_json, indent=4))
    write_fd.close()

def get_id_list(args):
    logger = logging.getLogger(__name__)
    # get the list of ids
    filename, file_extension = os.path.splitext(args.input)
    id_list = []
    if file_extension == '.json':
        logger.info('loading json...')
        id_data = open(args.input).read()
        id_list = json.loads(id_data)
    elif file_extension == '.csv':
        logger.info('loading csv...')
        # csvhandle = open(args.input, 'rU')
        # csvreader = csv.reader(csvhandle, dialect=csv.excel_tab)
        count = 0
        with open(args.input) as f:
            for rowdict in list(csv.DictReader(f)):
                # if list is not empty
                if rowdict:
                    logger.info('user id %s with %s relevant tweets',rowdict['id_str'], int(rowdict['relevant_tweets_count']))
                    id_list.append(rowdict['id_str'])
        logger.info('launching query for %s users', len(id_list))
    return id_list

def parse_args(args):
    currentdate = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', dest='input', required=True, help='This is a path to your input.json, a [] list of twitter ids.')
    parser.add_argument('-o', '--output', dest='output', required=True, help='This will be your output file, a {} json object showing original ids and twitter screen names.')
    parser.add_argument('-a', '--auth', dest='auth', required=True, help='This is the path to your oauth.json file for twitter')
    parser.add_argument('-l', '--log', dest='log', default=expanduser('~/pylogs/merge_bson_'+currentdate+'.log'), help='This is the path to where your output log should be. Required')
    args = parser.parse_args()

if __name__ == '__main__':
    #setup parser for command line arguments
    args = parse_args(sys.argv[1:])
    #configure logs
    logging.basicConfig(filename=args.log, level=logging.INFO)
    # actually merge the bson files
    twitter_query(args)