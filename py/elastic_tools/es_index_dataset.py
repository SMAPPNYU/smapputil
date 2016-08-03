import os
import sys
import time
import json
import pymongo
import logging
import argparse
import datetime
from pysmap import SmappDataset
from elasticsearch import Elasticsearch
from elasticsearch import helpers

MONGO_FIELD_OBJ_ID = "_id"

SMAPP_FIELD_RANDOM_NUMBER = "random_number"
SMAPP_FIELD_TIMESTAMP = "timestamp"
SMAPP_FIELD_SMAPP_TIMESTAMP = "smapp_timestamp"

ES_FIELD_IS_RETWEET_STATUS = "es_is_retweet_status"

TWITTER_FIELD_CREATED_AT = "created_at"
TWITTER_FIELD_RETWEETED_STATUS = "retweeted_status"

PRELIM_IMPORT_CHECK_MINUTES = 5
PRELIM_IMPORT_BATCH_HOURS = 24

indexed_date_field = None
currentdate = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

def index_dataset_preliminary_import(dataset_name, doc_type, db_host, db_port, db_user, db_pass, es_instance, start_date):
	print("Starting preliminary import for dataset {} from {}...".format(dataset_name, start_date))
	logger.info("Starting preliminary import for dataset {} from {}...".format(dataset_name, start_date))

	current_date_range_batch = (start_date, start_date + datetime.timedelta(hours=PRELIM_IMPORT_BATCH_HOURS))
	while True:
		try:
			# print("current date range batch: {}".format(current_date_range_batch))
			# logger.info("current date range batch: {}".format(current_date_range_batch))

			# Create fresh dataset
			dataset = get_smapp_mongo_dataset(dataset_name, db_host, db_port, db_user, db_pass)

			# Apply filter to dataset to get only documents at or after the latest date
			apply_filter_to_dataset(dataset, {indexed_date_field:{'$gte':current_date_range_batch[0], '$lt':current_date_range_batch[1]}})

			start_bulk_indexing(es_instance, dataset, dataset_name, doc_type)

			# Check if need to continue or if we are all caught up and ready to stream again
			latest_es_date = es_get_latest_date(es_instance, dataset_name, doc_type)
			latest_mongo_date = get_latest_date_in_dataset(dataset, indexed_date_field)
			latest_delta = latest_mongo_date - latest_es_date
			if latest_delta > datetime.timedelta(minutes=PRELIM_IMPORT_CHECK_MINUTES):
				# Move to next date range batch
				current_date_range_batch = (current_date_range_batch[1], current_date_range_batch[1] + datetime.timedelta(hours=PRELIM_IMPORT_BATCH_HOURS))
				continue
			else:
				print("Done with preliminary import for dataset {}.".format(dataset_name))
				logger.info("Done with preliminary import for dataset {}.".format(dataset_name))
				break
		except Exception as e:
			print(e)
			logger.info(e)
			time.sleep(10)
			print("Repeating date range batch {} for dataset {}.".format(current_date_range_batch, dataset_name))
			logger.info("Repeating date range batch {} for dataset {}.".format(current_date_range_batch, dataset_name))

