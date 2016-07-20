import os
import sys
import json
import logging
import argparse
import datetime
from pysmap import SmappDataset
from elasticsearch import Elasticsearch
from elasticsearch import helpers

currentdate = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

def index_dataset(dataset_name, doc_type, db_host, db_port, db_user, db_pass, es_hosts):

	dataset = SmappDataset(['mongo', db_host, db_port, db_user, db_pass], collection_regex='(^data$|^tweets$|^tweets_\d+$)', database_regex='(^' + dataset_name + '$|^' + dataset_name + '_\d+$)')

	es = Elasticsearch()
	count = 0
	actions = []
	# Index documents in batches of 5000
	for doc in dataset.get_collection_iterators():
	# 	# Delete conflicting mongo ID & Irrelevant fields
	# 	del doc['_id']
	# 	del doc['random_number']
	#     action = {
	#         "_index": dataset_name,
	#         "_type": doc_type,
	#         "_id": doc['id_str'],
	#         "_source": doc
	#         "chunk_size": 5000
	#     }
	#     actions.append(action)
	#     count += 1
	#     if count == 5000:
	#    		helpers.bulk(es, actions)
	#    		actions = []
	# # Index any remaining documents
	# if len(actions) > 0:
	# 	helpers.bulk(es, actions)
	# 	actions = []
		print(doc)

def parse_args(args):
	parser = argparse.ArgumentParser()
	parser.add_argument('-n', '--dataset-name', dest='dataset_name', required=True, help='an existing mongodb dataset to index in elasticsearch.')
	parser.add_argument('-t', '--doc-type', dest='doc_type', required=True, help='the type of object in the dataset. e.g. tweet or user')
	parser.add_argument('-h', '--db-host', dest='db_host', default='localhost', help='the host where mongodb is running')
	parser.add_argument('-p', '--db-port', dest='db_port', default='49999', help='the port on the host where mongodb is running')
	parser.add_argument('-u', '--db-user', dest='db_user', required=True, help='the username for the database to read from')
	parser.add_argument('-w', '--db-pass', dest='db_pass', required=True, help='password for this user')
	parser.add_argument('-eh', '--es-hosts', dest='es_hosts', required=True, help='list of elasticsearch data-node hosts, separated by spaces.')
	parser.add_argument('-l', '--log', dest='log', default=os.path.expanduser('~/pylogs/' + os.path.basename(__file__) + parser.parse_args().dataset_name +  '.log'), help='This is the path to where your output log should be.')
	return parser.parse_args(args)

if __name__ == '__main__':
	args = parse_args(sys.argv[1:])

	logging.basicConfig(filename=args.log, level=logging.INFO, filemode='w')
	logger = logging.getLogger(__name__)
	logging.info('@timestamp: {}'.format(currentdate))

	index_dataset(dataset_name, doc_type, db_host, db_port, db_user, db_pass, es_hosts)

'''
author @Roman
'''
