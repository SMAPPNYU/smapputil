import os
import json
import glob
import math
import datetime

import pandas as pd

output_file = '/scratch/olympus/filter_metadata/filter.csv'

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
    
    # calculate the file sizes
    bytes_ = sum([os.stat(f_).st_size for f_ in files_in_f])
    bytes_human = convert_size(bytes_)
    num_files = len(files_in_f)
    avg_size = bytes_ / num_files
    avg_size_human = convert_size(avg_size)
    
    # gets the latest file and the date it was updated.
    newest = max(glob.iglob(regex), key=os.path.getctime)
    latest_filedate = datetime.datetime.fromtimestamp(
        os.path.getctime(newest)
    )
    
    return (bytes_, bytes_human, num_files, 
            avg_size, avg_size_human, latest_filedate)


def append_collection(t, f):
    '''
    Gets metadata about a filter.json file.
    '''
    t['collection'] = f.split('/')[3]
    t['collection_size_bytes'], t['collection_size'], t['num_files'], t['avg_file_bytes'], \
    t['avg_file_size'], t['latest_update'] = return_size(f)
    
    return t


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
            tweets.append(json.loads(line))

        # scrape the list, and collect info about the collection size, 
        # and when it was last updated.
        d = [append_collection(t, f) for t in tweets if t['filter_type'] == 'track']
        d_ += d

    # put the contents into a pandas dataframe.
    df = pd.DataFrame(d_)

    # filter out columns we don't want.
    df = df[[c for c in df.columns if c not in ['_id', 'filter_type', 'active', 'date_removed']]]
    
    # write the results to a csv.
    df.to_csv(output_file, index=False)

main()

'''
This script reads filters.json files from /scratch/
and returns a csv containing filter terms, and size metadata.

After downloading this file to your HPC home (I suggest just git clone smapputil)


```
#!/bin/bash

#SBATCH --job-name=filter_meta
#SBATCH --nodes=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=12GB
#SBATCH --time=30:00

module purge
module load python3/intel/3.5.3

/share/apps/python3/3.5.3/intel/bin/python3 /home/$USER/smapputil/py/olympus_metadata/aggregate_filters.py
```

Author Leon Yin
Last updated 2017-07-07
'''
