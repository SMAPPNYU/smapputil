'''
Takes multiple bson files in as inputs and merges them.
'''

# c* http://stackoverflow.com/questions/18160078/how-do-you-write-tests-for-the-argparse-portion-of-a-python-module
# c* http://stackoverflow.com/questions/4028904/how-to-get-the-home-directory-in-python

import sys
import logging
import argparse
import datetime
from os.path import expanduser
from bson import BSON, decode_file_iter

def merge_bson(args):
    #configure logging
    logger = logging.getLogger(__name__)
    logger.info('Creating your output file : %s', args.output)
    with open(args.output, 'wb') as outputbson:
        for bsonfile in args.inputs:
            logger.info('Opening input file : %s', bsonfile)
            with open(bsonfile, 'rb') as bsonfile_handle:
                iterator = decode_file_iter(bsonfile_handle)
                for line in iterator:
                    outputbson.write(BSON.encode(line))
    logger.info('Finished merging input file : %s', bsonfile)
    logger.info('Finished merging all input files to path : %s', args.output)

def parse_args(args):
    currentdate = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
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
    # actually merge the bson files
    merge_bson(args)