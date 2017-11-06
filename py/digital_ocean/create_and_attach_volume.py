import argparse
import datetime
import json
import sys
import os
import time
import socket
from subprocess import Popen, PIPE

import digitalocean


verbose = 1


def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0]

def create_and_attach_volume(context):
    '''
    TODO: remove the mount if it exists!
    '''
    commands = [
        'sudo -S rm -rf /mnt/{VOL_NAME}',
        "sudo -S mkfs.ext4 -F /dev/disk/by-id/scsi-0DO_Volume_{VOL_NAME}",
        'sudo -S mkdir -p /mnt/{VOL_NAME}',
        'sudo -S mount -o discard,defaults /dev/disk/by-id/scsi-0DO_Volume_{VOL_NAME} /mnt/{VOL_NAME}',
        """sudo -S sh -c 'echo "/dev/disk/by-id/scsi-0DO_Volume_{VOL_NAME} /mnt/{VOL_NAME} ext4 defaults,nofail,discard 0 0">>/etc/fstab' """,        
        'sudo -S chown {USER}:{USER} /mnt/{VOL_NAME}'
    ]
    
    V = context['volume']
    
    try:
        if verbose:
            print("creating volume " + context['volume_name'])
        V.create()
    except Exception as e:
        if verbose:
            print("Issue attaching creating volume. {}".format(e))
        pass
    
    time.sleep(5)
    
    try:
        if verbose:
            print("connecting volume " + context['volume_name'])
        V.attach(droplet_id = context['droplet_id'], 
                 region = context['droplet_region'])
    except Exception as e:
        if verbose:
            print("Issue attaching volume. {}".format(e))
        pass
    
    time.sleep(5)
    
    for command in commands:
        command = command.format(VOL_NAME=context['volume_name'], 
                                 USER=context['user'])
        print(command)
        p = Popen(command, stdin=PIPE, stderr=PIPE, shell=True, universal_newlines=True)
        sudo_prompt = p.communicate(context['sudo_password'] + '\n')[1]
        time.sleep(20)       
    
    if verbose:
        print("Volume {} configred!".format(context['volume_name']))
   
    return True


def build_context(args):
    context = args

    if 'token' not in context:
        context['token'] = os.environ.get('DO_TOKEN')
    
    manager = digitalocean.Manager(token=context['token'])
    my_droplets = manager.get_all_droplets()
    mydrop = [_ for _ in my_droplets if _.ip_address == get_ip_address()][0]
    
    context['droplet_id'] = mydrop.id
    context['droplet'] = mydrop
    context['volume_name'] = mydrop.name + '-volume'
    context['volume_directory'] = '/mnt/' + context['volume_name']
    
    context['volume'] = digitalocean.Volume(
        token= context['token'],
        name= context['volume_name'],
        region= context['droplet_region'],
        size_gigabytes= context['volume_size_gbs']
    )

    context['user'] = os.environ.get('USER')
    if 'sudo_password' not in context:
        context['sudo_password'] = os.environ.get('SUDO')

    return context


def parse_args(args):
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--volume-size-gbs', dest='volume_size_gbs', required=True, type=int, help='The size in gbs of the volume you want')
    parser.add_argument('-r', '--volume-reigon', dest='droplet_region', required=True, help='slug for reigon')
    parser.add_argument('-d', '--digital-ocean-token', dest='token', required=False, help='DO access token')

    return vars(parser.parse_args())


if __name__ == '__main__':
    '''
    Parse the input flags,
    create a context dict of all variables we're going to use,
    create and connect a Digitial Ocean (DO) volume to store data
    '''
    #setup parser for command line arguments
    args = parse_args(sys.argv[1:])
    context = build_context(args)
    create_and_attach_volume(context)


'''
This script attaches a volume to the current IP.
Note this only works when you run it from a digital ocean machine.
This also needs to returns stdout if running remotely!

Leon Yin 2017-11-06
'''

