import os, sys, csv

import logging
import paramiko
import argparse
import subprocess

from os.path import expanduser

def paramiko_list_crontab(collector_machine, username, key):
    logger = logging.getLogger(__name__)
    # login to paramiko and list the crontab
    ssh = paramiko.SSHClient()
    ssh.load_system_host_keys()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(collector_machine, username=username, key_filename=key)
    ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command('crontab -l')
    # log any paramiko incident
    if ssh_stderr.read():
        logger.info('error from paramiko exec_command: %s', ssh_stderr.read())
    return ssh_stdout

def build_collection_list(crontab_entries):
    # create a parser for this argument
    cron_parser = argparse.ArgumentParser()
    cron_parser.add_argument('-n')
    cron_parser.add_argument('-nfsb')
    cron_parser.add_argument('-nfsm')

    collection_list = []

    # loop through each crontab entry 
    # and get the name of each collection
    for cron_entry in crontab_entries:
        if ' -n ' in cron_entry:
            split_cron_entry = cron_entry.split(' ')
            known_args, unknown_args = cron_parser.parse_known_args(split_cron_entry)
            collection_list.append(known_args.n[1:-1])
    return collection_list

def list_collections(collector_machine, username, key):
    # get the crontab
    paramiko_cron_output= paramiko_list_crontab(collector_machine, username, key)
    # read the crontab from stdout
    crontab = paramiko_cron_output.read()
    # parse the crontab for the names of the collections
    crontab_entries = crontab.decode().split('\n')

    # create a parser for this argument
    cron_parser = argparse.ArgumentParser()
    cron_parser.add_argument('-n')
    cron_parser.add_argument('-nfsb')
    cron_parser.add_argument('-nfsm')

    collection_list = []

    # loop through each crontab entry 
    # and get the name of each collection
    for cron_entry in crontab_entries:
        if ' -n ' in cron_entry and '-op collect' in cron_entry:
            split_cron_entry = cron_entry.split(' ')
            known_args, unknown_args = cron_parser.parse_known_args(split_cron_entry)
            collection_list.append(known_args.n[1:-1])
    return collection_list


def parse_args(args):
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', dest='input', required=True, help='Path to a file listing the servers you want to count.')
    parser.add_argument('-l', '--log', dest='log', required=True, help='This is the path to where your output log should be.')
    parser.add_argument('-k', '--key', dest='key', help='Specify your key, this is necessary on hpc where this was made to run as the key has a weird name.')
    return parser.parse_args(args)

if __name__ == '__main__':
    args = parse_args(sys.argv[1:])

    logging.basicConfig(filename=args.log, level=logging.INFO)
    logger = logging.getLogger(__name__)


    with open(expanduser(args.input), 'r') as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            k = row[1]
            v = list_collections(row[1], row[0], args.key)
            incl = ','.join(v)+',"*.json",metadata,filters'
            # needs to look like:
            # /share/apps/utils/rsync.sh -a /scratch/olympus/ yvan@192.241.158.221:/mnt/olympus-stage/ --include={"*.json",whale_test,metadata,filters} --exclude='*' --update
            run_cmd = '/share/apps/utils/rsync.sh -a {source} {uname}@{dest}:{dest_path} --include={{{params}}} --exclude="*" --update'.format(uname=row[0], source=row[3], dest=k, dest_path=row[2], params=incl) 
            logger.info('running: '+run_cmd)
            process = subprocess.Popen([run_cmd], stdin=None, stdout=None, stderr=None, shell=True)
            out, err = process.communicate()
            logger.info('rsync subprocess output:\n {}'.format(out))
            logger.info('rsync subprocess error:\n'.format(err))
