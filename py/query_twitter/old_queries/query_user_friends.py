import argparse
import datetime
import logging
import json
import csv
import sys
import os

from tkpool.tkpool.tweepypool import TweepyPool
from tweepy import Cursor, TweepError

def twitter_query(output, input_file, auth_file):
    logger = logging.getLogger(__name__)
    
    id_list = get_id_list(input_file)
    logger.info('creating oauth pool...')

    #query the tweets
    query_user_friends(output, id_list, auth_file)

def query_user_friends(output, id_list, auth_file):

    logger = logging.getLogger(__name__)

    num_inputs_queried = 0

    #create the api pool
    pi_pool = TweepyPool(auth_file)

    write_fd = open(output, 'w+')

    for userid in id_list:
        num_inputs_queried = num_inputs_queried + 1
        if not userid == '':
            try:
                count = 0
                for item in Cursor(api_pool.friends, id=userid, count=5000).items():
                    logger.debug('user id: {},  and screen_name {}'.format(item.id, item.screen_name)) 
                    count = count + 1
                    tweet_item = json.loads(json.dumps(item._json))
                    tweet_item['smapp_original_user_id'] = userid
                    tweet_item['smapp_timestamp'] = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S +0000')
                    write_fd.write(json.dumps(tweet_item))
                    write_fd.write('\n')
            except TweepError as e:
                logger.info('tweepy error: %s', e)
            logger.info('counted %s objects for input %s', count, userid)
        logger.info('number of inputs queried so far: %s', num_inputs_queried)
    write_fd.close()

def get_id_list(file_input):
    logger = logging.getLogger(__name__)
    filename, file_extension = os.path.splitext(file_input)
    id_list = []
    if file_extension == '.json':
        logger.info('loading json...')
        id_data = open(file_input).read()
        id_list = json.loads(id_data)
    elif file_extension == '.csv':
        logger.info('loading csv...')
        count = 0
        with open(file_input) as f:
            for rowdict in list(csv.DictReader(f)):
                # if list is not empty
                if rowdict:
                    id_list.append(rowdict['id'])
        logger.info('launching query for %s inputs', len(id_list))
    return id_list

def parse_args(args):
    currentdate = datetime.datetime.now().strftime("%Y-%m-%d_%H:%M")
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', dest='input', required=True, help='This is a path to your input.json, a [] list of twitter ids.')
    parser.add_argument('-o', '--output', dest='output', required=True, help='This will be your output file, a {} json object showing original ids and twitter screen names.')
    parser.add_argument('-a', '--auth', dest='auth', required=True, help='This is the path to your oauth.json file for twitter')
    parser.add_argument('-l', '--log', dest='log', default=os.path.expanduser('~/pylogs/query_user_friends_'+currentdate+'.log'), help='This is the path to where your output log should be. Required')
    return parser.parse_args()

if __name__ == '__main__':
    #setup parser for command line arguments
    args = parse_args(sys.argv[1:])
    #configure logs
    logging.basicConfig(filename=args.log, level=logging.INFO)
    # actually merge the bson files
    twitter_query(args.output, args.input, args.auth)
