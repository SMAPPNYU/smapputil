import sys
import csv
import json
import logging
import paramiko
import argparse

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
        if ' -n ' in cron_entry and '-op collect' in cron_entry:
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

    return build_collection_list(crontab_entries)

def parse_args(args):
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', dest='input', required=True, help='Path to a file listing the servers you want to count.')
    parser.add_argument('-o', '--output', dest='output', required=True, help='Path to output file with servers and their collections.')
    parser.add_argument('-l', '--log', dest='log', default=expanduser('~/pylogs/list_collections.log'), help='This is the path to where your output log should be.')
    parser.add_argument('-k', '--key', dest='key', default=None, help='optionally specify your key, this may be necessary on some systems with non default names')
    return parser.parse_args(args)

if __name__ == '__main__':
    args = parse_args(sys.argv[1:])

    logging.basicConfig(filename=args.log, level=logging.INFO)
    logger = logging.getLogger(__name__)

    collections_by_server = {}

    if args.input.endswith('.json'):
        with open(expanduser(args.input), 'r') as data:
            line_dict = json.load(data)
            for server, user in line_dict.items():
                collections_by_server[server] = list_collections(server, user, args.key)

    elif args.input.endswith('.csv'):
        with open(expanduser(args.input), 'r') as data:
            reader = csv.reader(data)
            for row in reader:
                collections_by_server[row[0]] = list_collections(row[0], row[1], args.key)

    else:
        logger.info('could not load file %s aint csv or json: ', args.input)
     
    f = open(args.output, 'w')
    print('servers available (with less than 9 collections:')
    for k,v in collections_by_server.items():
        if len(v) < 9:
            print(k)
    print('also check out file {}'.format(args.output))
    f.write(json.dumps(collections_by_server, indent=4))
    f.close()
    
'''
author @yvan
http://docs.paramiko.org/en/1.16/
http://jessenoller.com/blog/2009/02/05/ssh-programming-with-paramiko-completely-different
'''