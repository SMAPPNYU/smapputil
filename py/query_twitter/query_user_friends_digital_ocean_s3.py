'''
This script assumes a volume is attached to a digitalocean machine.

It then queries twitter for user metadata of followers for a given user id
and pools tokens.

One json file will be returned by a query. 
Each Json will have the user metadata from multiple input users.

Leon Yin 2017-11-06
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

import boto3
import digitalocean
from tkpool.tkpool.tweepypool import TweepyPool
from tweepy import Cursor, TweepError

from utils import *


def parse_args(args):
    '''
    Which arguments we'll need
    '''
    parser = argparse.ArgumentParser()

    parser.add_argument('-i', '--input', dest='input', required=True, help='This is a path to your input.json, a [] list of twitter ids.')
    parser.add_argument('-a', '--auth', dest='auth', required=True, help='This is the path to your oauth.json file for twitter')
    parser.add_argument('-f', '--filebase', dest='filebase', required=False, default='twitter_query', help='the_base_of_the_file')
    parser.add_argument('--digital-ocean-token', dest='token', required=False, help='DO access token', const=1, nargs='?', default=False)
    parser.add_argument('--s3-bucket', dest='s3_bucket', required=True, help='s3 bucket, ie s3://leonyin would be leonyin')
    parser.add_argument('--s3-key', dest='s3_key', required=True, help='the path in the bucket.')
    parser.add_argument('--sudo', dest='sudo_password', nargs='?', default=False, help='sudo pw for machine')

    return vars(parser.parse_args())


def build_context(args):
    '''
    This creates a dictionary of variables we'll be using throughout the script.
    args are from parse_args
    '''
    context = args
    currentdate = datetime.datetime.now().strftime("%Y-%m-%d")
    currentyear = datetime.datetime.now().strftime("%Y")
    currentmonth = datetime.datetime.now().strftime("%m")

    # digital ocean
    if not context['token']:
        context['token'] = os.environ.get('DO_TOKEN')
    manager = digitalocean.Manager(token=context['token'])
    my_droplets = manager.get_all_droplets()
    vols =  manager.get_all_volumes()

    mydrop = [_ for _ in my_droplets if _.ip_address == get_ip_address()][0]

    context['droplet'] = mydrop
    context['droplet_id'] = mydrop.id
    context['droplet_region'] = mydrop.region['slug']

    context['volume_name'] = mydrop.name + '-volume'
    context['volume_directory'] = '/mnt/' + context['volume_name']


    output_base = context['file_root'] + currentdate + '_' + \
        context['input'].split('/')[-1].replace('.csv', '.json')

    # AWS s3
    context['s3_path'] = os.path.join(
        's3://', context['s3_bucket'], context['s3_key'], 
        'output/user_friends/', currentyear, currentmonth,
        output_base + '.bz2'
    )
    context['s3_log'] = os.path.join(
        's3://', context['s3_bucket'], context['s3_key'], 
        'output/user_friends/',  currentyear, currentmonth,
        output_base.replace('.json', '.log')
    )
    
     # local stuff
    context['user'] = os.environ.get('USER')
    if not context['sudo_password']:
        context['sudo_password'] = os.environ.get('SUDO')
    
    context['output'] = os.path.join(
        context['volume_directory'], output_base
    )
    context['log'] = os.path.join(
        context['volume_directory'], output_base.replace('.json', '.log')
    )
    
    return context


def twitter_query(context):
    '''
    Gets user ids, and feeds them into a function to query twitter.
    '''
    output = context['output']
    input_file = context['input']
    auth_file = context['auth']

    log('creating oauth pool...')
    id_list = get_id_list(input_file)

    log('creating oauth pool...')
    api_pool = TweepyPool(auth_file)

    log('starting query...')
    num_inputs_queried = 0
    with open(output, 'w+') as write_fd:
        for user_id in id_list:
            num_inputs_queried = num_inputs_queried + 1
            if not user_id == '':
                try:
                    count = 0
                    for item in Cursor(api_pool.friends, id=user_id, count=5000).items():
                        log('user id: {},  and screen_name {}'.format(item.id, item.screen_name)) 
                        count = count + 1
                        tweet_item = json.loads(json.dumps(item._json))
                        tweet_item['smapp_original_user_id'] = user_id
                        tweet_item['smapp_timestamp'] = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S +0000')
                        write_fd.write(json.dumps(tweet_item) + '\n')
                except TweepError as e:
                    log('tweepy error: {}'.format(e))
                
                # update the logs and send to s3
                log('counted {} objects for input {}'.format(count, userid))
                s3.disk_2_s3(context['log'], context['s3_log'])

            log('number of inputs queried so far: {}'.format(num_inputs_queried))
            s3.disk_2_s3(context['log'], context['s3_log'])


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
    if context['volume']:
        prep_s3(context)
        twitter_query(context)
        context['output_bz2'] = pbzip2(context)
        s3.disk_2_s3(context['output_bz2'], context['s3_path'])
        settle_affairs_in_s3(context)
        detach_and_destroy_volume(context)
        destroy_droplet(context)

