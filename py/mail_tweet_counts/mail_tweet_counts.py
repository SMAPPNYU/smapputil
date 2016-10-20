import sys
import json
import logging
import pymongo
import argparse
import datetime

from config import config
from os.path import expanduser
from envelopes import Envelope, GMailSMTP

def mail_tweet_counts(host, port, ignore_dbs, ignore_collections):
    email_string = ''
    yesterday =  datetime.datetime.now() - datetime.timedelta(days=1)
    today = datetime.datetime.now()
    mongo = pymongo.MongoClient(host, int(port))
    db_gen = (database_name for database_name in mongo.database_names() if database_name not in ignore_dbs)
    for database_name in db_gen:
        count_for_db = 0
        collection_gen = (collection_name for collection_name in mongo[database_name].collection_names() if collection_name not in ignore_collections)
        for collection_name in collection_gen:
            count_for_db = count_for_db + mongo[database_name][collection_name].count({'timestamp': { '$gte': yesterday, '$lt': today }})
        email_string = email_string + 'db: {}, count: {}'.format(database_name, count_for_db) +'<br>\n' + '<br>\n'
        count_for_db = 0

    envelope = Envelope(
        from_addr=(config['mail']['gmailuser'], 'from smappmonitor'),
        to_addr=(config['mail']['toemail'], 'to smapp'),
        subject='daily tweet count',
        html_body=email_string
    )

    envelope.send('smtp.gmail.com', login=config['mail']['gmailuser'], password=config['mail']['gmailpass'], tls=True)

def parse_args(args):
    parser = argparse.ArgumentParser()
    parser.add_argument('-ho', '--host', dest='host', required=True, help='local hostname to map to')
    parser.add_argument('-p', '--port', dest='port', required=True, help='local port to map to the remoteport')
    parser.add_argument('-l', '--log', dest='log', default=expanduser('~/pylogs/mail_tweet_counts.log'), help='This is the path to where your output log should be.')
    return parser.parse_args(args)

if __name__ == '__main__':
    args = parse_args(sys.argv[1:])

    logging.basicConfig(filename=args.log, level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    mail_tweet_counts(args.host, args.port, config['ignore_dbs'], config['ignore_collections'])

'''
author @yvan
'''
