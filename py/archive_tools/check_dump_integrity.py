import os
import re
import sys
import json
import logging
import pymongo
import argparse
import datetime
import textwrap
from pysmap import SmappCollection

currentdate = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

#check_type
COUNT_COLLECTIONS = 0
COUNT_DOCUMENTS = 1

DB_RELEVANT_COLLECTIONS_REGEX = re.compile('(^tweets$|^tweets_\d+$)') # 'tweets' or 'tweets_#'
DUMP_RELEVANT_COLLECTIONS_REGEX = re.compile('(^tweets.bson$|^tweets_\d+.bson$)') # tweets.bson or tweets_#.bson

def check_dump_integrity(hostname, port, dbname, username, password, authdb, dump_dir, check_type = COUNT_COLLECTIONS):

	# connect to the db
	mongo = pymongo.MongoClient(hostname, int(port))
	if username and password:
		mongo[authdb].authenticate(username, password)

	db = mongo[dbname]

	# Get a list of relevant collections from the database
	db_collections = db.collection_names()
	db_relevant_collections = [match.group(1) for coll in db_collections for match in [DB_RELEVANT_COLLECTIONS_REGEX.search(coll)] if match]
	db_relevant_collections.sort()
	db_relevant_collections.sort(key=len)

	#Get a list of relevant collections from the dump
	dump_exists = True
	dump_path = dump_dir + dbname if dump_dir[-1:] == '/' else dump_dir + '/' + dbname
	dump_collections = []
	try:
		dump_collections = [file for file in os.listdir(dump_path)]
	except OSError as e:
		if e.errno == 2:
			dump_exists = False
		else:
			logging.error(e)
			print(e)

	dump_relevant_collections = [match.group(1) for coll in dump_collections for match in [DUMP_RELEVANT_COLLECTIONS_REGEX.search(coll)] if match]
	dump_relevant_collections.sort()
	dump_relevant_collections.sort(key=len)

	#CHECK NUMBER OF COLLECTIONS
	if check_type == COUNT_COLLECTIONS:
		num_collections_in_db = len(db_relevant_collections)
		num_collections_dumped = len(dump_relevant_collections)

		#Print integrity of number of collections in dump
		log_output = 'DUMP FOR {} '.format(dbname)
		if not dump_exists:
			log_output += 'DOES NOT EXIST. '
		elif num_collections_dumped < num_collections_in_db:
			log_output += 'IS MISSING COLLECTIONS. '
		elif num_collections_dumped > num_collections_in_db:
			log_output += 'HAS TOO MANY COLLECTIONS. '
		else:
			log_output += 'IS OK ON COLLECTIONS. '
		log_output += 'Number of collections in database: {}, Number of collections dumped: {}'.format(num_collections_in_db, num_collections_dumped)
		logging.info('\n' + log_output)
		print('\n' + log_output)

		#Print list of any collections missing from dump
		if dump_exists and (num_collections_dumped < num_collections_in_db):
			dump_relevant_collections_split = [dump_coll.split('.bson', 1)[0] for dump_coll in dump_relevant_collections]
			missing_collections = [coll for coll in db_relevant_collections if coll not in dump_relevant_collections_split]
			missing_collections.sort()
			missing_collections.sort(key=len)
			logging.info('\n' + 'Missing Collections: {}'.format(missing_collections))
			print('\n' + 'Missing Collections: {}'.format(missing_collections))

	#CHECK NUMBER OF DOCUMENTS
	elif check_type == COUNT_DOCUMENTS:
		logger.info('\n' + 'Counting number of documents in {} database'.format(dbname))
		print('\n' + 'Counting number of documents in {} database'.format(dbname))

		total_documents_in_db = 0
		db_collection_doc_counts = {}

		#Sum total documents in db
		for coll in db_relevant_collections:
			num_docs_in_coll = db[coll].count()
			total_documents_in_db += num_docs_in_coll

			#Save document count for db collection
			db_collection_doc_counts[coll] = num_docs_in_coll

			logging.info("Database {} {} document count: {}".format(dbname, coll, num_docs_in_coll))
			print("Database {} {} document count: {}".format(dbname, coll, num_docs_in_coll))
	
		logger.info('\n' + 'Counting number of documents in {} dump'.format(dbname))
		print('\n' + 'Counting number of documents in {} dump'.format(dbname))

		total_documents_dumped = 0
		dump_collection_doc_counts = {}

		#Sum up total number of documents in dump
		for coll in dump_relevant_collections:
			collection = SmappCollection('bson', dump_path + '/' + coll)
			num_docs_in_coll = collection.count_tweets()
			total_documents_dumped += num_docs_in_coll

			#Save document count for dump collection
			dump_collection_doc_counts[coll.split('.bson', 1)[0]] = num_docs_in_coll

			logging.info("Dump {} {} document count: {}".format(dbname, coll, num_docs_in_coll))
			print("Dump {} {} document count: {}".format(dbname, coll, num_docs_in_coll))

		#Print integrity of number of documents in dump
		log_output = 'DUMP FOR {} '.format(dbname)
		if not dump_exists:
			log_output += 'DOES NOT EXIST. '
		elif total_documents_dumped < total_documents_in_db:
			log_output += 'IS MISSING DOCUMENTS. '
		elif total_documents_dumped > total_documents_in_db:
			log_output += 'HAS TOO MANY DOCUMENTS. '
		else:
			log_output += 'IS OK ON DOCUMENTS. '
		log_output += 'Total documents in database: {}, Total documents dumped: {}'.format(total_documents_in_db, total_documents_dumped)
		logging.info('\n' + log_output)
		print('\n' + log_output)

		#Print list of any collections from dump missing documents
		if dump_exists and (total_documents_dumped < total_documents_in_db):
			collections_missing_docs = [coll for coll, count in db_collection_doc_counts.items() if (coll not in dump_collection_doc_counts or dump_collection_doc_counts[coll] != count)]
			collections_missing_docs.sort()
			collections_missing_docs.sort(key=len)
			logging.info('\n' + 'Collections Missing Documents: {}'.format(collections_missing_docs))
			print('\n' + 'Collections Missing Documents: {}'.format(collections_missing_docs))

