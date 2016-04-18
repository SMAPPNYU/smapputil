import os
import sys
import csv
import json
import tweepy
import logging
import argparse
import datetime

from os.path import expanduser
from smappPy import tweepy_pool

def ids_to_usernames(id_list, output, api):
    #configure logging
    logger = logging.getLogger(__name__)
    logger.info('Creating your output file : %s', output)
    write_fd = open(args.output, 'w')

    for a_user_id in id_list:
        try:
            name_json = {}
            res = api.get_user(user_id=a_user_id)
            name_json['screen_name'] = res.screen_name
            write_fd.write(json.dumps(name_json))
            write_fd.write('\n')
            logger.info("{} , {}".format(a_user_id, res.screen_name))
        except tweepy.TweepError as e:
            logger.info('excepted tweepy error: {}'.format(e))

    write_fd.close()

def usernames_to_ids(usernames_list, output, api):
    #configure logging
    logger = logging.getLogger(__name__)
    logger.info('Creating your output file : %s', output)
    write_fd = open(args.output, 'w')

    for a_user_screen_name in usernames_list:
        try:
            name_json = {}
            res = api.get_user(screen_name=a_user_screen_name)
            name_json['id'] = res.id
            write_fd.write(json.dumps(name_json))
            write_fd.write('\n')
            logger.info("{} , {}".format(a_user_screen_name, res.id))
        except tweepy.TweepError as e:
            logger.info('excepted tweepy error: {}'.format(e))

    write_fd.close()

def parse_args(args):
    currentdate = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    parser = argparse.ArgumentParser()
    parser.add_argument('-op', '--operation', dest='operation', required=True, help='name of method to perform, ids_users, users_ids')
    parser.add_argument('-i', '--input', dest='input', required=True, help='This is a path to your input.json, a [] list of twitter ids.')
    parser.add_argument('-o', '--output', dest='output', required=True, help='This will be your output file, a {} json object showing original ids and twitter screen names.')
    parser.add_argument('-a', '--auth', dest='auth', required=True, help='This is the path to your oauth.json file for twitter')
    parser.add_argument('-l', '--log', dest='log', default=expanduser('~/pylogs/username_id_convert'+currentdate+'.log'), help='This is the path to where your output log should be. Required')
    return parser.parse_args(args)

if __name__ == '__main__':
    #setup parser for command line arguments
    args = parse_args(sys.argv[1:])
    #configure logs
    logging.basicConfig(filename=args.log, level=logging.INFO)
    logger = logging.getLogger(__name__)

    input_list = []
    _, file_extension = os.path.splitext(args.input)

    if file_extension == '.json':
        logger.info('trying json...')
        id_data = open(args.input).read()
        input_list = json.loads(id_data)
        logger.info('loaded input_list as json')
    elif file_extension == '.csv':
        logger.info('is not json, trying csv')
        csvhandle = open(args.input)
        csvreader = csv.reader(csvhandle)
        count = 0
        for row in csvreader:
            if count > 0:
                input_list.append(row[0])
            count = count + 1
        logger.info('loaded input_list as csv')

    # create an API pool
    json_data = open(args.auth).read()
    oauth = json.loads(json_data)
    api = tweepy_pool.APIPool(oauth)

    if args.operation == 'ids_users':
        ids_to_usernames(input_list, args.output, api)
    elif args.operation == 'users_ids':
        usernames_to_ids(input_list, args.output, api)

'''
author @yvan
tweepy docs here : https://github.com/tweepy/tweepy/blob/master/tweepy/api.py#L146
'''