'''
Queries twitter for all timelines for input users.
This will return one bzipped json file for all input users.

This script assumes a volume is attached to a digitalocean machine.

https://developer.twitter.com/en/docs/tweets/timelines/api-reference/get-statuses-user_timeline

Leon Yin 2018-02-14
updated 2018-08-06
'''

import argparse
import datetime
import logging
import json
import csv
import sys
import os
import time
import socket
from subprocess import Popen, PIPE

import s3
import digitalocean
from tkpool.tkpool.tweepypool import TweepyPool
from tweepy import Cursor, TweepError

from utils import *


def parse_args(args):
    '''
    Which arguments we'll need
    '''
    parser = argparse.ArgumentParser()

    parser.add_argument('-i', '--input', dest='input', required=True, help='This is a path to your input(csv or json), a [] list of twitter ids.')
    parser.add_argument('-a', '--auth', dest='auth', required=True, help='This is the path to your oauth.json file for twitter')
    parser.add_argument('-d', '--digital-ocean-token', dest='token', required=False, help='DO access token', const=1, nargs='?', default=False)
    parser.add_argument('-f', '--filebase', dest='filebase', required=False, default='query_usertimeline', help='the_base_of_the_file')
    parser.add_argument('-b', '--s3-bucket', dest='s3_bucket', required=True, help='s3 bucket, ie s3://leonyin would be leonyin')
    parser.add_argument('--s3-key', dest='s3_key', required=False, help='the path in the bucket.', default='query_machine_stage')
    parser.add_argument('--sudo', dest='sudo_password', nargs='?', default=False, help='sudo pw for machine')
    parser.add_argument('-max', '--max-id', dest='max_id', required=False, help='Max Tweet ID for query.', default=False)
    parser.add_argument('-since', '--since-id', dest='since_id', nargs='?', help='Min Tweet ID for query', default=False)
    parser.add_argument('--start-idx-input', dest='offset', type=int, default=0, help='Start index offset')
    parser.add_argument('--query-date', dest='query_date', default=datetime.datetime.now().strftime("%Y-%m-%d"), help='YYYY-MM-DD')
    return vars(parser.parse_args())


def build_context(args):
    '''
    This creates a dictionary of variables we'll be using throughout the script.
    args are from parse_args
    '''
    context = args

    currentdate = args['query_date']
    currentyear = datetime.datetime.now().strftime("%Y")
    currentmonth = datetime.datetime.now().strftime("%m")
    
    input_name = os.path.splitext(os.path.basename(context['input']))[0]
    output_base = ( context['filebase'] + '__' + currentdate + '__' +
        context['input'].split('/')[-1].replace('.csv', '.json') )

    # local and digital ocean
    if not context['sudo_password']:
        context['sudo_password'] = os.environ.get('SUDO')
    if not context['token']:
        context['token'] = os.environ.get('DO_TOKEN')
    manager = digitalocean.Manager(token=context['token'])
    my_droplets = manager.get_all_droplets()
    vols =  manager.get_all_volumes()
    mydrop = [_ for _ in my_droplets if _.ip_address == get_ip_address()][0]
    context['droplet'] = mydrop
    context['droplet_id'] = mydrop.id
    context['droplet_region'] = mydrop.region['slug']
    
    context['volume_directory'] = os.path.join(
        '/mnt/' + mydrop.name + '-volume'
    )
    context['output'] = os.path.join(
        context['volume_directory'], output_base
    )
    context['log'] = os.path.join(
        context['volume_directory'], output_base.replace('.json', '.log')
    )
    # AWS s3
    context['s3_path'] = os.path.join(
        's3://' + context['s3_bucket'], context['s3_key'], 
        'output/user_timeline', currentyear, currentmonth, 
        output_base + '.bz2'
    )
    context['s3_log'] = os.path.join(
        's3://' + context['s3_bucket'], 'logs', 
        output_base.replace('.json', '.log')
    )
    context['s3_log_done'] = os.path.join(
        's3://' + context['s3_bucket'], context['s3_key'],
        'logs/user_timeline', currentyear, currentmonth,
        output_base.replace('.json', '.log')
    )
    context['s3_auth'] = os.path.join(
        's3://' + context['s3_bucket'], 'tokens/used', 
        os.path.basename(context['auth'])
    )
    
    return context


def twitter_query(context):
    '''
    Gets user ids, and feeds them into a function to query twitter.
    '''
    log('Starting query!')

    output = context['output']
    input_file = context['input']
    auth_file = context['auth']
    max_id = context['max_id']
    since_id = context['since_id']
    offset = context['offset']
        
    id_list = get_id_list(input_file, offset)
    log('creating oauth pool...')
    query_user_tweets(output, id_list, auth_file, max_id=max_id, since_id=since_id)


def query_user_tweets(output, id_list, auth_file, max_id=-1, since_id=-1):
    '''
    queries twitter for users from id_list and authentication from auth_file.
    '''
    num_inputs_queried = 0
    api_pool = TweepyPool(auth_file)
    write_fd = open(output, 'a+')
    for userid in id_list:
        num_inputs_queried = num_inputs_queried + 1
        # even though the count is 200 we can cycle through 3200 items.
        # if you put a count variable in this cursor it will iterate up 
        # to about 3200
        if not userid == '':
            try:
                count = 0
                if max_id and since_id:
                    cursor = Cursor(api_pool.user_timeline, 
                                    user_id=userid, 
                                    count=200, 
                                    max_id=max_id, 
                                    since_id=since_id,
                                    tweet_mode='extended')
                elif max_id:
                    cursor = Cursor(api_pool.user_timeline, 
                                    user_id=userid, 
                                    count=200, 
                                    max_id=max_id,
                                    tweet_mode='extended')
                elif since_id:
                    cursor = Cursor(api_pool.user_timeline, 
                                    user_id=userid, 
                                    count=200, 
                                    since_id=since_id,
                                    tweet_mode='extended')
                else:
                    cursor = Cursor(api_pool.user_timeline, 
                                    user_id=userid, 
                                    count=200,
                                    tweet_mode='extended')

                for item in cursor.items():
                    count = count + 1
                    tweet_item = json.loads(json.dumps(item._json))
                    tweet_item['smapp_timestamp'] = (datetime.datetime.
                        utcnow().strftime('%Y-%m-%d %H:%M:%S +0000'))
                    write_fd.write(json.dumps(tweet_item))
                    write_fd.write('\n')
            except TweepError as e:
                log('tweepy error: {}'.format(e))
            log('counted {} objects for input {}'.format(count, userid))
        log('number of inputs queried so far: {}'.format(num_inputs_queried))
        s3.disk_2_s3(context['log'], context['s3_log'])
    write_fd.close()


if __name__ == '__main__':
    '''
    Parse the input flags,
    create a context dict of all variables we're going to use,
    Check to make sure the machine has a volume attached.
    start a log,
    query twitter,
    compress the returned json object from twitter,
    upload the compressed json and the log to s3
    destroy all files on the volume, detach, destroy.
    '''
    args = parse_args(sys.argv[1:])
    context = build_context(args)
    logging.basicConfig(filename=context['log'], level=logging.INFO)
    
    context['volume'] = check_vol_attached(context)
    if context['volume']: # check if volume is attached
        if not s3.file_exists(context['s3_path']): # check if file exists
            prep_s3(context)
            twitter_query(context)
            context['output_bz2'] = pbzip2(context)
            s3.disk_2_s3(context['output_bz2'], context['s3_path'])
            settle_affairs_in_s3(context)
        detach_and_destroy_volume(context)
    destroy_droplet(context)

 