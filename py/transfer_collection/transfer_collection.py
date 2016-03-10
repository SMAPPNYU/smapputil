'''
TODO: Preserve and merge all metadata (filter criteria, limits, deletes, post-filters, etc) 
'''

import pymongo
import logging
import argparse
import datetime

from itertools import islice
from os.path import expanduser

# set a logger to log to ~/pylogs
LOG_PROGRESS_EVERY = 10000
currentdate = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
logger = logging.getLogger("TweetCollector.TransferCollection")
logging.basicConfig(filename=expanduser('~/pylogs/transfer_tweet_data_'+currentdate+'.log'), level=logging.INFO)

'''
    Run admin command to shard collection. 
    collection  - pymongo Collection object
    Collection also must have a hashed object ID index to function properly
    (see ensure_hashed_id_index())
'''

def enable_collection_sharding(authed_mongo_target, target_db, collection):
    try:
        authed_mongo_target.admin.command(
            "shardCollection",
            "{}.{}".format(target_db, collection.name),
            key={'_id': "hashed"})
    except pymongo.errors.OperationFailure as e:
        logger.info('opfailure in sharding of collection {}'.format(e))

'''
    Create a hashed index on the _id field of the documents in this collection
    Create an index on the tweet's unique id
    Create an index on the document's random field
    Create an index document's timestamp field
'''
def ensure_hashed_id_index(collection):
    try:
        collection.create_index([('_id', pymongo.HASHED)], name="_id_hashed", background=True)
    except pymongo.errors.OperationFailure as e:
        logger.info('opfailure in create hashed index indexes {}'.format(e))
    try:
        collection.create_index('id', name="twitter_id", drop_dups=True, background=True)
    except pymongo.errors.OperationFailure as e:
        logger.info('opfailure in create index on twitter \'id\' field {}'.format(e))
    try:
        collection.create_index('random_number', name="index_random", background=True)
    except pymongo.errors.OperationFailure as e:
        logger.info('opfailure in random number {}'.format(e))
    try:
        collection.create_index('timestamp', name="index_timestamp", background=True)
    except pymongo.errors.OperationFailure as e:
        logger.info('opfailure in create index on random timestamp {}'.format(e))

'''
    groups bunches of code together
'''
def grouper(n, iterable):
    "grouper(3, 'ABCDEFG') --> ABC DEF G"
    it = iter(iterable)
    while True:
       chunk = tuple(islice(it, n))
       if not chunk:
           return
       yield chunk

'''
    Transfers objects between two collections using an unordered insert_many
    (batch/bulk insertion, unordered because it's supposed to be better for
    sharding:

    https://docs.mongodb.org/manual/core/bulk-write-operations/
    #strategies-for-bulk-inserts-to-a-sharded-collection
'''
def bulk_transfer(source_collection, target_collection, batch_size=500,
        logger=logger, progress=LOG_PROGRESS_EVERY):
    count = 0
    inserted = 0
    total = source_collection.count()

    logger.info("Beginning transfer from source to target:\n\t{0}\n\t{1}".format(
        source_collection, target_collection))
    logger.info("Total to transfer: {0}".format(total))

    for batch in grouper(batch_size, source_collection.find()):
        r = target_collection.insert_many(batch, ordered=False)
        count += len(batch)
        inserted += len(r.inserted_ids)
        if count % progress == 0:
            logger.debug("Processed {0} / {1}".format(count, total))
            logger.debug("Inserted {0} / {1}".format(inserted, count))

    logger.info("Transfered {0} of {1}".format(count, total))

