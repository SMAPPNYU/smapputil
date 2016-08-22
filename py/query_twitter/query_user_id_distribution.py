import os
import sys
import json
import argparse
import datetime
import logging

def query_distribution(output_file, input_file):
    count_struct = {}
    logger = logging.getLogger(__name__)

    with open(input_file) as f:
        for line in f:
            try:
                json_line = json.loads(line)
            except ValueError as err:
                logger.info('failed to read a json line : %s', err)

            if 'smapp_original_user_id' in json_line and json_line['smapp_original_user_id'] not in count_struct:
                count_struct[json_line['smapp_original_user_id']] = 1
            elif 'smapp_original_user_id' in json_line:
                count_struct[json_line['smapp_original_user_id']] += 1

    with open(output_file, 'w') as filehandle:
        val = 0
        items = 0
        filehandle.write('{},{}'.format('id', 'smapp_tweet_count'))
        filehandle.write('\n')
        for key, value in count_struct.items():
            val = val + value
            items = items + 1
            filehandle.write('{},{}'.format(key, value))
            filehandle.write('\n')
        filehandle.write('average_per_user,{}'.format(val / items))
        filehandle.write('\n')
        filehandle.write('all_users_total,{}'.format(val))

def parse_args(args):
    currentdate = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', dest='input', required=True, help='This is a path to your input.json, a [] list of twitter ids.')
    parser.add_argument('-o', '--output', dest='output', required=True, help='This will be your output file, a {} json object showing original ids and twitter screen names.')
    parser.add_argument('-l', '--log', dest='log', default=os.path.expanduser('~/pylogs/query_tweet_distribution'+currentdate+'.log'), help='This is the path to where your output log should be. Required')
    return parser.parse_args(args)

if __name__ == '__main__':
    #setup parser for command line arguments
    args = parse_args(sys.argv[1:])
    #configure logs
    logging.basicConfig(filename=args.log, level=logging.INFO)
    # actually merge the bson files
    query_distribution(os.path.expanduser(args.output), os.path.expanduser(args.input))