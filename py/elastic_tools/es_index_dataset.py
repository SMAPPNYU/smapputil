import os
import sys
import json
import logging
import argparse
import datetime
import pymongo
from pysmap import SmappDataset
from elasticsearch import Elasticsearch
from elasticsearch import helpers

currentdate = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

def index_dataset(dataset_name, doc_type, db_host, db_port, db_user, db_pass, es_host):

	# Check if the dataset exists
	mongo = pymongo.MongoClient(db_host, int(db_port))
	database_names = mongo.database_names()
	if dataset_name not in database_names:
		print("Dataset {} does not exist.".format(dataset_name))
		logging.info("Dataset {} does not exist.".format(dataset_name))
		sys.exit(1)

	es = Elasticsearch([es_host],
						# find all es nodes in cluster
						sniff_on_start=True,
						# refresh nodes after a node fails to respond
						sniff_on_connection_fail=True)

	dataset = SmappDataset(['mongo', db_host, db_port, db_user, db_pass], collection_regex='(^data$|^tweets$|^tweets_\d+$)', database_regex='(^' + dataset_name + '$|^' + dataset_name + '_\d+$)')

	print("Indexing dataset {}...".format(dataset_name))
	logging.info("Indexing dataset...")
	for success, info in helpers.parallel_bulk(es, genereate_actions(dataset, dataset_name, doc_type), thread_count=4, chunk_size=5000):
		if not success:
			print('A document failed to index:', info)
			logging.info('A document failed to index:', info)

def genereate_actions(dataset, dataset_name, doc_type):
	for doc in dataset.get_collection_iterators():
		# Delete conflicting mongo ID & Irrelevant fields
		del doc['_id']
		del doc['random_number']
		# Create action object for bulk indexing
		yield {
			"_index": dataset_name.lower(),
			"_type": doc_type,
			"_id": doc['id_str'],
			"_source": doc
		}

def parse_args(args):
	parser = argparse.ArgumentParser()
	parser.add_argument('-n', '--dataset-name', dest='dataset_name', required=True, help='an existing mongodb dataset to index in elasticsearch.')
	parser.add_argument('-t', '--doc-type', dest='doc_type', required=True, help='the type of object in the dataset. e.g. tweet or user')
	parser.add_argument('-ho', '--db-host', dest='db_host', default='localhost', help='the host where mongodb is running')
	parser.add_argument('-p', '--db-port', dest='db_port', default='49999', help='the port on the host where mongodb is running')
	parser.add_argument('-u', '--db-user', dest='db_user', required=True, help='the username for the database to read from')
	parser.add_argument('-w', '--db-pass', dest='db_pass', required=True, help='password for this user')
	parser.add_argument('-eh', '--es-host', dest='es_host', default='localhost', help='the hostname/IP of a host that is a part of the elasticsearch cluster.')
	parser.add_argument('-l', '--log', dest='log', default=os.path.expanduser('~/pylogs/es_index_dataset_' + parser.parse_args().dataset_name +  '.log'), help='This is the path to where your output log should be.')
	return parser.parse_args(args)

if __name__ == '__main__':
	args = parse_args(sys.argv[1:])

	logging.basicConfig(filename=args.log, level=logging.INFO, filemode='w')
	logger = logging.getLogger(__name__)
	logging.info('@timestamp: {}'.format(currentdate))
	print('@timestamp: {}'.format(currentdate))

	index_dataset(args.dataset_name, args.doc_type, args.db_host, args.db_port, args.db_user, args.db_pass, args.es_host)

'''
author @Roman
'''
