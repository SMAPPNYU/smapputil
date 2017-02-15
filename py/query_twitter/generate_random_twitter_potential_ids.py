import argparse
import datetime
import logging
import random
import json
import sys
import os

USERID_FIRST = 1000 
USERID_LAST = 3015356002    

def generate_twitter_ids(output, number):
    write_fd = open(output, 'w+')
    random_user_ids = [str(random.randrange(USERID_FIRST, USERID_LAST)) for i in range(number)]
    json.dump(random_user_ids, write_fd, indent=2)
    write_fd.close()

def parse_args(args):
    currentdate = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', '--number', dest='number', type=int, required=True, help='the # of user ids you want to generate')
    parser.add_argument('-o', '--output', dest='output', required=True, help='This will be your output file, a {} json object showing original ids and twitter screen names.')
    parser.add_argument('-l', '--log', dest='log', default=os.path.expanduser('~/pylogs/generate_twitter_ids'+currentdate+'.log'), help='This is the path to where your output log should be. Required')
    return parser.parse_args()

if __name__ == '__main__':
    #setup parser for command line arguments
    args = parse_args(sys.argv[1:])
    #configure logs
    logging.basicConfig(filename=args.log, level=logging.INFO)
    # actually merge the bson files
    generate_twitter_ids(args.output, args.number)
