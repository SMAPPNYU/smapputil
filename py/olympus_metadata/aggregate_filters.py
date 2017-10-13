import os
import json
import glob
import math
import datetime
import subprocess
from shutil import copyfile

import pandas as pd
today = datetime.datetime.now().strftime('%Y_%m_%d')
cols_ignore = ['_id', 'filter_type', 'active', 'date_removed']

root = '/scratch/olympus/filter_metadata/'
output_file = os.path.join(root, 'filter.csv')
archive_file = os.path.join(root, 'archive/filter_{}.csv'.format(today))

gdrive = ('gdrive:SMaPP_2017/SMAPP_ALL_LAB_MEMBERS/'
          'Documentation/Twitter_Collection_Terms/')                          
gdrive_archive = os.path.join(gdrive, 'z_Archive')


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
    Gets the size of tweet files in aggragate and individually.
    Also gets the latest file date.
    '''
    # creates a regular expression for tweet files.
    regex = f.replace('/filters/filters.json', '/data/*')
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
    
    row = dict(
        bytes_ = bytes_,
        bytes_human = bytes_human,
        num_file = num_files,
        avg_size = avg_size,
        avg_size_human = avg_size_human,
        latest_filedate = latest_filedate,
        latest_file = newest,
        latest_bytes = latest_bytes
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

def clean_dates(t):
    if isinstance(t['date_added'], dict):
        t['date_added'] = datetime.datetime.fromtimestamp(
                  t["date_added"]["$date"]/1000.0)
    elif t['date_added'] is None:
        t['date_added'] = datetime.datetime(1950, 1, 1)  
    elif not isinstance(t['date_added'], datetime.datetime):
        try:
            t['date_added'] = datetime.datetime.strptime(
                t["date_added"], "%a %b %d %H:%M:%S %z %Y")
        except:
            t['date_added'] = datetime.datetime.strptime(
                t["date_added"].split('T')[0], "%Y-%m-%d")                
        
    t['date_added'] = datetime.datetime.strftime(
            t['date_added'], '%Y-%m-%d')
    
    return t

def rclone(src, dest):
    '''
    Calls the rclone program from the commandline
    '''
    result = subprocess.Popen([
        '/share/apps/rclone/1.35/bin/rclone copy {} {}'.format(
            src, dest
        )
    ], shell=True)

    return result.communicate()

def main():
    '''
    This is the main function that utilizes the functions above.
    '''
    # get the paths of all filter metadata files.
    files = glob.glob('/scratch/olympus/*/filters/*.json')

    # initalize a list of dictionaries for all the metadata.
    # then iterate through each metadate file.
    d_ = []
    for f in files:
        # read the json file into a list.
        tweets = []
        for line in open(f, 'r'):
            tweets.append(clean_dates(json.loads(line)))
           
        # get metadata about size and quantity.
        d = [append_collection(t, f) for t in tweets \
             if t['filter_type'] == 'track']
        d_ += d

    # put the contents into a pandas dataframe.
    df = pd.DataFrame(d_)

    # filter out columns we don't want.
    df = df[[c for c in df.columns if c not in cols_ignore]]
    
    # write the results to a csv.
    df.to_csv(output_file, index=False)
    copyfile(output_file, archive_file)
   
    rclone(output_file, gdrive)
    rclone(archive_file, gdrive_archive)
    
main()
