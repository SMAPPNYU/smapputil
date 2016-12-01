import bz2 
import sys
import csv
import json
import sqlite3
import logging
import argparse
import datetime

from os.path import expanduser
from smappdragon.tools.tweet_parser import TweetParser
from smappdragon import JsonCollection

def make_sqlite_db_csv(output, input_file):
    logger = logging.getLogger(__name__)
    logger.info('Creating your output file : %s', output)

    with open(input_file,'r') as f:
        csv_reader = csv.DictReader(f)
        csv_field_names = list(csv_reader.fieldnames)
        csv_fieldnames_str = ','.join(csv_field_names).replace('.','__')
        question_marks = ','.join(['?' for column in csv_field_names])

        con = sqlite3.connect(output)
        cur = con.cursor()
        cur.execute("CREATE TABLE data ({});".format(csv_fieldnames_str))
        insert_list = []
        for line in csv_reader:
            row = [line[field] for field in csv_field_names]
            insert_list.append(tuple(row))
            if (count % 10000) == 0:
                cur.executemany("INSERT INTO data ({}) VALUES ({});".format(csv_fieldnames_str, question_marks), insert_list)
                con.commit()
                insert_list = []
        if count < 10000:
            cur.executemany("INSERT INTO data ({}) VALUES ({});".format(csv_fieldnames_str, question_marks), insert_list)
            con.commit()
        con.close()

    logger.info('Finished processing input: {}, output is: {}'.format(input_file, output))

def make_sqlite_db_json(output, input_file, fields):
    logger = logging.getLogger(__name__)
    logger.info('Creating your output file : %s', output)

    column_str = ','.join([column for column in fields]).replace('.','__')
    question_marks = ','.join(['?' for column in fields])
    con = sqlite3.connect(output)
    cur = con.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS data ({});".format(column_str))

    json_col = JsonCollection(input_file)
    insert_list = []
    tp = TweetParser()

    for count,tweet in enumerate(json_col.get_iterator()):
        ret = tp.parse_columns_from_tweet(tweet, fields)
        row = [replace_none(col_val[1]) for col_val in ret]
        insert_list.append(tuple(row))

        if (count % 10000) == 0:
            cur.executemany("INSERT INTO data ({}) VALUES ({});".format(column_str, question_marks), insert_list)
            con.commit()
            insert_list = []

    if count < 10000:
        cur.executemany("INSERT INTO data ({}) VALUES ({});".format(column_str, question_marks), insert_list)
        con.commit()

    con.close()
    logger.info('Finished processing input: {}, output is: {}'.format(input_file, output))

def replace_none(s):
    if s is None:
        return 'NULL'
    return s

def parse_args(args):
    currentdate = datetime.datetime.now().strftime("%Y-%m-%d_%H:%M")
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--type', dest='type', required=True, help='Is your input a \'csv\' or a \'json\'?, Pick one.')
    parser.add_argument('-i', '--input', dest='input', required=True, help='These inputs are paths to your json file. Required')
    parser.add_argument('-f', '--fields', dest='fields', nargs='+', help='The field names you would like to turn into columns')
    parser.add_argument('-o', '--output', dest='output', required=True, help='This will be your outputted single json file. Required')
    parser.add_argument('-l', '--log', dest='log', default=expanduser('~/pylogs/make_sqlite_db'+currentdate+'.log'), help='This is the path to where your output log should be. Required')
    return parser.parse_args(args)

if __name__ == '__main__':
    args = parse_args(sys.argv[1:])
    logging.basicConfig(filename=args.log, level=logging.INFO)
    if args.type == 'csv':
        make_sqlite_db_csv(args.output, args.input)
    elif args.type == 'json':
        make_sqlite_db_json(args.output, args.input, args.fields)
    else:
        print('pick an appropriate input, csv or json')

'''
takes a .json file and coaxes out the specified fieldnames as co
author @yvan
'''


