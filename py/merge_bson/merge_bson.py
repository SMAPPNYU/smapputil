'''
Takes multiple bson files in as inputs and merges them.
'''

import sys
import logging
import argparse
import datetime

from os.path import expanduser
from bson import BSON, decode_file_iter

def merge_bson(output, inputs):
    #configure logging
    logger = logging.getLogger(__name__)
    logger.info('Creating your output file : %s', output)
    with open(output, 'wb') as outputbson:
        for bsonfile in inputs:
            logger.info('Opening input file : %s', bsonfile)
            with open(bsonfile, 'rb') as bsonfile_handle:
                iterator = decode_file_iter(bsonfile_handle)
                for line in iterator:
                    outputbson.write(BSON.encode(line))
    logger.info('Finished merging input file : %s', bsonfile)
    logger.info('Finished merging all input files to path : %s', output)

def merge_bson_unique(output, inputs, uniquefield):
    uniquefieldset = set()
    duplicatecount = 0
    invalidcount = 0
    totalcount = 0

    #configure logging
    logger = logging.getLogger(__name__)
    logger.info('Creating your output file : %s', output)
    with open(output, 'wb') as outputbson:
        for bsonfile in inputs:
            totalcount += 1
            logger.info('Opening input file : %s', bsonfile)
            with open(bsonfile, 'rb') as bsonfile_handle:
                iterator = decode_file_iter(bsonfile_handle)
                for singleobject in iterator:
                    if uniquefield not in singleobject:
                        invalidcount += 1
                    if singleobject[uniquefield] not in uniquefieldset:
                        outputbson.write(BSON.encode(singleobject))
                        uniquefieldset.add(singleobject[uniquefield])
                    else:
                        duplicatecount += 1
            logging.info('Finished merging input file : %s', bsonfile)
    logger.info('Finished merging all input files to path : %s', output)
    logger.info('Duplicates: %s, Total: %s, Invalid: %s', duplicatecount, totalcount, invalidcount)

def parse_args(args):
    currentdate = datetime.datetime.now().strftime("%Y-%m-%d_%H:%M")
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--inputs', dest='inputs', required=True, nargs='+', help='These inputs are paths to your bson files. Required.')
    parser.add_argument('-o', '--output', dest='output', required=True, help='This will be your outputted single bson file. Required')
    parser.add_argument('-f', '--uniquefield', dest='uniquefield', required=False, help='This takes one field that you can enforce uniqueness on like an \'id\' field.')
    parser.add_argument('-l', '--log', dest='log', default=expanduser('~/pylogs/merge_bson_'+currentdate+'.log'), help='This is the path to where your output log should be. Required')
    return parser.parse_args(args)

if __name__ == '__main__':
    #setup parser for command line arguments
    args = parse_args(sys.argv[1:])
    #configure logs
    logging.basicConfig(filename=args.log, level=logging.INFO)
    # actually merge the bson files
    if args.uniquefield:
        merge_bson_unique(args.output, args.inputs, args.uniquefield)
    else:
        merge_bson(args.output, args.inputs)

'''
author @yvan
c* http://stackoverflow.com/questions/18160078/how-do-you-write-tests-for-the-argparse-portion-of-a-python-module
c* http://stackoverflow.com/questions/4028904/how-to-get-the-home-directory-in-python
'''
