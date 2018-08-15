'''
Queries Twitter for user metadata for input users.
Output is many json files (one per input user) where each file has new line delimited
json objects of user metadata

This script does not need a volume attached to a digitalocean machine.

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
    parser.add_argument('-s3', '--s3-input', dest='s3_input', required=True, help='This is a path to your input cvs on s3. is s3://smapp-dev/project-quries/myproject/input/users_to_query.csv')
    parser.add_argument('-f', '--filebase', dest='filebase', required=False, default='user_lookup_many', help='the_base_of_the_file')
    parser.add_argument('-d', '--digital-ocean-token', dest='token', required=False, help='DO access token', const=1, nargs='?', default=False)
    parser.add_argument('--start-idx-api', dest='start_idx_api', type=int, default=0, help='the first token to use')
    parser.add_argument('--start-idx-input', dest='start_idx_input', type=int, default=0, help='the first input to query')
    parser.add_argument('--query-date', dest='query_date', default=datetime.datetime.now().strftime("%Y-%m-%d"), help='YYYY-MM-DD')
    parser.add_argument('-n', '--n-tokens', dest='n_tokens', type=int, default=60, help='the number of tokens to use')
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
    input_filename = os.path.basename(context['s3_input'])
    output_base = context['filebase'] + '__' + currentdate + '__' + \
                  input_filename.replace('.csv', '') 
    
    # local stuff
    context['currentdate'] = currentdate
    context['volume_directory'] = 'pylogs/'
    context['log'] = os.path.join(
        context['volume_directory'], 
        output_base + '.log'
    )
    
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
    if 's3://' not in context['s3_input']:
        raise "Improperly formatted -s3 or --s3-input flag"
    context['input'] = download_from_s3(context['s3_input'], new_dir='pylogs/')
    context['auth'] = 'pylogs/{}__{}__tokens.json'.format(mydrop.id, currentdate)
    context['s3_bucket'] = s3.get_bucket(context['s3_input'])
    context['s3_key'] = context['s3_input'].split('input/')[0]
    context['s3_path'] = os.path.join(
        context['s3_key'],
        'output/user_meta_many/' #, currentyear, currentmonth,
    )
    context['s3_log'] = os.path.join(
        's3://' + context['s3_bucket'], 'logs', 
        output_base + '.log'
    )
    context['s3_log_done'] = os.path.join(
        context['s3_key'],
        'logs/user_meta_many/', currentyear, currentmonth, 
        output_base + '.log'
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


def get_user_id_file(user_id, context):
    '''
    File locations for user_id csv files.
    '''
    filename = os.path.join(context['volume_directory'], user_id + '.json')
    s3_filename = os.path.join(context['s3_path'], user_id + '.json')
    s3_id_key = os.path.join(context['s3_path'], user_id)

    return filename, s3_filename, s3_id_key


def user_not_downloaded(u_id, context):
    '''
    Check if the user_id has already been processed.
    '''
    filename, s3_filename, s3_id_key = get_user_id_file(
        str(u_id), context)
    if not s3.file_exists(s3_filename):
        return True
    return False


def process_row(row, context):
    '''
    Parses JSON response from Twitter API.
    Writes to local disk and then sents to s3.
    '''
    user_meta = row.copy()
    user_meta['smapp_timestamp'] = (datetime.datetime.
        utcnow().strftime('%Y-%m-%d %H:%M:%S +0000'))
    filename, s3_filename, s3_id_key = get_user_id_file(
        str(user_meta['id']), 
        context
    )
    with open(filename, 'w+') as f:
        f.write(json.dumps(user_meta) + '\n')

    # move to s3.
    s3.disk_2_s3(filename, s3_filename)
    os.remove(filename)


def query_user_meta(user_id, api_pool, context):
    '''
    Queries twitter for followers ids from id_list.
    '''
    creds = api_pool.get_current_api_creds()
    function = 'users/lookup'
    the_url = "https://api.twitter.com/1.1/{}.json".format(function)

    # filter users ABD
    user_id = [u_id for u_id in user_id if user_not_downloaded(u_id, context)]

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
    create_token_files(context)
    prep_s3(context)
    twitter_query(context)
    settle_affairs_in_s3(context)
    destroy_droplet(context)

