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


s3_bucket = 'smapp-nyu'
s3_path = 'query_machine_stage'
volume_size_gbs = 2
droplet_reigon = 'nyc1'
verbose = 1


def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0]

def create_and_attach_volume(context, size_gigabytes=800):
    '''
    TODO: remove the mount if it exists!
    '''
    commands = [
        'sudo -S rm -rf /mnt/{VOL_NAME}',
        'sudo -S mkdir -p /mnt/{VOL_NAME}',
        'sudo -S mount -o discard,defaults /dev/disk/by-id/scsi-0DO_Volume_{VOL_NAME} /mnt/{VOL_NAME}',
        'echo /dev/disk/by-id/scsi-0DO_Volume_{VOL_NAME} /mnt/{VOL_NAME} ext4 defaults,nofail,discard 0 0 | sudo -S tee -a /etc/fstab',
        'sudo -S chown {USER}:{USER} /mnt/{VOL_NAME}'
    ]
    
    V = context['volume']
    
    try:
        if verbose:
            print("creating volume" + context['volume_name'])
        V.create()
    except Exception as e:
        if verbose:
            print("Issue attaching creating volume. {}".format(e))
        pass
    
    time.sleep(5)
    
    try:
        if verbose:
            print("connecting volume" + context['volume_name'])
        V.attach(droplet_id = context['droplet_id'], 
                 region = context['droplet_reigon'])
    except Exception as e:
        if verbose:
            print("Issue attaching volume. {}".format(e))
#         return False
        pass
    
    time.sleep(5)
    
    for command in commands:
        command = command.format(VOL_NAME=context['volume_name'], 
                                 USER=context['user']).split()
        p = Popen(command, stdin=PIPE, stderr=PIPE, universal_newlines=True)
        time.sleep(.2)
        sudo_prompt = p.communicate(context['sudo_password'] + '\n')[1]
        
    if verbose:
        print("Volume {} configred!".format(context['volume_name']))
   
    return True

def destroy(context):
    '''
    This is where it ends :)
    '''
    droplet = context['droplet']
    droplet.destroy()

def detach_and_destroy_volume(context):
    '''
    Remove all files from the volume, detaches the volume, then destroys it.
    '''
    V = context['volume']

    command = 'sudo -S rm -rf /mnt/{}'.format(context['volume_name']).split()
    try:
        p = Popen(command, stdin=PIPE, stderr=PIPE, universal_newlines=True)
        time.sleep(.2)
        sudo_prompt = p.communicate(context['sudo_password'] + '\n')[1]
    except Exception as e:
        if verbose:
            print('Issue clearing the Volume! {}'.format(e))
        pass
    
    if verbose:
        print('Detaching volume...')
    V.detach(droplet_id = context['droplet_id'], 
             region = context['droplet_reigon'])
    time.sleep(8)
    
    if verbose:
        print('Destorying volume...')
    V.destroy()
    
    if verbose:
        print("Volume {} Destroyed!".format(context['volume_name']))
    

def send_to_s3(context):
    f_out = context['output_bz2']
    if verbose:
        print("Sending file to s3".format(f_out))
    
    s3 = boto3.client('s3')
    s3.upload_file(f_out, context['s3_bucket'], context['s3_path'])
    s3.upload_file(context['log'], context['s3_bucket'], context['s3_log'])
    
    if verbose:
        s3_dest = os.path.join('s3://' + context['s3_bucket'], context['s3_path'])
        print("Sent file to {}".format(s3_dest))

def bzip(context):
    f_out = context['output']
    command = ['/bin/bzip2', f_out]
    process = Popen(command, stdin=PIPE, stderr=PIPE)
    
    while os.path.isfile(f_out):
        time.sleep(1)
        
    return f_out + '.bz2'

def twitter_query(context):
    if verbose:
        print('Starting query!')
    
    output = context['output']
    input_file = context['input']
    auth_file = context['auth']
    
    logger = logging.getLogger(__name__)
    
    id_list = get_id_list(input_file)
    logger.info('creating oauth pool...')

    #query the tweets
    query_user_tweets(output, id_list, auth_file)

def query_user_tweets(output, id_list, auth_file):

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

def parse_args(args):
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', dest='input', required=True, help='This is a path to your input.json, a [] list of twitter ids.')
    parser.add_argument('-a', '--auth', dest='auth', required=True, help='This is the path to your oauth.json file for twitter')
    
    return vars(parser.parse_args())

def build_context(args):
    context = args
    currentdate = datetime.datetime.now().strftime("%Y-%m-%d")
    
    # digital ocean
    context['token'] = os.environ.get('DO_TOKEN')
    manager = digitalocean.Manager(token=context['token'])
    my_droplets = manager.get_all_droplets()
    mydrop = [_ for _ in my_droplets if _.ip_address == get_ip_address()][0]
    
    context['droplet'] = mydrop
    context['droplet_id'] = mydrop.id
    context['volume_name'] = mydrop.name + '-volume'
    context['volume_directory'] = '/mnt/' + context['volume_name']
    context['droplet_reigon'] = droplet_reigon
    context['volume'] = digitalocean.Volume(
        token= context['token'],
        name= context['volume_name'],
        region= context['droplet_reigon'],
        size_gigabytes= volume_size_gbs
    )
    output_base = 'query_respondants_' + currentdate + '_' + \
        context['input'].split('/')[-1].replace('.csv', '.json')

    # AWS s3
    context['s3_bucket'] = s3_bucket
    context['s3_path'] = os.path.join(
        s3_path, output_base + '.bz2'
    )
    context['s3_log'] = os.path.join(
        s3_path, output_base.replace('.json', '.log')
    )
    
     # local stuff
    context['user'] = os.environ.get('USER')
    context['sudo_password'] = os.environ.get('SUDO')
    context['output'] = os.path.join(
        context['volume_directory'], output_base
    )
    context['log'] = os.path.join(
        context['volume_directory'], output_base.replace('.json', '.log')
    )
    
    return context

if __name__ == '__main__':
    '''
    Parse the input flags,
    create a context dict of all variables we're going to use,
    create a connect a Digitial Ocean (DO) volume to store data,
    start a log,
    query twitter,
    compress the returned json object from twitter,
    upload the compressed json and the log to s3
    destroy all files on the volume, detach, destroy.
    '''
    #setup parser for command line arguments
    args = parse_args(sys.argv[1:])
    context = build_context(args)
    if create_and_attach_volume(context):
        logging.basicConfig(filename=context['log'], level=logging.INFO)
        twitter_query(context)
        context['output_bz2'] = bzip(context)
        send_to_s3(context)
        detach_and_destroy_volume(context)
        destroy(context)
