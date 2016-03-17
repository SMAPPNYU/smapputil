import sys
import csv
import json
import logging
import argparse
import datetime

from os.path import expanduser

def csv_to_json(args):
    json_output = open(args.output, 'a')

    for csv_input in args.inputs:
        csvfile = open(csv_input, 'r')
        fieldnames = ("consumer_key","consumer_secret","access_token","access_token_secret")
        reader = csv.DictReader(csvfile, fieldnames)
        for row in reader:
            json.dump(row, json_output)
            json_output.write('\n')
        csvfile.close()

    json_output.close()

def csv_to_json_list(args):
    json_list = []
    json_output = open(args.output, 'a')

    for csv_input in args.inputs:
        csvfile = open(csv_input, 'r')
        fieldnames = ("consumer_key","consumer_secret","access_token","access_token_secret")
        reader = csv.DictReader(csvfile, fieldnames)
        for row in reader:
            json_list.append(row)
        csvfile.close()

    json.dump(json_list, json_output, indent=2)
    json_output.close()

def parse_args(args):
    currentdate = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--inputs', dest='inputs', required=True, nargs='+', help='These inputs are paths to your bson files. Required.')
    parser.add_argument('-o', '--output', dest='output', required=True, help='This will be your outputted single bson file. Required')
    parser.add_argument('-l', '--log', dest='log', default=expanduser('~/pylogs/merge_bson_'+currentdate+'.log'), help='This is the path to where your output log should be. Required')
    parser.add_argument('-jl', '--jsonlist', dest="jsonlist", action='store_true', default=False, help="call this flag to let the script know you want a json list and not a json object on each page")    
    return parser.parse_args(args)

if __name__ == '__main__':
    #setup parser for command line arguments
    args = parse_args(sys.argv[1:])
    #configure logs
    logging.basicConfig(filename=args.log, level=logging.INFO)
    # actually merge the bson files
    if args.jsonlist:
        csv_to_json_list(args)
    else:
        csv_to_json(args)
