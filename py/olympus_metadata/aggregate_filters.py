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

import pandas as pd
import tweepy
from tweepy.error import TweepError


from config import *

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


def return_size(f):
    '''
    Gets the size of tweet files in aggregate and of the latest file.
    '''
    # creates a regular expression for tweet files.
    regex = f.split('/filters/')[0] + '/data/*'
    files_in_f = glob.glob(regex)
    num_files = len(files_in_f)

    # calculate the file sizes
    bytes_ = sum([os.stat(f_).st_size for f_ in files_in_f])
    bytes_human = convert_size(bytes_)
    avg_size = bytes_ / num_files
    avg_size_human = convert_size(avg_size)

    # gets the latest file and the date it was updated.
    newest = max(glob.iglob(regex), key=os.path.getctime)

    latest_filedate = datetime.datetime.fromtimestamp(
        os.path.getctime(newest)
    )

    latest_bytes = os.stat(newest).st_size
    latest_bytes_human = convert_size(latest_bytes)

    row = dict(
        bytes_ = bytes_,
        bytes_human = bytes_human,
        num_file = num_files,
        avg_size = avg_size,
        avg_size_human = avg_size_human,
        latest_filedate = latest_filedate,
        latest_file = newest,
        latest_bytes = latest_bytes,
        latest_bytes_human = latest_bytes_human
    )

    return row

def append_collection(t, f):
    '''
    Gets metadata about a filter.json file.
    '''
    t['collection'] = f.split('/')[3]

    row = return_size(f)

    z = {**t, **row}

    return z


def clean_dates(d):
    '''
    Some of these files have dates of different formats.
    This script makes them the same!

    input: d is a dictionary of filter metadata
    '''
    if isinstance(d['date_added'], dict):
        d['date_added'] = datetime.datetime.fromtimestamp(
                  d["date_added"]["$date"]/1000.0)
    elif d['date_added'] is None:
        d['date_added'] = datetime.datetime(1950, 1, 1)
    elif not isinstance(d['date_added'], datetime.datetime):
        try:
            d['date_added'] = datetime.datetime.strptime(
                d["date_added"], "%a %b %d %H:%M:%S %z %Y")
        except:
            d['date_added'] = datetime.datetime.strptime(
                d["date_added"].split('T')[0], "%Y-%m-%d")

    d['date_added'] = datetime.datetime.strftime(
            d['date_added'], '%Y-%m-%d')

    return d


def rclone(src, dest):
    '''
    Calls the rclone program from the commandline.
    Used to copy over the output file from HPC to GDrive.
    '''
    result = subprocess.Popen([
        '/share/apps/rclone/1.35/bin/rclone copy {} {}'.format(
            src, dest
        )
    ], shell=True)

    return result.communicate()

def check_connection():
    '''
    check tweepy authentication by calling "me"!

    calls global api
    '''
    try:
        api.me()
        return True
    except(TweepError):
        return False

def get_username(user_id):
    '''
    gets users username with Tweepy
    calls global api variable
    '''
    try:
        u = api.get_user(user_id)
        return u.name
    except(TweepError):
        logger.warning(TweepError)
        return user_id


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
        if not str(user_id) in user_lookup:
            logger.info("Getting username for {} and adding to the file".format(user_id))
            user_lookup[str(user_id)] = get_username(user_id)

    return user_lookup

def parse_args(args):
    currentdate = datetime.datetime.now().strftime("%Y-%m-%d_%H:%M")
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', '--log', dest='log', default=os.path.expanduser('~/pylogs/repair_pool'+currentdate+'.log'), help='This is the path where your output logging will go. This is a required parameter')
    return parser.parse_args(args)

def main():
    '''
    This is the main function that utilizes the functions above.
    '''

    args = parse_args(sys.argv[1:])
    logging.basicConfig(filename=args.log, level=logging.INFO)

    logger = logging.getLogger(__name__)
    logger.info('Todays Date: %s', datetime.datetime.now().strftime("%Y-%m-%d_%H:%M"))

    logger.info("Checking connection")
    if not check_connection():
        logger.warning("There was an authentication error")
        sys.exit("authentication error")


    # get the paths of all filter metadata files.
    files = glob.glob('/scratch/olympus/*/filters/*.json')

    # initalize a list of dictionaries for all the metadata.
    # then iterate through each metadate file.
    d_ = []

    logger.info("Reading the json file into a list")
    for f in files:
        # read the json file into a list.
        tweets = []
        for line in open(f, 'rb'):
            tweets.append(clean_dates(json.loads(line.decode('utf-8'))))

        # get metadata about size and quantity.
        d = [append_collection(t, f) for t in tweets \
             if t['filter_type'] in ['track', 'follow']]
        d_ += d

    logger.info('Putting the contents into a pandas dataframe')
    # put the contents into a pandas dataframe.
    df = pd.DataFrame(d_)
    df.sort_values(by='collection', inplace=True)

    user_ids = df[df["filter_type"] == "follow"]['value'].unique()

    logger.info("Updating user ids")
    user_lookup = update_user_ids(user_ids, logger)

    with open(user_lookup_path, 'w') as f:
        logger.info("Writing user lookup table to file")
        f.write(json.dumps(user_lookup))
        chown(user_lookup_path, group="smapp")

    logger.info("Replacing twitter user_ids with twitter usernames in table")
    df['value'].replace(user_lookup, inplace=True)

    # These are the columns we want!
    cols = ['collection'] + [c for c in df.columns if c not in cols_ignore]

    logger.info("Writing results to a csv")
    # filter out columns we don't want, and write the results to a csv.
    df[cols].to_csv(output_file, index=False)

    chown(output_file, group="smapp")

    logger.info("Copying the file into the archive")
    # copy the file into the archive.
    copyfile(output_file, archive_file)

    logger.info("Sending the files to Google Drive")
    # send the files to Google Drive.
    rclone(output_file, gdrive)
    rclone(archive_file, gdrive_archive)

    logger.info("Finished successfully!")

main()

