'''
Queries Twitter for user metadata for input users.
Output is one json file that is new line delimited
json objects of user metadata

This script assumes a volume is attached to a digitalocean machine.

This script pools tokens using the kidspool class -- which should be in the directory where this lives.
We use the Twitter restful API (not tweepy) via twitter_api, to interact with Twitter.

https://developer.twitter.com/en/docs/accounts-and-users/follow-search-get-users/api-reference/get-users-lookup

Leon Yin 2018-02-14
updated 2018-08-06
'''

import os
import sys
import csv
import json
import time
import socket
from socket import error as SocketError
import argparse
import datetime
import logging

import s3
from subprocess import Popen, PIPE
import pandas as pd
import digitalocean

from kidspool.kidspool import kids_pool
from twitter_api.twitter_api import twitterreq

from utils import *
        
def parse_args(args):
    '''
    Parses the input arguments.
    '''
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', dest='input', required=True, help='This is a path to your input(csv or json), a [] list of twitter ids.')
    parser.add_argument('-a', '--auth', dest='auth', required=True, help='This is the path to your oauth.json file for twitter')
    parser.add_argument('-f', '--filebase', dest='filebase', required=False, default='twitter_query', help='the_base_of_the_file')
    parser.add_argument('-d', '--digital-ocean-token', dest='token', required=False, help='DO access token', const=1, nargs='?', default=False)
    parser.add_argument('-b', '--s3-bucket', dest='s3_bucket', required=True, help='s3 bucket, ie s3://leonyin would be leonyin')
    parser.add_argument('-r', '--s3-key', dest='s3_key', required=True, help='the path in the bucket.')
    parser.add_argument('--start-idx-api', dest='start_idx_api', type=int, default=0, help='the first token to use')
    parser.add_argument('--start-idx-input', dest='start_idx_input', type=int, default=0, help='the first input to query')
    parser.add_argument('--query-date', dest='query_date', default=datetime.datetime.now().strftime("%Y-%m-%d"), help='YYYY-MM-DD')

    return vars(parser.parse_args())


def build_context(args):
    '''
    This creates a dictionary of variables we'll be using throughout the script.
    args are from parse_args
    '''
    context = args
    
    currentdate = context['query_date']
    currentyear = datetime.datetime.now().strftime("%Y")
    currentmonth = datetime.datetime.now().strftime("%m")
    output_base = ( context['filebase'] + '__' + currentdate + '__' +
        context['input'].split('/')[-1].replace('.csv', '.json') )
    
    # local stuff
    context['currentdate'] = currentdate

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

    context['output'] = os.path.join(
        context['volume_directory'], output_base
    )
    context['log'] = os.path.join(
        context['volume_directory'], output_base.replace('.json', '.log')
    )
    
    # s3 stuff
    context['s3_path'] = os.path.join(
        's3://' + context['s3_bucket'], context['s3_key'],
        'output/user_meta', currentyear, currentmonth,
        output_base + '.bz2'
    )
    context['s3_log'] = os.path.join(
        's3://' + context['s3_bucket'], 'logs', 
        output_base.replace('.json', '.log')
    )
    context['s3_log_done'] = os.path.join(
        's3://' + context['s3_bucket'], context['s3_key'],
        'logs/user_meta', currentyear, currentmonth, 
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
    input_file = context['input']
    auth_file = context['auth']
    id_list = get_id_list(input_file)
    offset = context['start_idx_input']
    start_idx = context['start_idx_api']
    
    log('Creating oauth pool...')
    api_pool = kids_pool(auth_file, start_idx=start_idx, verbose=verbose)
    query_user_meta(id_list[ offset : ], api_pool, context)


def process_row(row, context):
    '''
    Parses JSON response from Twitter API.
    Writes to local disk and then sents to s3.
    '''
    user_meta = row.copy()
    user_meta['smapp_timestamp'] = (datetime.datetime.
        utcnow().strftime('%Y-%m-%d %H:%M:%S +0000'))
    with open(context['output'], 'a+') as f:
        f.write(json.dumps(user_meta))


def query_user_meta(user_id, api_pool, context):
    '''
    Queries twitter for followers ids from id_list.
    '''
    creds = api_pool.get_current_api_creds()
    function = 'users/lookup'
    the_url = "https://api.twitter.com/1.1/{}.json".format(function)

    # chunk the user_ids into lists of 100 per API call.
    id_count = 0
    for i, user_chunks in enumerate(chunker(user_id, 100)):
        api_pool.set_increment()
        if api_pool.get_current_api_calls() % 300 == 0:
            api_pool.find_next_token()
            creds = api_pool.get_current_api_creds()
        
        parameters = [('user_id', ','.join(user_chunks))]
        try:
            out = twitterreq(the_url, creds=creds, parameters=parameters)
            resp_code = out.code
        except SocketError as e: #connection reset by peer
            log(e)
            resp_code = 104
        
        if resp_code == 200:
            try:
                response = json.loads(out.read().decode('utf-8'))
                for row in response:
                    process_row(row, context)
                id_count += len(response)
                log("Iternation: {} Total_IDs: {}".format(i, id_count))
                time.sleep(1)
            
            except SocketError as e: # 104 sometimes shows up when we read the out.
                log("Likely a 104 error! {}".format(e))
                time.sleep(60 * 60)
        
        elif resp_code in [404, 400, 410, 422, 401]: # error with data, log it, 401 means private user!
            
            log("Iteration: {} fruitless with error {}".format(i, resp_code))

        elif resp_code in [420, 429, 406]: # rate limited, try again
            log("Iternation: {} rate limited with error {}".format(i, resp_code))
            time.sleep(901)
            api_pool.find_next_token()
            creds = api_pool.get_current_api_creds()

        elif resp_code in [500, 502, 503, 504, 104]: # server error, wait, try again.
            log("Iternation: {} server error {}".format(i, resp_code))
            time.sleep(60 * 60)

        else: # some other error, just break...
            log("Iternation: {} unknown error {}".format(i, resp_code))
            break

        # send an update to s3 after each iteration!
        s3.disk_2_s3(context['log'], context['s3_log'])


if __name__ == '__main__':
    '''
    This script downloads friends or follower ids locally as csv files,
    after each sucessful download, the log and the csv are uploaded to s3.
    When all users have been successfully downloaded, the credits are freed up,
    and the log is moved to the archive.
    The DO machine used for this query is then destroyed.
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