def parse_args(args):
	parser = argparse.ArgumentParser()
	parser.add_argument('-i', '--input', dest='input', required=True, nargs='+', help='a list of mongo dumps for which to test the integrity. Either a .json file or list of names separated by spaces.')
	parser.add_argument('-d', '--dumpdir', dest='dump_dir', required=True, help='the path to the directory where the mongodumps are located')
	parser.add_argument('-ho', '--hostname', dest='hostname', default='localhost', help='the host where mongodb is running')
	parser.add_argument('-p', '--port', dest='port', default='49999', help='port on host where mongodb is running')
	parser.add_argument('-u', '--username', dest='username', help='the username for the databases to read from')
	parser.add_argument('-w', '--password', dest='password', help='password for this user')
	parser.add_argument('-a', '--auth', dest='authdb', default='admin', help='the auth db')
	parser.add_argument('-l', '--log', dest='log', default=os.path.expanduser('~/pylogs/check_dump_integrity.log'), help='This is the path to where your output log should be.')
	return parser.parse_args(args)

if __name__ == '__main__':
	args = parse_args(sys.argv[1:])

	logging.basicConfig(filename=args.log, level=logging.INFO, filemode='w')
	logger = logging.getLogger(__name__)
	logging.info('@timestamp: {}'.format(currentdate))

	input_list = []

	#json input
	if '.json' in args.input[0]:
		with open(os.path.expanduser(args.input[0]), 'r') as data:
			input_list = json.load(data)
	#direct input
	else:
		input_list = args.input

	for db in input_list:
		intro_string = textwrap.dedent(
		"""\n
		****{}*****
		*   {}   *
		****{}*****
		""".format('*' * len(db),db,'*' * len(db)))
		logging.info(intro_string)
		print(intro_string)

		check_dump_integrity(args.hostname, args.port, db, args.username, args.password, args.authdb, args.dump_dir, COUNT_COLLECTIONS)
		check_dump_integrity(args.hostname, args.port, db, args.username, args.password, args.authdb, args.dump_dir, COUNT_DOCUMENTS)

	logging.info('\n')
	print('\n')
	
'''
author @Roman
'''
