import os
import sys
import glob
from itertools import repeat
from shutil import copyfile
from subprocess import Popen, PIPE
from multiprocessing import Pool
from time import sleep
import argparse

from smappdragon.tools.tweet_cleaner import clean_tweets

    
def parse_args():
    '''
    Parse argument flags included when executing this here script.
    collection_name (-c) needs to be the name of a colleciton in 
    /scratch/olympus

    n_jobs are the number of CPU jobs you want this job to run on.
    Make sure that it is the same as the number of CPUS you request
    When issuing the sbatch job.
    '''
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--collection',
        action="store", dest="collection_name", required=True,
        help="What olympus collection do you want?")
    parser.add_argument('-n', '--n_jobs', type=int,
        action="store", dest="n_jobs",
        help="How many cores do you want", default=4)
   
    return vars(parser.parse_args())


def get_global_context(args):
    '''
    Sets variables that will be used throughout this script.
    In lieu of globals.

    Args is a dict returned from parse_args().
    '''
    collection_name = args['collection_name']
    netid = os.environ.get('USER')

    olympus_tweets = '/scratch/olympus/{}/data'.format(collection_name)
    olympus_local = '/scratch/{}/olympus_local/'.format(netid)

    collection_local = os.path.join(olympus_local, collection_name, 'json')
    collection_dirty = os.path.join(olympus_local, collection_name, 'json_dirty')
    
    print("files will be stored here: {}".format(collection_local))

    if not os.path.exists(olympus_tweets):
        print("the collection: {} does not exist".format(olympus_tweets))
        sys.exit()

    # make the local olympus, if first time. 
    # also directories for clean and dirty collection
    if not os.path.exists(olympus_local):
        os.makedirs(olympus_loca, exist_ok=True)
    if not os.path.exists(collection_local):
        os.makedirs(collection_local, exist_ok=True)
    if not os.path.exists(collection_dirty):
        os.makedirs(collection_dirty, exist_ok=True)

    context_ = {
        'olympus_tweets': olympus_tweets,
        'olympus_local': olympus_local,
        'collection_local': collection_local,
        'collection_dirty': collection_dirty
    }

    # concat the two dicts
    context = {**args, **context_}

    return context

def get_context(f, global_context):
    '''
    Get the local file path for compressed, uncompressed tweet,
    and dirty uncompressed tweet.
    '''

    f_name = f.split('/')[-1]
    f_name_u = f_name.replace('.bz2', '')

    f_compressed = os.path.join(global_context['collection_local'], f_name)
    f_uncompressed = os.path.join(global_context['collection_local'], f_name_u)
    f_dirty = os.path.join(global_context['collection_dirty'], f_name_u)

    context = {
        'f': f,
        'f_compressed': f_compressed,
        'f_uncompressed': f_uncompressed,
        'f_dirty': f_dirty
    }

    return context


def bunzip(f):
    '''
    Unzip a file!
    Uses the Process open (Popen) to access the commandline.
    '''
    process = Popen(['/usr/bin/bunzip2', f], 
                    stdout=PIPE, stderr=PIPE)


def clean_file(context):
    '''
    Cleans a tweet.
    JSON blobs that are corrupt will be written to a new file (dirty)
    '''
    f = context['f_uncompressed']
    clean = context['f_uncompressed'] + '.clean_temp'
    dirty = context['f_dirty']

    clean_tweets(f, clean, dirty)
    
    os.remove(f)
    os.rename(clean, f)
    
    if os.stat(dirty).st_size == 0:
        os.remove(dirty)


def copy_unzip_clean(f, context_global):
    '''
    Bring together the four functions above.
    '''
    context = get_context(f, context_global)
    f_u = context['f_uncompressed']
    f_c = context['f_compressed']

    if os.path.isfile(f_u):
        # if this is triggered, the file has already been processed.
        return
    copyfile(f, f_c)
    bunzip(f_c)
    while os.path.isfile(f_c):
        sleep(1)
    clean_file(context)


def main():
    '''
    Note that collection_name is the result of the -c flag, and
    n_jobs is the result of the -n flag.
    '''
    input_args = parse_args()
    context_global = get_global_context(input_args)

    olympus_path = context_global['olympus_tweets']
    files = glob.glob(os.path.join(olympus_path, '*.bz2'))
    args = zip(files, repeat(context_global))

    with Pool(context_global['n_jobs']) as pool:
        '''
        This is the parallelized version of the following:

        for f in files:
            copy_unzip_clean(f, collection_local)

        Pool(8), means we're using 8 cpus!

        pool.starmap() allows us to apply the a function to all 8 CPUs in the Pool 
        using all the inputs from args.

        starmap allows us to use a function with two or more inputs, in this case
        the inputs are the name of the olympus file, and the destination of those files.
        '''
        pool.starmap(copy_unzip_clean, args)

if __name__ == "__main__":
    main()
    
'''
Use this script to transport, uncompress them, and clean a collection 
from /scratch/olympus to your /scratch/$USER space.

Specify the collection, use the -c flag, and the number of cores you requested
using the -n flag.

EX:
python olympus2scratch.py -c womens_march_2017 -n 8

Yields the Women's March collection using 8 CPUs.

This script originates from a Jupyter Notebook:
https://github.com/SMAPPNYU/smapputil/blob/master/nbs/olympus2scratch.ipynb

And can be implented in SLURM using this test script:
https://github.com/SMAPPNYU/smapputil/blob/master/sbatch/olympus2scratch_ex.sbatch

There you will find better documentation!

Last updated 2017-11-09
Author @yinleon
'''