'''
    Does a naive (no bulk inserts) transfer, one-by-one, 
    of all objects from source collection to target collection
'''
def naive_transfer(source_collection, target_collection, logger=logger,
        progress=LOG_PROGRESS_EVERY):
    count = 0
    total = source_collection.count()

    logger.info("Beginning transfer from source to target:\n\t{0}\n\t{1}".format(
        source_collection, target_collection))
    logger.info("Total to transfer: {0}".format(total))

    for tweet in source_collection.find():
        target_collection.insert_one(tweet)
        count += 1
        if count % progress == 0:
            logger.debug("Transfered {0} / {1}".format(count, total))

    logger.info("Transfered {0} of {1}".format(count, total))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--host", default="smapp.politics.fas.nyu.edu",
        help=" [smapp.politics.fas.nyu.edu] Mongo server for source data (to transfer to Target)")
    parser.add_argument("-p", "--port", type=int, default=27011,
        help="[27011] Source data mongo server port")
    parser.add_argument("-u", "--username", default=None,
        help="[None] Source data mongo server user")
    parser.add_argument("-w", "--password", default=None,
        help="[None] Source data mongo user password")
    parser.add_argument("-d", "--db", required=True,
        help="[Required] Database to transfer on source server")

    parser.add_argument("-ts", "--targethost", default="localhost",
        help="[localhost] Target mongo server to transfer data to")
    parser.add_argument("-tp", "--targetport", type=int, default=27017,
        help="[49999] Target mongo server port")
    parser.add_argument("-tu", "--targetuser", default=None,
        help="[None] Target mongo server user")
    parser.add_argument("-tw", "--targetpassword", default=None,
        help="[None] Target mongo user password")
    parser.add_argument("-td", "--targetdb", required=True,
        help="[Required] Database to transfer source data in to")

    parser.add_argument("-au", "--ausr", required=True,
        help="[None] Source data mongo server user")
    parser.add_argument("-aw", "--apwd", required=True,
        help="[None] Source data mongo user password")
    parser.add_argument("-adb", "--adb", required=True,
        help="[Required] Database to transfer on source server")

    args = parser.parse_args()

    # connect to the db
    # then get a list of collections
    source_mongo = pymongo.MongoClient(args.host, int(args.port))
    source_db = source_mongo[args.db]
    source_metadata_collection = source_db['smapp_metadata']
    if args.username and args.password:
        source_db.authenticate(args.username, args.password)
    source_metadata_document = source_metadata_collection.find_one({'document': 'smapp-tweet-collection-metadata'})
    source_collections_list = source_metadata_document['tweet_collections'][::-1]

    target_mongo = pymongo.MongoClient(args.targethost, int(args.targetport))
    target_db = target_mongo[args.targetdb]
    target_metadata_collection = target_db['smapp_metadata']
    if args.targetuser and args.targetpassword and args.ausr and args.apwd:
        authed_mongo_target = target_mongo[args.adb].authenticate(args.ausr, args.apwd)
        target_db.authenticate(args.targetuser, args.targetpassword)
    target_metadata_document = target_metadata_collection.find_one({'document': 'smapp-tweet-collection-metadata'})
    target_collections_list = target_metadata_document['tweet_collections']

    logger.info("Source DB tweet collections: {0}".format(source_collections_list))
    logger.info("Target DB tweet collections: {0}".format(target_collections_list))
    logger.info("Reverse-ordered source collections to transfer: {0}".format(source_collections_list))

    for source_collection_name in source_collections_list:
        # Check if collection exists and is nonempty
        if source_db[source_collection_name].count() <= 0:
            logger.info("Collection {0} empty. Skipping".format(source_collection_name))
            continue

        if source_collection_name in target_db.collection_names():
            logger.info("Collection of tweets exists on target db, inserting into: {0}".format(source_collection_name))
            print 'if ' + source_collection_name
        else:
            logger.info("Creating new collection on target: {0}".format(source_collection_name))
            print 'else ' + source_collection_name
            target_db.create_collection(source_collection_name)
            logger.info("Adding new collection to metadata and saving")
            target_collections_list.insert(0, source_collection_name)
            target_db['smapp_metadata'].update_one({'document': 'smapp-tweet-collection-metadata'}, {'$set': {'tweet_collections': target_collections_list}})
        # Create indexes and enable sharding on new collection
        logger.info("Creating indexes and enabling sharding on {0}".format(source_collection_name))

        ensure_hashed_id_index(target_db[source_collection_name])
        enable_collection_sharding(authed_mongo_target, target_db,target_db[source_collection_name])
        
        # BULK (chunk-wise insert, to speed up)
        bulk_transfer(source_db[source_collection_name], target_db[source_collection_name])

    logger.info("Transfer of all collections from source complete")
