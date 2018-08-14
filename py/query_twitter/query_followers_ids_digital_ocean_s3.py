'''
Queries twitter for user metadata of followers of the input users.

The output is one json file of user metadata per input user.
So for 60 inputs, we get 60 json files.

There's no need to attach a volume for this query.
Tokens are pooled using tkpool.

https://developer.twitter.com/en/docs/accounts-and-users/follow-search-get-users/api-reference/get-followers-ids

Leon Yin 2017-11-06
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
    parser.add_argument('--cursor', dest='cursor', type=int, default=-1, help='the cursor to query')

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
    context['currentyear'], context['currentmonth'] = currentyear, currentmonth
    output_base = ( context['filebase'] + '__' + currentdate + '__' +
        context['input'].split('/')[-1].replace('.csv', '') )

    # local stuff
    context['currentdate'] = currentdate
    context['volume_directory'] = 'pylogs/'
    context['log'] = os.path.join(
        context['volume_directory'], output_base + '.log'
    )
    
    context['input'] = download_from_s3(context['input']) if 's3://' in context['input'] else context['input']
    context['auth'] = download_from_s3(context['auth']) if 's3://' in context['auth'] else context['auth']

    # digital ocean
    if not context['token']: 
        context['token'] = os.environ.get('DO_TOKEN')
    manager = digitalocean.Manager(token=context['token'])
    my_droplets = manager.get_all_droplets()
    vols =  manager.get_all_volumes()
    mydrop = [_ for _ in my_droplets if _.ip_address == get_ip_address()][0]
    context['droplet'] = mydrop
    context['droplet_id'] = mydrop.id
    
    # s3 stuff
    context['s3_path'] = os.path.join(
        's3://' + context['s3_bucket'], context['s3_key'],
        'output/follower_ids/',
    )
    context['s3_log'] = os.path.join(
        's3://' + context['s3_bucket'], 'logs', output_base + '.log'
    )
    context['s3_log_done'] = os.path.join(
        's3://' + context['s3_bucket'], context['s3_key'],
        'logs/follower_ids/', currentyear, currentmonth, 
        output_base + '.log'
    )
    context['s3_auth'] = os.path.join(
        's3://' + context['s3_bucket'], 'tokens/used', 
        os.path.basename(context['auth'])
    )

    return context


def get_user_id_file(user_id, context):
    '''
    File locations for user_id csv files.
    '''
    filename = os.path.join(context['volume_directory'], user_id + '.csv')
    s3_filename = os.path.join(context['s3_path'], user_id, 
        context['currentyear'], context['currentmonth'],
        user_id  + '.csv')    
    s3_id_key = os.path.join(context['s3_path'], user_id)

    return filename, s3_filename, s3_id_key


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
    api_pool = kids_pool(auth_file, start_idx=start_idx, verbose=1)
    
    for i, user_id in enumerate( id_list[ offset : ] ):
        if i == 0: # first cursor, only if flag is set.
            cursor = context['cursor']
        else:
            cursor = -1
        filename, s3_filename, s3_id_key = get_user_id_file(user_id, context)
        if not s3.exists(s3_id_key):
            query_user_followers_ids(filename, user_id, api_pool, cursor=cursor)
            log('Sending file to s3: {}'.format(s3_filename))
            s3.disk_2_s3(filename, s3_filename)
            s3.disk_2_s3(context['log'], context['s3_log'])
            os.remove(filename)
            # send an update to s3 after each iteration!
            s3.disk_2_s3(context['log'], context['s3_log'])
        else: 
            log('{} already queried!!!'.format(user_id))
        log('>>> {} out of {}'.format(i + offset, len(id_list)))
        time.sleep(1)


def query_user_followers_ids(filename, user_id, api_pool, cursor):
    '''
    Queries twitter for followers ids from id_list.
    '''
    log("Working on {}".format(user_id))
    creds = api_pool.get_current_api_creds()
    function = 'followers/ids'
    the_url = "https://api.twitter.com/1.1/{}.json".format(function)
    
    id_count = 0
    while cursor != 0: 
        api_pool.set_increment()
        if api_pool.get_current_api_calls() % 15 == 0:
            api_pool.find_next_token()
            creds = api_pool.get_current_api_creds()
        
        parameters = [('user_id', user_id),
                      ('cursor', cursor)]
        try:
            out = twitterreq(the_url, creds=creds, parameters=parameters)
            resp_code = out.code
        except SocketError as e: #connection reset by peer
            log(e)
            resp_code = 104
        
        if resp_code == 200:
            try:
                response = json.loads(out.read().decode('utf-8'))
                new_ids = response["ids"]            
                if len(new_ids) == 0:
                    df = pd.DataFrame([None])
                else:
                    df = pd.DataFrame(new_ids, dtype=str)
                df.columns = ['user_id_followers']
                if cursor == -1: 
                    df.to_csv(filename, index=False)
                else: 
                    df.to_csv(filename, index=False, header=False, mode='a')
                cursor = response["next_cursor"] # want to record this
                id_count += len(new_ids)
                log("User id: {} Next_Cursor: {} Total_IDs:{}".format(
                    user_id, cursor, id_count))
                time.sleep(1)
            
            except SocketError as e: # 104 sometimes shows up when we read the out.
                log("Likely a 104 error! {}".format(e))
                time.sleep(60 * 60)
        
        elif resp_code in [404, 400, 410, 422, 401]: # error with data, log it, 401 means private user!
            df = pd.DataFrame([out.code])
            df.columns = ['user.id']
            if cursor == -1: 
                df.to_csv(filename, index=False)
            else: 
                if len(df) > 1:
                    df.to_csv(filename, index=False, header=False, mode='a')            
            log("User id: {} fruitless with error {}".format(user_id, resp_code))
            cursor = 0

        elif resp_code in [420, 429, 406]: # rate limited, try again
            log("User id: {} rate limited with error {}".format(user_id, resp_code))
            time.sleep(901)
            api_pool.find_next_token()
            creds = api_pool.get_current_api_creds()

        elif resp_code in [500, 502, 503, 504, 104]: # server error, wait, try again.
            log("User id: {} server error {}".format(user_id, resp_code))
            time.sleep(60 * 60)

        else: # some other error, just break...
            log("User id: {} unknown error {}".format(user_id, resp_code))
            break
       

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
    prep_s3(context)
    twitter_query(context)
    settle_affairs_in_s3(context)
    destroy_droplet(context)

