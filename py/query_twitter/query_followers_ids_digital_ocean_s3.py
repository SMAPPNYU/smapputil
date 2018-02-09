import os
import sys
import csv
import json
import time
import socket
import argparse
import datetime
import logging
from subprocess import Popen, PIPE

import pandas as pd
import digitalocean

from kidspool.kidspool import kids_pool
from twitter_api.twitter_api import twitterreq
import s3

verbose = 1


def destroy_droplet(context):
    '''
    This is where it ends :)
    '''
    droplet = context['droplet']
    droplet.destroy()


def get_user_id_file(user_id, context):
    '''
    File locations for user_id csv files.
    '''
    filename = os.path.join(context['volume_directory'], user_id + '.csv')
    s3_filename = os.path.join(context['s3_path'], user_id, 
        user_id + '__' + context['currentdate'] + '.csv')
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
    api_pool = kids_pool(auth_file, start_idx=start_idx, verbose=verbose)
    
    for i, user_id in enumerate( id_list[ offset : ] ):
        if i == 0: # first cursor.
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
        else: log('{} already queried!!!'.format(user_id))
        log('>>> {} out of {}'.format(i + offset, len(id_list)))
        time.sleep(.1)


def query_user_followers_ids(filename, user_id, api_pool, cursor):
    '''
    Queries twitter for friends ids from id_list.
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
        out = twitterreq(the_url, 
                         creds = creds,
                         parameters = parameters)
        resp_code = out.code
        if resp_code == 200:
            response = json.loads(out.read().decode('utf-8'))
            new_ids = response["ids"]            
            if len(new_ids) == 0:
                df = pd.DataFrame([None])
            else:
                df = pd.DataFrame(new_ids)
            df.columns = ['user.id']
            if cursor == -1: 
                df.to_csv(filename, index=False)
            else: 
                df.to_csv(filename, index=False, header=False, mode='a')
            cursor = response["next_cursor"] # want to record this
            id_count += len(new_ids)
            log("User id: {} Cursor: {} Total_IDs:{}".format(user_id, cursor, id_count))
            time.sleep(1)

        elif resp_code in [404, 400, 410, 422, 401]: # error with data, log it, leave.
            df = pd.DataFrame([out.code])
            df.columns = ['user.id']
            if cursor == -1: 
                df.to_csv(filename, index=False)
            else: 
                df.to_csv(filename, index=False, header=False, mode='a')            
            log("User id: {} fruitless with error {}".format(user_id, resp_code))
            cursor = 0

        elif resp_code in [420, 429, 406]: # rate limited, try again
            log("User id: {} rate limited with error {}".format(user_id, resp_code))
            time.sleep(901)
            api_pool.find_next_token()
            creds = api_pool.get_current_api_creds()

        elif resp_code in [500, 502, 503, 504, 104]: # server error, wait.
            log("User id: {} server error {}".format(user_id, resp_code))
            time.sleep(100)

        else: # some other error, just break...
            log("User id: {} unknown error {}".format(user_id, resp_code))

            break

def get_id_list(file_input):
    '''
    Opens list of user ids to query.
    '''
    filename, file_extension = os.path.splitext(file_input)
    id_list = []
    if file_extension == '.json':
        log('loading json...')
        id_data = open(file_input).read()
        id_list = json.loads(id_data)
    elif file_extension == '.csv':
        log('loading csv...')
        with open(file_input) as f:
            for rowdict in list(csv.DictReader(f)):
                if rowdict:
                    id_list.append(rowdict['id'])
        log('{} inputs to query.'.format(len(id_list)))
    return id_list


def get_ip_address():
    '''
    Gets the IP address of this machine.
    '''
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0]


def log(msg):
    '''
    Records messages and prints if verbose.
    '''
    logger = logging.getLogger(__name__)
    if verbose: print(msg)
    logger.info(msg)


def build_context(args):
    '''
    This creates a dictionary of variables we'll be using throughout the script.
    args are from parse_args
    '''
    context = args
    currentdate = datetime.datetime.now().strftime("%Y-%m-%d")
    output_base = context['filebase'] + '_' + currentdate + '_' + \
        context['input'].split('/')[-1].replace('.csv', '')

    if not context['token']: 
        context['token'] = os.environ.get('DO_TOKEN')
    if not context['sudo_password']: 
        context['sudo_password'] = os.environ.get('SUDO')

    manager = digitalocean.Manager(token=context['token'])
    my_droplets = manager.get_all_droplets()
    vols =  manager.get_all_volumes()
    mydrop = [_ for _ in my_droplets if _.ip_address == get_ip_address()][0]
    
    context['user'] = os.environ.get('USER')
    context['currentdate'] = currentdate
    context['droplet'] = mydrop
    context['droplet_id'] = mydrop.id
    context['volume_directory'] = 'pylogs/' #+ context['volume_name']
    context['s3_path'] = os.path.join('s3://' + context['s3_bucket'], context['s3_key'])
    context['s3_log'] = os.path.join('s3://' + context['s3_bucket'],'logs', output_base + '.log')
    context['log'] = os.path.join(context['volume_directory'], output_base + '.log')
    return context


def parse_args(args):
    '''
    Parses the input arguments.
    '''
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', dest='input', required=True, help='This is a path to your input.json, a [] list of twitter ids.')
    parser.add_argument('-a', '--auth', dest='auth', required=True, help='This is the path to your oauth.json file for twitter')
    parser.add_argument('-f', '--filebase', dest='filebase', required=False, default='twitter_query', help='the_base_of_the_file')
    parser.add_argument('-d', '--digital-ocean-token', dest='token', required=False, help='DO access token', const=1, nargs='?', default=False)
    parser.add_argument('-b', '--s3-bucket', dest='s3_bucket', required=True, help='s3 bucket, ie s3://leonyin would be leonyin')
    parser.add_argument('-r', '--s3-key', dest='s3_key', required=True, help='the path in the bucket.')
    parser.add_argument('-s', '--sudo', dest='sudo_password', nargs='?', default=False, help='sudo pw for machine')
    parser.add_argument('--start-idx-api', dest='start_idx_api', type=int, default=0, help='the first token to use')
    parser.add_argument('--start-idx-input', dest='start_idx_input', type=int, default=0, help='the first input to query')
    parser.add_argument('--cursor', dest='cursor', type=int, default=-1, help='the cursor to query')

    return vars(parser.parse_args())


if __name__ == '__main__':
    args = parse_args(sys.argv[1:])
    context = build_context(args)
    logging.basicConfig(filename=context['log'], level=logging.INFO)
    
    twitter_query(context)
    s3.disk_2_s3(context['log'], context['s3_log'])
    destroy_droplet(context)

'''
This script assumes a volume is attached to a digitalocean machine.
It then queries twitter for all timelines for a given user id,
and pools tokens.
Leon Yin 2018-02-02
'''
