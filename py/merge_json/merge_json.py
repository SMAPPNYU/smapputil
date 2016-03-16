'''
Takes multiple json files in as inputs and merges them.
'''

import sys
import json
import logging
import argparse
import datetime

from os.path import expanduser

def merge_json(args):
    #configure logging
    logger = logging.getLogger(__name__)
    logger.info('Creating your output file : %s', args.output)
    with open(args.output, 'wb') as outputjson:
        for jsonfile in args.inputs:
            logger.info('Opening input file : %s', jsonfile)
            with open(jsonfile, 'rb') as jsonfile_handle:
                iterator = decode_file_iter(jsonfile_handle)
                for line in iterator:
                    outputjson.write(line)
    logger.info('Finished merging input file : %s', jsonfile)
    logger.info('Finished merging all input files to path : %s', args.output)

def parse_args(args):
    currentdate = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--inputs', dest='inputs', required=True, nargs='+', help='These inputs are paths to your bson files. Required.')
    parser.add_argument('-o', '--output', dest='output', required=True, help='This will be your outputted single bson file. Required')
    parser.add_argument('-l', '--log', dest='log', default=expanduser('~/pylogs/merge_json_'+currentdate+'.log'), help='This is the path to where your output log should be. Required')
    return parser.parse_args(args)

if __name__ == '__main__':
    #setup parser for command line arguments
    args = parse_args(sys.argv[1:])
    #configure logs
    logging.basicConfig(filename=args.log, level=logging.INFO)
    # actually merge the json` files
    merge_json(args)