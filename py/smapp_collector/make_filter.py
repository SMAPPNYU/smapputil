import sys
import json
import logging
import argparse
import datetime

def make_filter(output, args_list):
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
    parser.add_argument('-t', '--track', dest='track', nargs='+', help='track parameter')
    parser.add_argument('-f', '--follow', dest='follow', nargs='+', help='follow parameter')
    parser.add_argument('-loc', '--locations', dest='locations', nargs='+', help='location parameter')
    parser.add_argument('-o', '--output', dest='output', required=True, help='output filter criteria file')
    parser.add_argument('-l', '--log', dest='log', default=expanduser('~/pylogs/merge_bson_'+currentdate+'.log'), help='log file')
    return parser.parse_args(args)

if __name__ == '__main__':
    #setup parser for command line arguments
    args = parse_args(sys.argv[1:])
    #configure logs
    logging.basicConfig(filename=args.log, level=logging.INFO)
    make_filter(args.output, args.inputs)
    