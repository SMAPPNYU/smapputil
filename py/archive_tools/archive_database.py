import os
import sys
import json
import time
import signal
import psutil
import logging
import argparse
import subprocess

def dump_database(hostname, port, dbname, username, password, output_path):
    mongodump_string = "mongodump --host {}:{} -u {} -p {} -o {} -d {}".format(hostname, port, username, password, output_path, dbname)
    logger.info('trying to start: {}'.format(mongodump_string))
    process = subprocess.Popen([mongodump_string], shell=True)
    logger.info('process should be: {}'.format(process.pid))
    proc = psutil.Process(process.pid)
    logger.info('proc.status is {}'.format(proc.status()))
    if proc.status() != psutil.STATUS_RUNNING and proc.status() != psutil.STATUS_SLEEPING:
        logger.info('things are not right, trying to kill {}'.format(process.pid))
        os.killpg(os.getpgid(int(process.pid)), signal.SIGTERM)
    while proc.status() == psutil.STATUS_RUNNING or proc.status() == psutil.STATUS_SLEEPING:
        logger.info('mongodumping with command: {}'.format(mongodump_string))
        time.sleep(1)

def parse_args(args):
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', dest='input', required=True, help='a list of dbs to transfer')
    parser.add_argument('-ho', '--hostname', dest='hostname', help='')
    parser.add_argument('-u', '--username', dest='username', help='the username for this database to read/write on')
    parser.add_argument('-w', '--password', dest='password', help='password for this user on this db')
    parser.add_argument('-p', '--port', dest='localport', default='49999', help='local port to map to the remoteport')
    parser.add_argument('-l', '--log', dest='log', default=os.path.expanduser('~/pylogs/archive_database.log'), help='This is the path to where your output log should be.')
    return parser.parse_args(args)

if __name__ == '__main__':
    args = parse_args(sys.argv[1:])

    logging.basicConfig(filename=args.log, level=logging.INFO)
    logger = logging.getLogger(__name__)

    with open(expanduser(args.input), 'r') as data:
            input_dict = json.load(data)
            for db in input_dict:
                    dump_database(args.hostname, args.port, db['name'], args.username, args.password, )