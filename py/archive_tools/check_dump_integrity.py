import os
import re
import sys
import json
import logging
import pymongo
import argparse
import datetime

currentdate = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

CHECK_COLLECTIONS = 0
CHECK_TWEETS = 1

def check_dump_integrity(hostname, port, dbname, username, password, authdb, dump_dir, check_type = CHECK_COLLECTIONS):

	logger.info('\n' + 'checking integrity of {}'.format(dbname))

	# connect to the db
	mongo = pymongo.MongoClient(hostname, int(port))
	if username and password:
		mongo[authdb].authenticate(username, password)

	db = mongo[dbname]

	# Get a list of collections from the database named 'tweet' or 'tweets_#'
	db_collections = db.collection_names()
	db_tweet_collections = [match.group(1) for coll in db_collections for match in [re.compile('(^tweets$|^tweets_\d+$)').search(coll)] if match]
	db_tweet_collections.sort(key=len)

	#Get a list of dumped collections named tweet.bson or tweets_#.bson
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

	dump_tweet_collections = [match.group(1) for coll in dump_collections for match in [re.compile('(^tweets.bson$|^tweets_\d+.bson$)').search(coll)] if match]
	dump_tweet_collections.sort(key=len)

	#CHECK NUMBER OF TWEET COLLECTIONS
	if (check_type == CHECK_COLLECTIONS):
		num_tweet_collections_in_db = len(db_tweet_collections)
		num_tweet_collections_dumped = len(dump_tweet_collections)

		#Log the integrity of the dump
		log_output = 'DUMP FOR {} '.format(dbname)
		if not dump_exists:
			log_output += 'DOES NOT EXIST. '
		elif num_tweet_collections_dumped < num_tweet_collections_in_db:
			log_output += 'IS MISSING TWEET COLLECTIONS. '
		elif num_tweet_collections_dumped > num_tweet_collections_in_db:
			log_output += 'HAS TOO MANY TWEET COLLECTIONS. '
		else:
			log_output += 'IS OK. '
		log_output += 'Number of Tweet collections in database: {}, Number of Tweet collections dumped: {}'.format(num_tweet_collections_in_db, num_tweet_collections_dumped)
		logging.info(log_output)
		print('\n' + log_output)

		#Log list of missing tweet collections if relevant
		if dump_exists and (num_tweet_collections_dumped < num_tweet_collections_in_db):
			dump_tweet_collections_split = [dump_coll.split('.bson', 1)[0] for dump_coll in dump_tweet_collections]
			missing_tweet_collections = [db_tweet_coll for db_tweet_coll in db_tweet_collections if db_tweet_coll not in dump_tweet_collections_split]
			logging.info('\n' + 'Missing Tweet Collections: {}'.format(missing_tweet_collections))
			print('\n' + 'Missing Tweet Collections: {}'.format(missing_tweet_collections))

		# # print("\n {}".format(db_collections))
		# print('\n' + 'db_tweet_collections: {}'.format(db_tweet_collections))
		# # print('dump_collections: {}'.format(dump_collections))
		# print('dump_tweet_collections: {}'.format(dump_tweet_collections))

	#CHECK NUMBER OF TWEETS
	elif check_type == CHECK_TWEETS:

		total_tweets_in_database = 0

		#Query mongo for a list of mongo collections named 'tweets_#' for this data set
		#For each mongo collection in the returned list
			#num_tweets = Query mongo for the number of tweet objects
			#Add num_tweets to total_tweets_in_database
	
		total_tweets_dumped = 0

		#For each dumped mongo collection 'tweets_#.bson' in the data set's dump folder
			#Open bson file
			#num_tweets = number of tweets found in bson file
			#Add num_tweets to total_tweets_dumped

		#Log the integrity of the dump
		log_output = 'DUMP {} '.format(dbname)
		if total_tweets_dumped < total_tweets_in_database:
			log_output = 'IS MISSING TWEETS. '
		elif total_tweets_dumped > total_tweets_in_database:
			log_output = 'HAS TOO MANY TWEETS. '
		else:
			log_output = 'is OK, not missing any tweets. '
		log_output += 'Total Tweets in database: {}, Total Tweets dumped: {}'.format(total_tweets_in_database, total_tweets_dumped)
		logging.info(log_output)
		print(log_output)

def parse_args(args):
	parser = argparse.ArgumentParser()
	parser.add_argument('-i', '--input', dest='input', required=True, help='a list of mongo dumps for which to test the integrity. Either a .json file or direct input like @"name1 name2"')
	parser.add_argument('-d', '--dumpdir', dest='dump_dir', required=True, help='the path to the directory where the mongodumps are located')
	parser.add_argument('-ho', '--hostname', dest='hostname', default='localhost', help='the host where mongodb is running')
	parser.add_argument('-p', '--port', dest='port', default='27017', help='port on host where mongodb is running')
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

	#direct input
	if args.input[:1] == '@':
		input_list = args.input[1:].split()
		for db in input_list:
			check_dump_integrity(args.hostname, args.port, db, args.username, args.password, args.authdb, args.dump_dir, CHECK_COLLECTIONS)
			# check_dump_integrity(args.hostname, args.port, db, args.username, args.password, args.authdb, args.dump_dir, CHECK_TWEETS)
	#json file
	else: 
		with open(os.path.expanduser(args.input), 'r') as data:
			input_list = json.load(data)
			for db in input_list:
				check_dump_integrity(args.hostname, args.port, db, args.username, args.password, args.authdb, args.dump_dir, CHECK_COLLECTIONS)
				# check_dump_integrity(args.hostname, args.port, db, args.username, args.password, args.authdb, args.dump_dir, CHECK_TWEETS)

'''
author @Roman
'''
