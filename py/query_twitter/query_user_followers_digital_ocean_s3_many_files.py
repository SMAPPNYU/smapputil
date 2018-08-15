'''
Queries twitter for user metadata of followers of the input users.

The output is one json file of user metadata per input user.
So for 60 inputs, we get 60 json files.

There's no need to attach a volume for this query.
Tokens are pooled using tkpool.

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

import s3
import digitalocean
from tweepy import Cursor, TweepError


from tkpool.tkpool.tweepypool import TweepyPool
from utils import *


def parse_args(args):
    '''
    Which arguments we'll need
    '''
    parser = argparse.ArgumentParser()

    parser.add_argument('-s3', '--s3-input', dest='s3_input', required=True, help='This is a path to your input cvs on s3. is s3://smapp-dev/project-quries/myproject/input/users_to_query.csv')
    parser.add_argument('--filebase', dest='filebase', nargs='?', default='twitter_query', help='the_base_of_the_file')
    parser.add_argument('-d', '--digital-ocean-token', dest='token', required=False, help='DO access token', const=1, nargs='?', default=False)
    parser.add_argument('--start-idx-api', dest='start_idx_api', type=int, default=0, help='the first token to use')
    parser.add_argument('--start-idx-input', dest='start_idx_input', type=int, default=0, help='the first input to query')
    
    parser.add_argument('-n', '--n-tokens', dest='n_tokens', type=int, default=60, help='the number of tokens to use')
    
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
    input_filename = os.path.basename(context['s3_input'])
    output_base = context['filebase'] + '__' + currentdate + '__' + \
                  input_filename.replace('.csv', '.json') 
    
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
    context['volume_directory'] = 'pylogs/'
    
    # AWS s3
    if 's3://' not in context['s3_input']:
        raise "Improperly formatted -s3 or --s3-input flag"
    context['input'] = download_from_s3(context['s3_input'], new_dir='pylogs/')
    context['auth'] = 'pylogs/{}__{}__tokens.json'.format(mydrop.id, currentdate)
    context['s3_bucket'] = s3.get_bucket(context['s3_input'])
    context['s3_key'] = context['s3_input'].split('input/')[0]
    context['s3_path'] = os.path.join(
        context['s3_key'], 
        'output/user_friends_many/',
    )
    context['s3_log'] = os.path.join(
        's3://' + context['s3_bucket'], 'logs', 
        output_base.replace('.json', '.log')
    )
    context['s3_log_done'] = os.path.join(
        context['s3_key'],
        'logs/user_friends_many/', currentyear, currentmonth, 
        output_base.replace('.json', '.log')
    )
    context['s3_auth'] = os.path.join(
        's3://' + context['s3_bucket'], 'tokens/used', 
        os.path.basename(context['auth'])
    )
    
     # local stuff
    context['user'] = os.environ.get('USER')
   
    context['output'] = os.path.join(
        context['volume_directory'], output_base
    )
    context['log'] = os.path.join(
        context['volume_directory'], 
        output_base.replace('.json', '.log')
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
    api_pool = TweepyPool(auth_file)
    for i, user_id in enumerate(id_list[ offset : ]):
        filename, s3_filename = get_user_id_file(user_id, context)
        if not s3.file_exists(s3_filename):
            log('writing user id: {} here'.format(user_id, filename)) 

            with open(filename, 'w+') as write_fd:
                for item in Cursor(api_pool.followers, id=user_id, count=5000).items():
                    tweet_item = json.loads(json.dumps(item._json))
                    tweet_item['smapp_original_user_id'] = user_id
                    tweet_item['smapp_timestamp'] = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S +0000')
                    write_fd.write(json.dumps(tweet_item)+ '\n')

            log('Sending file to s3: {}'.format(s3_filename))
            s3.disk_2_s3(filename, s3_filename)
            s3.disk_2_s3(context['log'], context['s3_log'])
            os.remove(filename)
        else: 
            log('{} already queried!!!'.format(user_id))
        log('>>> {} out of {}'.format(i + offset, len(id_list)))
        time.sleep(1)


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
        create_token_files(context)
        prep_s3(context)
        twitter_query(context)
        settle_affairs_in_s3(context)
        detach_and_destroy_volume(context)
        destroy_droplet(context)

