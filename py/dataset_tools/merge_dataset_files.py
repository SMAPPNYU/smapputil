import bz2 
import sys
import json
import logging
import argparse
import datetime

from os.path import expanduser

def merge_dataset(output, inputs):
    #configure logging
    logger = logging.getLogger(__name__)
    logger.info('Creating your output file : %s', output)

    with open(output, 'wb') as outputjson:
        for jsonfile in inputs:
            logger.info('Opening input file : %s', jsonfile)
            with bz2.BZ2File(jsonfile, 'rb') as jsonfile_handle:
                for count,line in enumerate(jsonfile_handle):
                    outputjson.write(line.rstrip())
                    outputjson.write(b'\n')
        logger.info('Finished merging input file : %s', jsonfile)
    logger.info('Finished merging all input files to path : %s', output)

def parse_args(args):
    currentdate = datetime.datetime.now().strftime("%Y-%m-%d_%H:%M")
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--inputs', dest='inputs', required=True, nargs='+', help='These inputs are paths to your json files. Required.')
    parser.add_argument('-o', '--output', dest='output', required=True, help='This will be your outputted single json file. Required')
    parser.add_argument('-l', '--log', dest='log', default=expanduser('~/pylogs/merge_json_'+currentdate+'.log'), help='This is the path to where your output log should be. Required')
    return parser.parse_args(args)

if __name__ == '__main__':
    #setup parser for command line arguments
    args = parse_args(sys.argv[1:])
    #configure logs
    logging.basicConfig(filename=args.log, level=logging.INFO)
    # actually merge the json` files
    merge_dataset(args.output, args.inputs, args.jsonlist, args.jsonload)

'''
takes multiple .json.bz2 files in as inputs and merges them.
author @yvan
'''