def index_dataset_stream(dataset_name, doc_type, db_host, db_port, db_user, db_pass, es_instance, should_stream_now):
	print("Starting indexing stream for dataset {}...".format(dataset_name))
	logger.info("Starting indexing stream for dataset {}...".format(dataset_name))

	dataset = get_smapp_mongo_dataset(dataset_name, db_host, db_port, db_user, db_pass)

	num_docs = es_instance.count(index=dataset_name.lower(), doc_type=doc_type)
	latest_es_date = None
	if num_docs['count'] != 0:
		print("ES Index {} is not empty. Starting stream using latest date in es index.".format(dataset_name.lower()))
		logger.info("ES Index {} is not empty. Starting stream using latest date in es index.".format(dataset_name.lower()))
		latest_es_date = es_get_latest_date(es_instance, dataset_name, doc_type)
	elif should_stream_now:
		print("ES Index {} is empty and --stream-now was specified. Starting stream using latest date in mongo dataset.".format(dataset_name.lower()))
		logger.info("ES Index {} is empty and --stream-now was specified. Starting stream using latest date in mongo dataset.".format(dataset_name.lower()))
		latest_es_date = get_latest_date_in_dataset(dataset, indexed_date_field)
	else:
		print("Unable to start stream. ES Index {} is empty, and --stream-now was not specified.".format(dataset_name.lower()))
		logger.info("Unable to start stream. ES Index {} is empty, and --stream-now was not specified.".format(dataset_name.lower()))
		sys.exit(1)

	# Clean up dataset
	dataset = None

	needs_prelim_check = False
	while True:
		try:
			# If its been too long since we were last streaming, do another preliminary import
			if needs_prelim_check:
				latest_mongo_date = get_latest_date_in_dataset(dataset, indexed_date_field)
				latest_delta = latest_mongo_date - latest_es_date
				if latest_delta > datetime.timedelta(minutes=PRELIM_IMPORT_CHECK_MINUTES):
					# Since streaming won't leave gaps, start from batch after last indexed doc in elasticsearch
					index_dataset_preliminary_import(dataset_name, doc_type, db_host, db_port, db_user, db_pass, es_instance, latest_es_date)

				needs_prelim_check = False
				# Continue with streaming if/after we're caught up
				print("Starting indexing stream for dataset {}...".format(dataset_name))
				logger.info("Starting indexing stream for dataset {}...".format(dataset_name))

			# Create fresh dataset
			dataset = get_smapp_mongo_dataset(dataset_name, db_host, db_port, db_user, db_pass)

			# Apply filter to dataset to get only documents at or after the latest date
			apply_filter_to_dataset(dataset, {indexed_date_field:{'$gte':latest_es_date}})

			start_bulk_indexing(es_instance, dataset, dataset_name, doc_type)

			# Query for date of the latest indexed document in elasticsearch
			latest_es_date = es_get_latest_date(es_instance, dataset_name, doc_type)
		except Exception as e:
			print(e)
			logger.info(e)
			needs_prelim_check = True
			time.sleep(10)

# ES METHODS

def start_bulk_indexing(es_instance, dataset, dataset_name, doc_type):
	for success, info in helpers.parallel_bulk(es_instance, generate_actions(dataset, dataset_name, doc_type), thread_count=4, chunk_size=1000):
		if not success:
			print('A document failed to index: {}'.format(info))
			logger.info('A document failed to index: {}'.format(info))

# Generator which yields actions for bulk indexing using the SmappDataset generator
def generate_actions(dataset, dataset_name, doc_type):
	for doc in dataset.get_collection_iterators():
		# Delete conflicting mongo ID & Irrelevant fields
		doc.pop(MONGO_FIELD_OBJ_ID, None)
		doc.pop(SMAPP_FIELD_RANDOM_NUMBER, None)
		doc.pop(SMAPP_FIELD_TIMESTAMP, None)
		doc.pop(SMAPP_FIELD_SMAPP_TIMESTAMP, None)
		# Add new is_retweet_status bool field to support quick retweet vs non-retweet visualizations
		if TWITTER_FIELD_RETWEETED_STATUS in doc:
			doc[ES_FIELD_IS_RETWEET_STATUS] = True
		else:
			doc[ES_FIELD_IS_RETWEET_STATUS] = False

		# Create action object for bulk indexing
		yield {
			"_index": dataset_name.lower(),
			"_type": doc_type,
			"_id": doc['id_str'],
			"_source": doc
		}

