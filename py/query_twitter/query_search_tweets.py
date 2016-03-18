import argparse
import datetime
import logging
import urllib
import time
import json
import csv
import sys
import os

from smappPy import tweepy_pool
from tweepy import Cursor, TweepError

def twitter_query(args):
    logger = logging.getLogger(__name__)
    
    terms_list = get_terms_list(args.input)
    logger.info('creating oauth pool...')

    #query the tweets
    query_search_tweets(args.output, terms_list)

def query_search_tweets(output, terms_list):
    logger = logging.getLogger(__name__)

    tweets_id_json = {}
    num_users_queried = 0

    #create the api pool
    json_data = open(args.auth).read()
    oauth = json.loads(json_data)
    api_pool = tweepy_pool.APIPool(oauth)

    for term in terms_list:
        num_users_queried = num_users_queried + 1
        count = 0
        if not term == '':
            try:
                for item in Cursor(api_pool.search, q=urllib.quote(term)).items():
                    logger.debug('tweet text: %s', item.text) 
                    count = count + 1
                    if not term in tweets_id_json:
                        tweets_id_json[term] = {}
                    tweets_id_json[term][str(count)] = item.text
            except TweepError as e:
                logger.info('tweepy error: %s', e)
            logger.info('counted %s tweets for term %s', count, term)
        logger.info('number of users queried so far: %s', num_users_queried)

    write_fd = open(args.output, 'w')
    write_fd.write(json.dumps(tweets_id_json, indent=4))
    write_fd.close()

def get_terms_list(file_input):
    logger = logging.getLogger(__name__)
    filename, file_extension = os.path.splitext(file_input)
    terms_list = []
    if file_extension == '.json':
        logger.info('loading json...')
        with open(file_input) as data:
            terms_list = json.load(data)
    elif file_extension == '.csv':
        logger.info('loading csv...')
        count = 0
        with open(file_input) as f:
            for rowdict in list(csv.DictReader(f)):
                # if list is not empty
                if rowdict:
                    terms_list.append(rowdict['term'])
        logger.info('launching query for %s users', len(terms_list))
    return terms_list

def parse_args(args):
    currentdate = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', dest='input', required=True, help='This is a path to your input.json, a [] list of twitter ids.')
    parser.add_argument('-o', '--output', dest='output', required=True, help='This will be your output file, a {} json object showing original ids and twitter screen names.')
    parser.add_argument('-a', '--auth', dest='auth', required=True, help='This is the path to your oauth.json file for twitter')
    parser.add_argument('-l', '--log', dest='log', default=os.path.expanduser('~/pylogs/query_search_tweets'+currentdate+'.log'), help='This is the path to where your output log should be. Required')
    return parser.parse_args()

if __name__ == '__main__':
    #setup parser for command line arguments
    args = parse_args(sys.argv[1:])
    #configure logs
    logging.basicConfig(filename=args.log, level=logging.INFO)
    # actually merge the bson files
    twitter_query(args)

'''
http://tweepy.readthedocs.org/en/v3.5.0/api.html?highlight=search#API.search
https://dev.twitter.com/rest/public/search
https://dev.twitter.com/rest/reference/get/search/tweets
https://dev.twitter.com/rest/public/rate-limiting
'''
