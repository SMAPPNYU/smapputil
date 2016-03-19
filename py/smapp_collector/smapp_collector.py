import sys
import json
import logging
import argparse
import datetime

from subprocess import Popen
from crontab import CronTab

def start_collector():
    command = sys.executable 
    Popen([command], stdin=None, stdout=None, stderr=None, shell=True)

def remove_collector():
    pass

def freeze_collector():
    pass

def split_collector():
    pass

def make_oauth(output, args_list):
    oauth_file = {
        "consumer_key": args_list[0],
        "consumer_secret": args_list[1],
        "access_token": args_list[2],
        "access_token_secret": args_list[3]
    }
    json.dump(oauth_file, output)

def make_filter(output, track, follow, locations):
    filter_doc = {
        "track":[],
        "follow":[],
        "geo":[]
    }

    if track:
        filter_doc['track'] = track
    if follow: 
        filter_doc['follow'] = follow
    if locations:
        filter_doc['geo'] = locations

    json.dump(filter_doc, output)

def parse_args(args):
    currentdate = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
    parser = argparse.ArgumentParser()
    parser.add_argument('-op', '--operation', dest='operation', required=True, help='name of method to perform')
    parser.add_argument('-t', '--track', dest='track', default="", nargs='+', help='track parameter')
    parser.add_argument('-f', '--follow', dest='follow',default="", nargs='+', help='follow parameter')
    parser.add_argument('-loc', '--locations', dest='locations', default="", nargs='+', help='location parameter')
    parser.add_argument('-o', '--output', dest='output', required=True, help='output filter criteria file')
    parser.add_argument('-l', '--log', dest='log', default=expanduser('~/pylogs/merge_bson_'+currentdate+'.log'), help='log file')
    return parser.parse_args(args)

if __name__ == '__main__':
    #setup parser for command line arguments
    args = parse_args(sys.argv[1:])
    #configure logs
    logging.basicConfig(filename=args.log, level=logging.INFO)
    make_filter(args.output, args.track, args.follow, args.locations)