def es_get_latest_date(es_instance, dataset_name, doc_type):
	latest_query = {
	  "query": {
		"match_all": {}
	  },
	  "size": 1,
	  "sort": [
		{
		  TWITTER_FIELD_CREATED_AT: {
			"order": "desc"
		  }
		}
	  ]
	}
	latest_doc = es_instance.search(index=dataset_name.lower(), doc_type=doc_type, body=latest_query)
	latest_date = latest_doc['hits']['hits'][0]['_source'][TWITTER_FIELD_CREATED_AT]

	#Convert latest date to ISO format equivalent
	return datetime.datetime.strptime(latest_date, "%a %b %d %H:%M:%S +0000 %Y")

# MONGO METHODS

def get_smapp_mongo_dataset(dataset_name, db_host, db_port, db_user, db_pass):
	return SmappDataset(['mongo', db_host, db_port, db_user, db_pass], collection_regex='(^data$|^tweets$|^tweets_\d+$)', database_regex='(^' + dataset_name + '$|^' + dataset_name + '_\d+$)')

def apply_filter_to_dataset(dataset, filter_to_set):
	dataset.collections = [collection.set_filter(filter_to_set) for collection in dataset.collections]

def get_oldest_date_in_dataset(dataset, date_field):
	oldest_date = None
	for collection in dataset.collections:
		doc = collection.mongo_collection.find_one(filter=None, sort=([(date_field, pymongo.ASCENDING)]))
		# date = datetime.datetime.strptime(doc[date_field],'%a %b %d %H:%M:%S +0000 %Y')
		date = doc[date_field]
		if oldest_date == None or date < oldest_date:
			oldest_date = date

	return oldest_date

def get_latest_date_in_dataset(dataset, date_field):
	latest_date = None
	for collection in dataset.collections:
		doc = collection.mongo_collection.find_one(filter=None, sort=([(date_field, pymongo.DESCENDING)]))
		# date = datetime.datetime.strptime(doc[date_field],'%a %b %d %H:%M:%S +0000 %Y')
		date = doc[date_field]
		if latest_date == None or date > latest_date:
			latest_date = date

	return latest_date

def print_date_info(dataset, dataset_name, doc_type, es_instance):
	oldest_date = get_oldest_date_in_dataset(dataset, indexed_date_field)
	latest_date = get_latest_date_in_dataset(dataset, indexed_date_field)

	num_docs = es_instance.count(index=dataset_name.lower(), doc_type=doc_type)
	latest_es_date = None
	if num_docs['count'] != 0:
		latest_es_date = es_get_latest_date(es_instance, dataset_name, doc_type)

	print("oldest mongo date: {}".format(oldest_date))
	logger.info("oldest mongo date: {}".format(oldest_date))
	print("latest mongo date: {}".format(latest_date))
	logger.info("latest mongo date: {}".format(latest_date))
	print("latest es date: {}".format(latest_es_date))
	logger.info("latest es date: {}".format(latest_es_date))
		
def parse_args(args):
	parser = argparse.ArgumentParser()
	parser.add_argument('-n', '--dataset-name', dest='dataset_name', required=True, help='an existing mongodb dataset to index in elasticsearch.')
	parser.add_argument('-t', '--doc-type', dest='doc_type', required=True, help='the type of object in the dataset. e.g. tweet or user')
	parser.add_argument('-ho', '--db-host', dest='db_host', default='localhost', help='the host where mongodb is running')
	parser.add_argument('-p', '--db-port', dest='db_port', default='49999', help='the port on the host where mongodb is running')
	parser.add_argument('-u', '--db-user', dest='db_user', required=True, help='the username for the database to read from')
	parser.add_argument('-w', '--db-pass', dest='db_pass', required=True, help='password for this user')
	parser.add_argument('-eh', '--es-host', dest='es_host', default='localhost', help='the hostname/IP of a host that is a part of the elasticsearch cluster.')
	parser.add_argument('-sn', '--stream-now', dest='should_stream_now', action='store_true', default=False, help='pass in this argument to skip the preliminary import of existing data and go straight to streaming.')
	parser.add_argument('-l', '--log', dest='log', default=os.path.expanduser('~/pylogs/es_index_dataset_' + parser.parse_args().dataset_name + '.log'), help='This is the path to where your output log should be.')
	return parser.parse_args(args)

