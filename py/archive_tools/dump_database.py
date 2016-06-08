import os
import sys
import json
import logging
import argparse
import subprocess

def dump_database(hostname, port, dbname, username, password, authdb, output_path):
    mongodump_string = "mongodump --host {}:{} -u {} -p '{}' -o {} -d {} --authenticationDatabase {}".format(hostname, port, username, password, output_path, dbname, authdb)
    logger.info('trying to start: {}'.format(mongodump_string))
    try:
        #check_output is like popen but blocks to w8 for output
        process_out = subprocess.check_output([mongodump_string], shell=True)
        logger.info('finished: {}'.format(mongodump_string))
        logger.info('output: {}'.format(process_out))
    except subprocess.CalledProcessError as e:
        logger.info('failed for reason: {} on data set: {}'.format(e, dbname))

def parse_args(args):
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', dest='input', required=True, help='a list of dbs to mongodump')
    parser.add_argument('-ho', '--hostname', dest='hostname', help='')
    parser.add_argument('-u', '--username', dest='username', help='the username for this database to read/write on')
    parser.add_argument('-w', '--password', dest='password', help='password for this user on this db')
    parser.add_argument('-p', '--port', dest='port', default='49999', help='local port to map to the remoteport')
    parser.add_argument('-a', '--auth', dest='authdb', default='admin', help='the auth db')
    parser.add_argument('-o', '--outputpath', dest='outputpath', help='the path to the folder where you\'d like the mongodump to go')
    parser.add_argument('-l', '--log', dest='log', default=os.path.expanduser('~/pylogs/dump_database.log'), help='This is the path to where your output log should be.')
    return parser.parse_args(args)

if __name__ == '__main__':
    args = parse_args(sys.argv[1:])

    logging.basicConfig(filename=args.log, level=logging.INFO)
    logger = logging.getLogger(__name__)

    with open(os.path.expanduser(args.input), 'r') as data:
            input_list = json.load(data)
            for db in input_list:
                    dump_database(args.hostname, args.port, db, args.username, args.password, args.authdb, args.outputpath)

'''
author @yvan
'''