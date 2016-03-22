import sys
import json
import logging
import argparse
import datetime

from smapp_collector import make_filter

def parse_args(args):
    currentdate = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
    parser = argparse.ArgumentParser()
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
    