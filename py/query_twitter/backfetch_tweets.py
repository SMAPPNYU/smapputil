"""
Script to add tweets from search api to a collection.
"""

import sys
import logging
import argparse
from tweepy import Cursor, TweepError
from smappPy.tweepy_pool import APIPool
from mongo_manager import MongoDBManager

def store_tweets(mongo_manager, tweets):
    k = 0
    for tweet in tweets:
        mongo_manager.store_tweet(tweet._json)
        k += 1
        sys.stdout.write('.')
    print('')
    logging.info("{} tweets done.".format(k))

def find_tweets_for_users(api, user_ids):
    return [tweet for user_id in user_ids for tweet in Cursor(api.user_timeline, user_id).items()]


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--server', default='smapp-data.bio.nyu.edu')
    parser.add_argument('-p', '--port', default=27011)
    parser.add_argument('-u', '--user')
    parser.add_argument('-w', '--password')
    parser.add_argument('-d', '--database-name', required=True)
    parser.add_argument('-c', '--tweet-collection-name', default='tweets')
    parser.add_argument('-o', '--oauths-file', required=True)
    parser.add_argument('-id', '--user-ids', help='comma-separated list of user ids to backfetch')
    parser.add_argument('-q', '--query')
    args = parser.parse_args()

    if not args.user_ids and not args.query:
        parser.exit('Please choose  user-ids or a query')

    api = APIPool(oauths_filename=args.oauths_file)

    mongo_manager = MongoDBManager(args.server,
                                   args.port,
                                   args.database_name,
                                   args.tweet_collection_name,
                                   args.user,
                                   args.password,
                                   logging)

    if args.user_ids:
        user_ids = [e.strip() for e in args.user_ids.split(',')]
        logging.info("Backfetching for {} users: {}".format(len(user_ids), args.user_ids))
        store_tweets(mongo_manager, find_tweets_for_users(api, user_ids))

    if args.query:
        logging.info("Backfetching for query: {}".format(args.query))
        store_tweets(mongo_manager, Cursor(api.search, args.query).items())
