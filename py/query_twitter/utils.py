import csv
import json
import time
import socket
import datetime
import logging
from subprocess import Popen, PIPE

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

def get_id_list(file_input):
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
        log('launching query for %s inputs', len(id_list))
    return id_list

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

    command = 'sudo -S rm -rf /mnt/{}'.format(context['volume_name']).split()
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
    
    log("Volume {} Destroyed!".format(context['volume_name']))


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