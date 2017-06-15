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
                collections_by_server[server] = paramiko_list_crontab(server, user, args.key).read()

    elif args.input.endswith('.csv'):
        with open(expanduser(args.input), 'r') as data:
            reader = csv.reader(data)
            for row in reader:
                collections_by_server[row[0]] = paramiko_list_crontab(row[0], row[1], args.key).read()

    else:
        logger.info('could not load file %s aint csv or json: ', args.input)
     
    f = open(args.output, 'w')
    for k,v in collections_by_server.items():
        f.write('-'*100 + '\n')
        f.write(k+':')
        f.write('\n')
        f.write('-'*100 + '\n')
        f.write(' ')
        f.write('\n')
        f.write('\n')
        f.write(v.decode('utf-8'))
        f.write(' ')
        f.write('\n')
        f.write('\n')
    f.close()
    
'''
author @yvan
basically the same as the list collections code except that it stores the crons instead of extracting names from them
this is our backup mechanism, all the importand info for a collector lives essentially in its cron so if we have it we can repair
redeploy
'''