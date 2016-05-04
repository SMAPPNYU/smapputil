"""
Get tweets from Twitter REST API via a number of methods (twitter search queries,
tweet IDs, or user IDs).

Store to mongodb (or file?)
"""

import time
import codecs
import logging
import argparse
from tweepy import TweepError
from simple_mongo_manager import SimpleMongoDBManager
from smappPy.get_tweets import query_tweets, user_tweets
from smappPy.tweepy_error_handling import parse_tweepy_error
from smappPy.tweepy_pool import APIBreakPool, APIPool, RateLimitException

OVER_CAP_WAIT = 10
USER_DNE_ERROR = 34

logger = logging.getLogger('BackfetchLogger')
def set_logger():
    logger.setLevel(logging.INFO)
    h = logging.StreamHandler()
    h.setLevel(logging.INFO)
    h.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(h)

def store_tweets(mongo_manager, tweets):
    k = 0
    while True:
        try:
            t = tweets.next()
        except RateLimitException as r:
            logger.info("Twitter RateLimit. Breaking (moving to next term).")
            break
        except TweepError as e:
            error_dict = parse_tweepy_error(e)
            if error_dict["code"] == USER_DNE_ERROR:
                logger.info("User does not exist. Breaking (moving to next user).")
                break
            else:
                logger.info("Tweepy error: {0}, {1}. Breaking.".format(error_dict["code"],
                    error_dict["message"]))
                break
        except StopIteration:
            logger.info("All tweets requested have been fetched.")
            break
        except Exception as e:
            logger.warning("Unknown error, stopping: {0}".format(e))
            break
        mongo_manager.store_tweet(t._json)
        k += 1
    logger.info(".. {0} tweets fetched.".format(k))


if __name__ == "__main__":
    set_logger()

    parser = argparse.ArgumentParser("Gets Twitter REST API tweets, stores")
    parser.add_argument("-s", "--server", default="smapp-data.bio.nyu.edu")
    parser.add_argument("-p", "--port", default=27011)
    parser.add_argument("-u", "--user", default="smapp_readWrite")
    parser.add_argument("-w", "--password", required=False)
    parser.add_argument("-d", "--database-name", required=True)
    parser.add_argument("-c", "--tweet-collection-name", default="tweets")
    parser.add_argument("-o", "--oauths-file", required=True)
    parser.add_argument("-t", "--query-type", required=True,
        choices=["search", "user_id", "user_screen_name"], 
        help="Type of REST api query to issue. Indicates what in-file holds")
    parser.add_argument("-i", "--infile", required=True,
        help="Line-separated file of searches, user IDs, or tweet IDs to fetch tweets for")
    parser.add_argument("-l", "--limit", type=int, default=0,
        help="Number of tweets to request in total (recommended) [0]")
    args = parser.parse_args()

    mongo_manager = SimpleMongoDBManager(args.server,
                                         args.port,
                                         args.database_name,
                                         args.tweet_collection_name,
                                         args.user,
                                         args.password,
                                         logger)

    # BreakPool or just Pool? If no break, then will query same thing until limit is hit or
    # StopIteration is reached. In case of search terms, no StopIteration comes (and usually
    # it doesn't with users), so have to rely on Limit being set well.
    # Only thing to keep track of is whether a high limit gets multiples of the same thing
    # (it's effectively running the same query over and over), or whether it gets new/dift/
    # /earlier/later things (which should happen, and should be managed by the tweepy cursor)
    # api = APIBreakPool(oauths_filename=args.oauths_file, debug=True)
    api = APIPool(oauths_filename=args.oauths_file, debug=True)
    
    with codecs.open(args.infile, "r", "utf8") as inhandle:
        for line in inhandle:
            query_term = line.strip()
            logger.info("Querying REST api for term/user: {0}".format(query_term))

            if args.query_type == "search":
                tweet_cursor = query_tweets(api, query_term, limit=args.limit)
            elif args.query_type == "user_id":
                tweet_cursor = user_tweets(api, user_id=int(query_term), limit=args.limit)
            elif args.query_type == "user_screen_name":
                tweet_cursor = user_tweets(api, screen_name=query_term, limit=args.limit)
            else:
                raise Exception("Error, unrecognized query type: {0}".format(args.query_type))

            #import pdb; pdb.set_trace()
            store_tweets(mongo_manager, tweet_cursor)

    logger.info("Complete")



