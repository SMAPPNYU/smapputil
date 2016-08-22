import os
import sys
import json
import logging
import argparse
import datetime
import pymongo

currentdate = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

def parse_args(args):
	parser = argparse.ArgumentParser()
	parser.add_argument('-n', '--dataset-name', dest='dataset_name', required=True, help='the mongodb dataset to check.')
	parser.add_argument('-ho', '--db-host', dest='db_host', default='localhost', help='the host where mongodb is running')
	parser.add_argument('-p', '--db-port', dest='db_port', default='49999', help='the port on the host where mongodb is running')
	parser.add_argument('-l', '--log', dest='log', default=os.path.expanduser('~/pylogs/dataset_exists.log'), help='This is the path to where your output log should be.')
	return parser.parse_args(args)

if __name__ == '__main__':
	args = parse_args(sys.argv[1:])

	logging.basicConfig(filename=args.log, level=logging.INFO, filemode='w')
	logger = logging.getLogger(__name__)
	logging.info('@timestamp: {}'.format(currentdate))

	# Check if the dataset exists
	mongo = pymongo.MongoClient(args.db_host, int(args.db_port))
	database_names = mongo.database_names()
	if args.dataset_name not in database_names:
		print("Dataset {} does not exist.".format(args.dataset_name))
		logging.info("Dataset {} does not exist.".format(args.dataset_name))
		sys.exit(100)
	else:
		print("Dataset {} exists.".format(args.dataset_name))

'''
author @Roman
'''
