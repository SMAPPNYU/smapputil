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

def index_dataset(dataset_name, doc_type, db_host, db_port, db_user, db_pass, es_instance, stream_after = False):
	print("Indexing dataset {}...".format(dataset_name))
	logger.info("Indexing dataset {}...".format(dataset_name))

	dataset = get_smapp_mongo_dataset(dataset_name, db_host, db_port, db_user, db_pass)
	start_bulk_indexing(es_instance, dataset, dataset_name, doc_type)

	if stream_after:
		print("Finished Initial import.")
		logger.info("Finished Initial import.")
		index_dataset_stream(dataset_name, doc_type, db_host, db_port, db_user, db_pass, es_instance)
	else:
		print("Done.")
		logger.info("Done.")

def index_dataset_stream(dataset_name, doc_type, db_host, db_port, db_user, db_pass, es_instance):
	print("Starting indexing stream for dataset {}...".format(dataset_name))
	logger.info("Starting indexing stream for dataset {}...".format(dataset_name))

	while True:
		#Query for timestamp of the latest indexed document in elasticsearch
		query = {
		  "query": {
		    "match_all": {}
		  },
		  "size": 1,
		  "sort": [
		    {
		      "timestamp_ms": {
		        "order": "desc"
		      }
		    }
		  ]
		}
		latest_doc = es_instance.search(index=dataset_name.lower(), doc_type=doc_type, body=query)
		latest_timestamp = latest_doc['hits']['hits'][0]['_source']['timestamp_ms']
		print(latest_timestamp)
		
		#Apply filter to dataset to get only documents at or after the latest timestamp
		dataset = get_smapp_mongo_dataset(dataset_name, db_host, db_port, db_user, db_pass)
		apply_filter_to_dataset(dataset, {'timestamp_ms':{'$gte':latest_timestamp}})
		start_bulk_indexing(es_instance, dataset, dataset_name, doc_type)

def start_bulk_indexing(es_instance, dataset, dataset_name, doc_type):
	for success, info in helpers.parallel_bulk(es_instance, generate_actions(dataset, dataset_name, doc_type), thread_count=4, chunk_size=5000):
		if not success:
			print('A document failed to index:', info)
			logger.info('A document failed to index:', info)

def generate_actions(dataset, dataset_name, doc_type):
	for doc in dataset.get_collection_iterators():
		# Delete conflicting mongo ID & Irrelevant fields
		doc.pop("_id", None)
		doc.pop("random_number", None)
		doc.pop("timestamp", None)
		doc.pop("smapp_timestamp", None)
		# Create action object for bulk indexing
		yield {
			"_index": dataset_name.lower(),
			"_type": doc_type,
			"_id": doc['id_str'],
			"_source": doc
		}

def get_smapp_mongo_dataset(dataset_name, db_host, db_port, db_user, db_pass):
	return SmappDataset(['mongo', db_host, db_port, db_user, db_pass], collection_regex='(^data$|^tweets$|^tweets_\d+$)', database_regex='(^' + dataset_name + '$|^' + dataset_name + '_\d+$)')

def apply_filter_to_dataset(dataset, filter_to_set):
	dataset.collections = [collection.set_filter(filter_to_set) for collection in dataset.collections]

def parse_args(args):
	parser = argparse.ArgumentParser()
	parser.add_argument('-n', '--dataset-name', dest='dataset_name', required=True, help='an existing mongodb dataset to index in elasticsearch.')
	parser.add_argument('-t', '--doc-type', dest='doc_type', required=True, help='the type of object in the dataset. e.g. tweet or user')
	parser.add_argument('-ho', '--db-host', dest='db_host', default='localhost', help='the host where mongodb is running')
	parser.add_argument('-p', '--db-port', dest='db_port', default='49999', help='the port on the host where mongodb is running')
	parser.add_argument('-u', '--db-user', dest='db_user', required=True, help='the username for the database to read from')
	parser.add_argument('-w', '--db-pass', dest='db_pass', required=True, help='password for this user')
	parser.add_argument('-eh', '--es-host', dest='es_host', default='localhost', help='the hostname/IP of a host that is a part of the elasticsearch cluster.')
	parser.add_argument('-sa', '--stream-after', dest='stream_after', action='store_true', default=False, help='after the initial import, continuously updates the dataset\'s index with the newest documents.')
	parser.add_argument('-sn', '--stream-now', dest='stream_now', action='store_true', default=False, help='skips the initial import and immediately starts updating the dataset\'s index with the newest documents.')
	parser.add_argument('-l', '--log', dest='log', default=os.path.expanduser('~/pylogs/es_index_dataset_' + parser.parse_args().dataset_name + '.log'), help='This is the path to where your output log should be.')
	return parser.parse_args(args)

if __name__ == '__main__':
	args = parse_args(sys.argv[1:])

	logging.basicConfig(filename=args.log, level=logging.INFO, filemode='w', format='%(asctime)s - %(levelname)s - %(message)s')
	logger = logging.getLogger(__name__)
	logging.info('@timestamp: {}'.format(currentdate))
	print('@timestamp: {}'.format(currentdate))

	# Connect to mongodb, check if the dataset exists
	mongo = pymongo.MongoClient(args.db_host, int(args.db_port))
	database_names = mongo.database_names()
	if args.dataset_name not in database_names:
		print("Dataset {} does not exist.".format(args.dataset_name))
		logger.info("Dataset {} does not exist.".format(args.dataset_name))
		sys.exit(1)

	# Connect to Elasticsearch, gather list of hosts 
	es_instance = Elasticsearch([args.es_host],
						# find all es nodes in cluster
						sniff_on_start=True,
						# refresh nodes after a node fails to respond
						sniff_on_connection_fail=True)

	if args.stream_now:
		index_dataset_stream(args.dataset_name, args.doc_type, args.db_host, args.db_port, args.db_user, args.db_pass, es_instance)
	else:
		index_dataset(args.dataset_name, args.doc_type, args.db_host, args.db_port, args.db_user, args.db_pass, es_instance, args.stream_after)

'''
author @Roman
'''
