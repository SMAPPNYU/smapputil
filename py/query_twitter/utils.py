import os
import csv
import json
import time
import socket
import datetime
import logging
import random
from subprocess import Popen, PIPE

import pandas as pd
import digitalocean
import s3

verbose = 1

def log(msg):
    '''
    Records messages and prints if verbose.
    '''
    logger = logging.getLogger(__name__)
    if verbose: print(msg)
    logger.info(msg)

def get_ip_address():
    '''
    Gets the IP address of this machine.
    '''
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0]

def get_id_list(file_input, offset=0):
    '''
    opens list of user ids to query.
    from the -i arg
    '''
    filename, file_extension = os.path.splitext(file_input)
    id_list = []
    if file_extension == '.json':
        log('loading json...')
        id_data = open(file_input).read()
        id_list = json.loads(id_data)
    elif file_extension == '.csv':
        log('loading csv...')
        count = 0
        with open(file_input) as f:
            for rowdict in list(csv.DictReader(f)):
                # if list is not empty
                if rowdict:
                    id_list.append(rowdict['id'])
        log('launching query for {} inputs'.format(len(id_list)))
    return id_list[offset:]

def prep_s3(context):
    '''
    Uploads the api tokens, claiming them from further use.
    '''
    log(">>> Start {}".format(datetime.datetime.now()))
    s3.disk_2_s3(context['log'], context['s3_log'])
    s3.disk_2_s3(context['auth'], context['s3_auth'])


def settle_affairs_in_s3(context):
    '''
    Removes the api tokens, freeing them for further use.
    Moves the log file into archive.
    '''
    s3.rm(context['s3_auth'])
    s3.mv(context['s3_log'], context['s3_log_done'])


def destroy_droplet(context):
    '''
    This is where it ends :)
    '''
    droplet = context['droplet']
    droplet.destroy()

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

def detach_and_destroy_volume(context):
    '''
    Remove all files from the volume, detaches the volume, then destroys it.
    '''
    V = context['volume']

    command = 'sudo -S rm -rf {}'.format(context['volume_directory']).split()
    try:
        p = Popen(command, stdin=PIPE, stderr=PIPE, universal_newlines=True)
        time.sleep(.2)
        sudo_prompt = p.communicate(context['sudo_password'] + '\n')[1]
    except Exception as e:
        log('Issue clearing the Volume! {}'.format(e))

        pass
    
    log("Detaching volumne...")
    V.detach(droplet_id = context['droplet_id'], 
             region = context['droplet_region'])
    time.sleep(12)
    
    log("Destroying volumne...")
    V.destroy()
    
    log("Volume {} Destroyed!".format(context['volume_directory']))


def bzip(context):
    '''
    Bzips a file.
    When this is successful, the original file will have disappeared.
    When that happens this returns the new file name with the .bz2 extension.
    '''
    f_out = context['output']
    command = ['/bin/pbzip2', f_out]
    process = Popen(command, stdin=PIPE, stderr=PIPE)
    
    while os.path.isfile(f_out):
        time.sleep(1)
        
    return f_out + '.bz2'


def pbzip2(context):
    f_out = context['output']
    log("bzipping {}".format(f_out))
    command = ['/usr/bin/pbzip2', '-v', '-f', f_out]
    process = Popen(command, shell=False, stdout=PIPE, stdin=PIPE)
    for line in iter(process.stdout.readline, b''): 
        log(line)
    returncode = process.wait() 
    log("return code for {}".format(returncode))
    return f_out + '.bz2'


def chunker(seq, n):
    '''
    Chunks an iterator (seq) into length (n).
    '''
    return (seq[pos:pos + n] for pos in range(0, len(seq), n))


def load_tokens_s3(s3_path):
    tokens = s3.read_json(s3_path, lines=True)
    return tokens


def download_from_s3(s3_input, new_dir='pylogs/'):
    input_filebase = os.path.basename(s3_input)
    new_file = os.path.join(new_dir, input_filebase)
    
    if s3.file_exists(s3_input):
        s3.wget(s3_input, new_file)
    else:
        raise "{} is not in s3!".format(s3_input)
    
    return new_file


def get_free_tokens(s3_used_token_pattern, s3_all_token_pattern):
    '''Calculates the delta between the used tokens and all tokens on s3.
    Returns a Pandas Dataframe of the key metadata.'''
    used_token_files = s3.ls(s3_used_token_pattern)
    all_tokens = s3.ls(s3_all_token_pattern)
    
    df_all = load_tokens_s3(all_tokens[0])
    
    df_used = pd.DataFrame()
    for s3_path in used_token_files:
        toks = load_tokens_s3(s3_path)
        toks['s3_path'] = s3_path
        df_used = df_used.append(toks)
        
    df_free = df_all[~df_all['consumer_key'].isin(df_used['consumer_key'])]
    
    return df_free


def create_token_files(context, 
                       s3_used_token_pattern='s3://smapp-nyu/tokens/used/*.json', 
                       s3_all_token_pattern='s3://smapp-nyu/tokens/all_tokens/*.json'):
    
    n_tokens_per_file = context['n_tokens']
    
    enough = False
    while not enough:
        df_free = get_free_tokens(s3_used_token_pattern, 
                                  s3_all_token_pattern)
        if len(df_free) >= n_tokens_per_file:
            enough = True
            break
        sleep_mins = random.random() * 15
        log('Not enough tokens, sleeping for {} mins...'.format(sleep_mins))
        time.sleep(60 * sleep_mins)
    
    log('Enough Tokens!')                   
    df_token_temp = df_free.sample(n_tokens_per_file)
    df_token_temp.to_json(context['auth'], orient='records', lines=True)
    
# def get_user_id_file(user_id, context):
#     '''
#     File locations for user_id csv files.
#     '''
#     filename = os.path.join(context['volume_directory'], user_id + '.json')
#     s3_filename = os.path.join(context['s3_path'], user_id + '.json')
#     s3_id_key = os.path.join(context['s3_path'], user_id)

#     return filename, s3_filename, s3_id_key

# def get_user_id_file(user_id, context):
#     '''
#     File locations for user_id csv files.
#     '''
#     filename = os.path.join(context['volume_directory'], user_id + '.csv')
#     s3_filename = os.path.join(context['s3_path'], user_id, 
#         context['currentyear'], context['currentmonth'],
#         user_id  + '.csv')
#     s3_id_key = os.path.join(context['s3_path'], user_id)

#     return filename, s3_filename, s3_id_key