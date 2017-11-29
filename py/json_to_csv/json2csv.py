import os
import glob
import json
from itertools import repeat, zip_longest
from subprocess import Popen, PIPE
from multiprocessing import Pool
import optparse
from time import sleep

import pandas as pd
from pysmap import SmappCollection


parser = optparse.OptionParser()
parser.add_option('-c', '--collection',
    action="store", dest="collection_name",
    help="What olympus collection do you want?", default="")
parser.add_option('-x', '--cols',
    action="store", dest="cols",
    help="columns space-delimited", default='text created_at id')
parser.add_option('-n', '--n_jobs', type=int,
    action="store", dest="n_jobs",
    help="How many cores do you want", default=4)
parser.add_option('-k', '--keep',
    action="store_true",  dest="keep",
    help="Do you want to keep the json files?", default=True)
parser.add_option('-s', '--split',
    action="store_true",  dest="split",
    help="Do you want to keep the json files?", default=False)

options, args = parser.parse_args()
collection_name = options.collection_name
cols = options.cols.split(',')
n_jobs = options.n_jobs
keep = options.keep
split = options.split

netid = os.environ.get('USER')
olympus_local = '/scratch/{}/olympus_local/'.format(netid)
collection_local = os.path.join(olympus_local, collection_name, 'json')
csv_out = os.path.join(olympus_local, collection_name, 'csv')

if not collection_name:
    raise("Select a collection name with the -c flag."
          "The collection needs to be in {}".format(olympus_local))

if not os.path.isdir(csv_out):
    os.makedirs(csv_out)

    
def grouper(iterable, n, fillvalue=None):
    '''
    Collect data into fixed-length chunks or blocks
    '''
    # grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx
    args = [iter(iterable)] * n
    return zip_longest(fillvalue=fillvalue, *args)


def split_json(f, chunksize = 120000, remove = True):
    '''
    Splits json into chunksize, and removes old file
    '''
    collection = SmappCollection('json', f)
    for i, group in enumerate(grouper(collection, chunksize)):
        f_out = f.replace('.json', '___pt{:03d}.json'.format(i))
        if os.path.isfile(f_out):
            os.remove(f_out)
        with open(f_out, 'w') as outputfile:
            json.dump(list(group), outputfile, ensure_ascii=False)
    if remove:  
        os.remove(f)
  
def split_csv(f, compression='gzip', chunksize = 120000, remove = True):
    '''
    Splits json into chunksize, and removes old file
    '''
    for i, df in enumerate(pd.read_csv(f, iterator=True, chunksize=chunksize)):
        f_out = f.replace('.csv', '___pt{:03d}.csv.gz'.format(i))
        print(f_out)
        df.to_csv(f_out, index=False, compression=compression)
  
    if remove:  
        os.remove(f)


def gzip(f):
    '''
    Unzip a file!
    Uses the Process open (Popen) to access the commandline.
    '''
    process = Popen(['/share/apps/pigz/2.3.4/intel/bin/pigz','--best', f], 
                    stdout=PIPE, stderr=PIPE)


def bootstrap(f):
    '''Json in to CSV out'''
    return f.replace(collection_local, csv_out).replace('.json', '.csv')


def json2csv(f, cols=cols, keep=True):
    '''
    Reads a json file into a SmappCollection.
    Dumps to csv.
    Removes incompletely dumped csv's from past jobs.
    gzips csv.
    '''
    f_out = bootstrap(f)
    if not os.path.isfile(f_out):
        collection = SmappCollection('json', f).dump_to_csv(f_out, cols)
    if not keep:
        os.remove(f)
    
    split_csv(f_out)


def main():
    
    #if split:
    #    with Pool(n_jobs) as pool:
    #        pool.map(split_json, files)

    files = glob.glob(collection_local + '/*.json')
    args = zip(files, repeat(cols), repeat(keep))

    with Pool(n_jobs) as pool:
        pool.starmap(json2csv, args)

if __name__ == "__main__":
    main()
    
