import os
import sys
import json
import logging
import pymongo
import argparse
import datetime
import subprocess
from smappdragon import MongoCollection

currentdate = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

def dump_database(hostname, port, dbname, username, password, authdb, output_path):
    mongodump_string = "mongodump --host {}:{} -u {} -p '{}' -o {} -d {} --authenticationDatabase {}".format(hostname, port, username, password, output_path, dbname, authdb)
    logger.info('trying to start: {}'.format(mongodump_string))
    try:
        #check_output is like popen but blocks to w8 for output
        process_out = subprocess.check_output([mongodump_string], shell=True)
        logger.info('finished: {}'.format(mongodump_string))
        logger.info('output: {}'.format(process_out))
    except subprocess.CalledProcessError as e:
        logger.info('failed for reason: {} on data set: {}'.format(e, dbname))

def query_dump_database(hostname, port, dbname, username, password, authdb, authusername, authpassword, output_path):

    # connect to the db
    mongo = pymongo.MongoClient(hostname, int(port))
    if username and password:
        mongo[authdb].authenticate(authusername, authpassword)

    db = mongo[dbname]

    # Get a list of relevant collections from the database
    db_collection_names = db.collection_names()
    db_collection_names.sort()
    db_collection_names.sort(key=len)

    if len(db_collection_names) == 0:
        print("Database for {} is empty".format(dbname))
        logging.info("Database for {} is empty".format(dbname))
        return

    #Create dump folder
    dump_folder_path = output_path + dbname if output_path[-1:] == '/' else output_path + '/' + dbname
    if not os.path.exists(dump_folder_path):
        os.makedirs(dump_folder_path)
    else:
       print("Dump folder for {} already exists".format(dbname))
       logging.info("Dump folder for {} already exists".format(dbname))
       return 

    print("Dumping database {}".format(dbname))
    logging.info("Dumping {} database".format(dbname))

    #Use MongoCollection with dump_to_bson to dump each collection in the database
    for collection_name in db_collection_names:
        collection_dump_path = dump_folder_path + collection_name + '.json' if dump_folder_path[-1:] == '/' else dump_folder_path + '/' + collection_name + '.json'
        collection_to_dump = MongoCollection(hostname, port, username, password, dbname, collection_name)
        collection_to_dump.dump_to_json(collection_dump_path)

def parse_args(args):
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', dest='input', required=True, nargs='+', help='a list of dbs to mongodump. Either a .json file or list of names separated by spaces.')
    parser.add_argument('-ho', '--hostname', dest='hostname', help='')
    parser.add_argument('-u', '--username', dest='username', help='the username for this database to read/write on')
    parser.add_argument('-w', '--password', dest='password', help='password for this user on this db')
    parser.add_argument('-au', '--authusername', dest='authusername', help='the username for the admin db')
    parser.add_argument('-aw', '--authpassword', dest='authpassword', help='password for the admin db')
    parser.add_argument('-p', '--port', dest='port', default='49999', help='local port to map to the remoteport')
    parser.add_argument('-a', '--auth', dest='authdb', default='admin', help='the auth db')
    parser.add_argument('-o', '--outputpath', dest='outputpath', help='the path to the folder where you\'d like the mongodump to go')
    parser.add_argument('-l', '--log', dest='log', default=os.path.expanduser('~/pylogs/dump_database.log'), help='This is the path to where your output log should be.')
    parser.add_argument('-q', '--querydump', dest='querydump', action='store_true', default=False, help='pass this argument in to perform a query dump instead of a mongo dump')
    return parser.parse_args(args)

if __name__ == '__main__':
    args = parse_args(sys.argv[1:])

    logging.basicConfig(filename=args.log, level=logging.INFO)
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
        if args.querydump:
            query_dump_database(args.hostname, args.port, db, args.username, args.password, args.authdb, args.authusername, args.authpassword, args.outputpath)
        else:
            dump_database(args.hostname, args.port, db, args.username, args.password, args.authdb, args.outputpath)

'''
author @yvan
'''