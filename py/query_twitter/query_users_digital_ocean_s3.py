
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


verbose = 1


def get_ip_address():
    '''
    Gets the IP address of this machine.
    '''
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0]


def destroy_droplet(context):
    '''
    This is where it ends :)
    '''
    droplet = context['droplet']
    droplet.destroy()


def detach_and_destroy_volume(context):
    '''
    Remove all files from the volume, detaches the volume, then destroys it.
    '''
    logger = logging.getLogger(__name__)
    V = context['volume']

    command = 'sudo -S rm -rf /mnt/{}'.format(context['volume_name']).split()
    try:
        p = Popen(command, stdin=PIPE, stderr=PIPE, universal_newlines=True)
        time.sleep(.2)
        sudo_prompt = p.communicate(context['sudo_password'] + '\n')[1]
    except Exception as e:
        if verbose:
            print('Issue clearing the Volume! {}'.format(e))
            logger.info('Issue clearing the Volume! {}'.format(e))

        pass
    
    if verbose:
        print('Detaching volume...')
        logger.info("Detaching volumne...")
    V.detach(droplet_id = context['droplet_id'], 
             region = context['droplet_region'])
    time.sleep(8)
    
    if verbose:
        print('Destorying volume...')
        logger.info("Destroying volumne...")
    V.destroy()
    
    if verbose:
        print("Volume {} Destroyed!".format(context['volume_name']))
        logger.info("Volume {} Destroyed!".format(context['volume_name']))
    

def send_to_s3(context):
    '''
    Uses boto3 to send a the bzipped file to s3.
    '''
    logger = logging.getLogger(__name__)
    f_out = context['output_bz2']
    if verbose:
        print("Sending file to s3".format(f_out))
        logger.info("Sending file to s3".format(f_out))
    
    s3 = boto3.client('s3')
    s3.upload_file(f_out, context['s3_bucket'], context['s3_path'])
    s3.upload_file(context['log'], context['s3_bucket'], context['s3_log'])
    
    if verbose:
        s3_dest = os.path.join('s3://' + context['s3_bucket'], context['s3_path'])
        print("Sent file to {}".format(s3_dest))
        logger.info("Sending file to s3".format(f_out))

def bzip(context):
    '''
    Bzips a file.
    When this is successful, the original file will have disappeared.
    When that happens this returns the new file name with the .bz2 extension.
    '''
    f_out = context['output']
    command = ['/bin/bzip2', f_out]
    process = Popen(command, stdin=PIPE, stderr=PIPE)
    
    while os.path.isfile(f_out):
        time.sleep(1)
        
    return f_out + '.bz2'


def twitter_query(context):
    '''
    Gets user ids, and feeds them into a function to query twitter.
    '''
    logger = logging.getLogger(__name__)
    if verbose:
        print('Starting query!')

    output = context['output']
    input_file = context['input']
    auth_file = context['auth']
        
    id_list = get_id_list(input_file)
    logger.info('creating oauth pool...')

    #query the tweets
    query_user_tweets(output, id_list, auth_file)


def query_user_tweets(output, id_list, auth_file):
    '''
    queries twitter for users from id_list and authentication from auth_file.
    '''
    logger = logging.getLogger(__name__)
    num_inputs_queried = 0

    #create the api pool
    api_pool = TweepyPool(auth_file)

    write_fd = open(output, 'w+')

    for userid in id_list:
        num_inputs_queried = num_inputs_queried + 1
        # even though the count is 200 we can cycle through 3200 items.
        # if you put a count variable in this cursor it will iterate up 
        # to about 3200
        if not userid == '':
            try:
                count = 0
                for item in Cursor(api_pool.user_timeline, user_id=userid, count=200).items():
                    logger.debug('tweet text: %s', item.text) 
                    count = count + 1
                    tweet_item = json.loads(json.dumps(item._json))
                    tweet_item['smapp_timestamp'] = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S +0000')
                    write_fd.write(json.dumps(tweet_item))
                    write_fd.write('\n')
            except TweepError as e:
                logger.info('tweepy error: %s', e)
            logger.info('counted %s objects for input %s', count, userid)
        logger.info('number of inputs queried so far: %s', num_inputs_queried)
    write_fd.close()


def get_id_list(file_input):
    '''
    opens list of user ids to query.
    from the -i arg
    '''
    logger = logging.getLogger(__name__)
    filename, file_extension = os.path.splitext(file_input)
    id_list = []
    if file_extension == '.json':
        logger.info('loading json...')
        id_data = open(file_input).read()
        id_list = json.loads(id_data)
    elif file_extension == '.csv':
        logger.info('loading csv...')
        count = 0
        with open(file_input) as f:
            for rowdict in list(csv.DictReader(f)):
                # if list is not empty
                if rowdict:
                    id_list.append(rowdict['id'])
        logger.info('launching query for %s inputs', len(id_list))
    return id_list


def check_vol_attached(context):
    '''
    Checks to see if a digital ocean volume is attached to the machine.
    Returns False if not, otherwise returns a 
    '''
    manager = digitalocean.Manager(token=context['token'])
    
    vols =  manager.get_all_volumes()
    myvol = [v for v in vols if context['droplet_id'] in v.droplet_ids]
    
    if not myvol: # check if volume is attached.
        return False
    else:
        return myvol[0]


def build_context(args):
    '''
    This creates a dictionary of variables we'll be using throughout the script.
    args are from parse_args
    '''
    context = args
    currentdate = datetime.datetime.now().strftime("%Y-%m-%d")

    # digital ocean
    if not context['token']:
        context['token'] = os.environ.get('DO_TOKEN')
    manager = digitalocean.Manager(token=context['token'])
    my_droplets = manager.get_all_droplets()
    mydrop = [_ for _ in my_droplets if _.ip_address == get_ip_address()][0]

    context['droplet'] = mydrop
    context['droplet_id'] = mydrop.id
    context['volume_name'] = mydrop.name + '-volume'
    context['volume_directory'] = '/mnt/' + context['volume_name']

    output_base = 'query_respondants_' + currentdate + '_' + \
        context['input'].split('/')[-1].replace('.csv', '.json')

    # AWS s3
    context['s3_path'] = os.path.join(
        context['s3_root'], output_base + '.bz2'
    )
    context['s3_log'] = os.path.join(
        context['s3_root'], output_base.replace('.json', '.log')
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


def parse_args(args):
    '''
    Which arguments we'll need
    '''
    parser = argparse.ArgumentParser()

    parser.add_argument('-i', '--input', dest='input', required=True, help='This is a path to your input.json, a [] list of twitter ids.')
    parser.add_argument('-a', '--auth', dest='auth', required=True, help='This is the path to your oauth.json file for twitter')
    parser
    parser.add_argument('-d', '--digital-ocean-token', dest='token', required=False, help='DO access token', const=1, nargs='?', default=False)
    parser.add_argument('-b', '--s3-bucket', dest='s3_bucket', required=True, help='s3 bucket, ie s3://leonyin would be leonyin')
    parser.add_argument('-r', '--s3-root', dest='s3_root', required=True, help='the path in the bucket.')
    parser.add_argument('-s', '--sudo', dest='sudo_password', nargs='?', default=False, help='sudo pw for machine')

    return vars(parser.parse_args())


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
        twitter_query(context)
        context['output_bz2'] = bzip(context)
        send_to_s3(context)
        detach_and_destroy_volume(context)
        destroy_droplet(context)

'''
This script assumes a volume is attached to a digitalocean machine.
It then queries twitter for all timelines for a given user id,
and pools tokens.
Leon Yin 2018-01-16
'''
