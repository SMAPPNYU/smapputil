import os
import sys
import re
import json
import glob
import math
import datetime
import subprocess
import logging
import argparse
from shutil import copyfile, chown
from multiprocessing import Pool

import pandas as pd
import tweepy
from tweepy.error import TweepError

from config import *


def parse_args(args):
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', '--log', dest='log', 
                        default=os.path.expanduser('~/pylogs/filter_metadata.log'), 
                        help='This is the path where your output logging will go.')
    return parser.parse_args(args)

def check_connection():
    '''
    check tweepy authentication by calling `me()`.
    calls global api from config.py
    '''
    try:
        api.me()
        return True
    except(TweepError):
        return False

def read_filter_file(f):
    '''
    Reads a json filter file.
    Cleans up the dates,
    Parses the filters and returns a dict (d)
    '''
    collection_name = f.split('/')[3]
    tweets = []
    for line in open(f, 'rb'):
        tweet_json = json.loads(line.decode('utf-8'))
        tweet_clean = clean_dates(tweet_json)
        tweet_clean['collection'] = collection_name
        tweets.append(tweet_clean)

    return tweets

def clean_dates(d):
    '''
    Some of these files have dates of different formats.
    This script makes them the same!
    input: d is a dictionary of filter metadata
    ''' 
    
    if isinstance(d['date_added'], dict):
        d['date_added'] = datetime.datetime.fromtimestamp(
                  d["date_added"]["$date"] / 1000.0)
    elif d['date_added'] is None:
        # this means that no date added is associated with the filter term
        d['date_added'] = skip_date       
    elif not isinstance(d['date_added'], datetime.datetime):
        ### rethink this format - let's say the except also returns an error? use skip_date instaed?
        try:
            d['date_added'] = datetime.datetime.strptime(
                d["date_added"], "%a %b %d %H:%M:%S %z %Y")
        except:
            d['date_added'] = datetime.datetime.strptime(
                d["date_added"].split('T')[0], "%Y-%m-%d")

    d['date_added'] = datetime.datetime.strftime(
            d['date_added'], '%Y-%m-%d')

    return d

def update_user_ids(user_ids, logger):
    '''
    checks if file exists, if not creates a new files
    checks if each user's id already exists, and if it doesn't,
    calls tweepy api to get username for each id
    '''
    if os.path.exists(user_lookup_path):
        with open(user_lookup_path, 'r') as file:
            user_lookup = json.loads(file.read())
    else:
        user_lookup = {}

    for user_id in user_ids:
        user_id = str(user_id)
        if not user_id in user_lookup:
            logger.info("Looking up username for {}".format(user_id))
            username = get_username(user_id, logger)
            user_lookup[user_id] = username

    return user_lookup

def get_username(user_id, logger):
    '''
    gets users username with Tweepy
    calls global api variable
    '''
    try:
        u = api.get_user(user_id=user_id)
        return u.name
    
    except TweepError as e:
        logger.warning(TweepError)
        if e.api_code == 50: # not found
            return 'not found'
        elif e.api_code == 63: # suspended
            return 'user suspended'
        elif e.api_code == 64: # we are suspended!
            return -1
        else:
            return e.api_code

def get_context(title):
    '''
    Formats the name of the file, pattern can be found in config.py
    '''
    output_file = output_file_pattern.format(title)
    archive_file = archive_file_pattern.format(title)
    
    return output_file, archive_file

def convert_size(size_bytes):
    '''
    Bytes to a human-readable format.
    '''
    if size_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)

    return "%s %s" % (s, size_name[i])

def get_size(f):
    '''
    Gets the size of tweet files in aggregate, and of the latest file.
    '''
    # creates a regular expression for tweet files.
    collection_name = f.split('/')[3]
    regex = f.split('/filters/')[0] + '/data/*'
    files_in_f = glob.glob(regex)
    num_files = len(files_in_f)

    # calculate the file sizes
    bytes_ = sum([os.stat(f_).st_size for f_ in files_in_f])
    bytes_human = convert_size(bytes_)

    # gets the latest file and the date it was updated.
    newest = max(glob.iglob(regex), key=os.path.getctime)

    latest_filedate = datetime.datetime.fromtimestamp(
        os.path.getctime(newest))

    latest_bytes = os.stat(newest).st_size
    latest_bytes_human = convert_size(latest_bytes)

    row = dict(
        collection = collection_name,
        collection_size_bytes = bytes_,
        collection_size = bytes_human,
        collection_number_of_files = num_files,
        latest_filedate = latest_filedate,
        latest_filename = newest,
        latest_filesize = latest_bytes_human
    )

    return row
       