if __name__ == '__main__':
	args = parse_args(sys.argv[1:])

	logging.basicConfig(filename=args.log, filemode='w', format='%(asctime)s - %(levelname)s - %(message)s')
	logger = logging.getLogger(__name__)
	logger.setLevel(logging.INFO)
	pylogger = logging.getLogger('elasticsearch.trace')
	pylogger.setLevel(logging.WARNING)
	print('@timestamp: {}'.format(currentdate))
	logger.info('@timestamp: {}'.format(currentdate))

	# Connect to mongodb, check if the dataset exists
	mongo = pymongo.MongoClient(args.db_host, int(args.db_port))
	database_names = mongo.database_names()
	if args.dataset_name not in database_names:
		print("Dataset {} does not exist.".format(args.dataset_name))
		logger.info("Dataset {} does not exist.".format(args.dataset_name))
		sys.exit(1)
	mongo.close()

	# Find out which date field to use for streaming
	dataset = get_smapp_mongo_dataset(args.dataset_name, args.db_host, args.db_port, args.db_user, args.db_pass)
	for doc in dataset.get_collection_iterators():
		if SMAPP_FIELD_SMAPP_TIMESTAMP in doc:
			indexed_date_field = SMAPP_FIELD_SMAPP_TIMESTAMP
		elif SMAPP_FIELD_TIMESTAMP in doc:
			indexed_date_field = SMAPP_FIELD_TIMESTAMP
		else:
			print("Can't stream dataset {}. Couldn't find recognized indexed date field.".format(args.dataset_name))
			logger.info("Can't stream dataset {}. Couldn't find recognized indexed date field.".format(args.dataset_name))
		break

	# Connect to Elasticsearch, gather list of hosts 
	es_instance = Elasticsearch([args.es_host],
						# find all es nodes in cluster
						sniff_on_start=True,
						# refresh nodes after a node fails to respond
						sniff_on_connection_fail=True)

	print_date_info(dataset, args.dataset_name, args.doc_type, es_instance)
	
	# Need to do a preliminary import first until we're caught up for streaming
	prelim_start_date = None
	num_docs = es_instance.count(index=args.dataset_name.lower(), doc_type=args.doc_type)
	# If index is empty, start from oldest date in mongo
	if num_docs['count'] == 0:
		# If should_stream_now specified, skip preliminary import and go straight to streaming
		if not args.should_stream_now:
			print("ES Index {} is empty, starting preliminary import from beginning of mongo dataset.".format(args.dataset_name.lower()))
			logger.info("ES Index {} is empty, starting preliminary import from beginning of mongo dataset.".format(args.dataset_name.lower()))
			prelim_start_date = get_oldest_date_in_dataset(dataset, indexed_date_field)
			index_dataset_preliminary_import(args.dataset_name, args.doc_type, args.db_host, args.db_port, args.db_user, args.db_pass, es_instance, prelim_start_date)
	# Otherwise, start from batch before last indexed doc in elasticsearch
	else:
		print("ES Index {} is not empty, starting preliminary import from latest date in es index.".format(args.dataset_name.lower()))
		logger.info("ES Index {} is not empty, starting preliminary import from latest date in es index.".format(args.dataset_name.lower()))
		prelim_start_date = es_get_latest_date(es_instance, args.dataset_name, args.doc_type) - datetime.timedelta(hours=PRELIM_IMPORT_BATCH_HOURS)
		index_dataset_preliminary_import(args.dataset_name, args.doc_type, args.db_host, args.db_port, args.db_user, args.db_pass, es_instance, prelim_start_date)

	# Clean up dataset
	dataset = None

	index_dataset_stream(args.dataset_name, args.doc_type, args.db_host, args.db_port, args.db_user, args.db_pass, es_instance, args.should_stream_now)

'''
author @Roman
'''
