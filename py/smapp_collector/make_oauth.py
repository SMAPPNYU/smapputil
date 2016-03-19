import sys
import json
import logging
import argparse
import datetime

def make_oauth(output, args_list):
    oauth_file = {
        "consumer_key": args_list[0],
        "consumer_secret": args_list[1],
        "access_token": args_list[2],
        "access_token_secret": args_list[3]
    }
    json.dump(oauth_file, output)

def parse_args(args):
    currentdate = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--inputs', dest='inputs', required=True, nargs='+', help='These inputs are paths to your bson files. Required.')
    parser.add_argument('-o', '--output', dest='output', required=True, help='This will be your outputted single bson file. Required')
    parser.add_argument('-l', '--log', dest='log', default=expanduser('~/pylogs/merge_bson_'+currentdate+'.log'), help='This is the path to where your output log should be. Required')
    return parser.parse_args(args)

if __name__ == '__main__':
    #setup parser for command line arguments
    args = parse_args(sys.argv[1:])
    #configure logs
    logging.basicConfig(filename=args.log, level=logging.INFO)
    make_oauth(args.output, args.inputs)
    