def rclone(src, dest):
    '''
    Calls the rclone program from the commandline.
    Used to copy over the output file from HPC to GDrive.
    '''
    process = subprocess.Popen([
        '/share/apps/rclone/1.35/bin/rclone copy {} {}'.format(
            src, dest
        )
    ], shell=True)

    return process.communicate()


def main():
    args = parse_args(sys.argv[1:])
    logging.basicConfig(filename=args.log, level=logging.INFO)
    logger = logging.getLogger(__name__)
    logger.info('Todays Date: %s', datetime.datetime.now().strftime("%Y-%m-%d_%H:%M"))

    logger.info("Checking Tweepy Authentication")
    if not check_connection():
        logger.warning("There was an authentication error")
        sys.exit("authentication error")

    logger.info("Reading the json files into a list")
    files = glob.glob('/scratch/olympus/*/filters/filters.json') # not including pre filters!
    with Pool(8) as pool: # map the function read_filter_file to 8 cores
        d = pool.map(read_filter_file, files)
    d_flat = [ent for sublist in d for ent in sublist]  # flatten the output

    logger.info('Putting the contents into a Pandas dataframe')
    df = pd.DataFrame(d_flat)
    df.sort_values(by='collection', inplace=True)    
    
    # collection meta
    collection_meta = []
    for f in files:
        collection_size = get_size(f)
        collection_meta.append(collection_size)
    df_size = pd.DataFrame(collection_meta)
    
    # terms tracked
    df_term = df[df["filter_type"] == "track"]
    df_term.loc[:, "keyword"] = df_term["value"]
    
    # users
    df_user = df[(df["filter_type"] == "follow") & 
                 (~df["collection"].isin(blacklist_collections))]
    user_ids = df_user["value"].unique()
    logger.info("Updating {} user ids".format(len(user_ids))) 
    user_lookup = update_user_ids(user_ids, logger) # this hits the tweepy api.
    user_names = df_user["value"].astype(str).replace(user_lookup)
    df_user.loc[:, "user.id"] = df_user["value"]
    df_user.loc[:, "user.name"] = user_names
    
    with open(user_lookup_path, 'w') as f:
        logger.info("Writing user lookup table to file")
        f.write(json.dumps(user_lookup))
        chown(user_lookup_path, group="smapp")
    
    logger.info("Writing results to a csv")
    for df__, title__ in zip([df_term, df_user, df_size], 
                             ['tracking_terms', 'following_users', 'collection_meta']):
        
        output_file, archive_file = get_context(title__)
        logger.info("Saving locally {}".format(output_file))
        
        cols = ['collection'] + [c for c in df__.columns if c not in cols_ignore]
        df__[cols].to_csv(output_file, index=False)
        chown(output_file, group="smapp")
        
        logger.info("Copying the {} into the archive".format(output_file))
        copyfile(output_file, archive_file)

        logger.info("Sending the files to {}".format(gdrive))
        rclone(output_file, gdrive)
        rclone(archive_file, gdrive_archive)
        
        logger.info("Finished successfully!")
    
main()

"""
This script reads the filter.json file connected to each Twitter collection to determine the users and terms that the collection is following. These two types of filters become their own files, which are saved in HPC, as well as Google Drive.
For users, we are only given user ids. So we must hit the Tweepy API to return user names.
Collections with randomly generated user ids are omitted from the user output file.
For variables that are seemingly missing, check the config.py file.
Note that Tweepy credentials and the rclone remote are pulled from enviornment variables in Prince.
Leon Yin
Nicole Baram
2018-01-05
"""
