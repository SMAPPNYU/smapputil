'''
Takes multiple json files in as inputs and merges them 
together. This script enforces a uniqueness on the field
given as an input by the user.
'''

import sys
import json
import logging
import argparse
import datetime

from os.path import expanduser

def merge_json(args):
    uniquefieldset = set()
    duplicatecount = 0
    invalidcount = 0
    totalcount = 0

    #configure logging
    logger = logging.getLogger(__name__)
    logger.info('Creating your output file : %s', args.output)
    with open(args.output, 'w') as outputjson:
        for jsonfile in args.inputs:
            totalcount += 1
            logger.info('Opening input file : %s', jsonfile)
            with open(jsonfile, 'r') as jsonfile_handle:
                for line in jsonfile_handle:
                    singleobject = json.loads(line)
                    if args.uniquefield not in singleobject:
                        invalidcount += 1
                    if json.dumps(singleobject[args.uniquefield]) not in uniquefieldset:
                        outputjson.write(json.dumps(singleobject))
                        outputjson.write('\n')
                        uniquefieldset.add(json.dumps(singleobject[args.uniquefield]))
                    else:
                        duplicatecount += 1
            logging.info('Finished merging input file : %s', jsonfile)
    logger.info('Finished merging all input files to path : %s', args.output)
    logger.info('Duplicates: %s, Total: %s, Invalid: %s', duplicatecount, totalcount, invalidcount)

def parse_args(args):
    currentdate = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--inputs', dest='inputs', required=True, nargs='+', help='These inputs are paths to your json files. Required.')
    parser.add_argument('-o', '--output', dest='output', required=True, help='This will be your outputted single json file. Required')
    parser.add_argument('-f', '--uniquefield', dest='uniquefield', required=True, help='This takes one field that you can enforce uniqueness on like an \'id\' field.')
    parser.add_argument('-l', '--log', dest='log', default=expanduser('~/pylogs/merge_json_'+currentdate+'.log'), help='This is the path to where your output log should be. Required')
    return parser.parse_args(args)

if __name__ == '__main__':
    #setup parser for command line arguments
    args = parse_args(sys.argv[1:])
    #merge the actual json files
    merge_json(args)
    #configure logging
    logging.basicConfig(filename=args.log, level=logging.INFO)
