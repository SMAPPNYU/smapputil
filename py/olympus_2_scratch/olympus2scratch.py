import os
import glob
from itertools import repeat
from shutil import copyfile
from subprocess import Popen, PIPE
from multiprocessing import Pool
from time import sleep
import optparse

from smappdragon.tools.tweet_cleaner import clean_tweets

parser = optparse.OptionParser()
parser.add_option('-c', '--collection',
    action="store", dest="collection_name",
    help="What olympus collection do you want?", default="")
parser.add_option('-n', '--n_jobs', type=int,
    action="store", dest="n_jobs",
    help="How many cores do you want", default=4)
options, args = parser.parse_args()
collection_name = options.collection_name
n_jobs = options.n_jobs

if not collection_name:
    raise("Specify which olympus collection you used to be moved, using the -c flag."
          "Avaialble collections can be viewed using `ls /scratch/olympus` on Prince.")

netid = os.environ.get('USER')
olympus_tweets = '/scratch/olympus/{}/data'.format(collection_name)
olympus_local = '/scratch/{}/olympus_local/'.format(netid)
collection_local = os.path.join(olympus_local, collection_name, 'json')
print("files will be stored here: {}".format(collection_local))

if not os.path.exists(olympus_tweets):
    print("the collection: {} does not exist".format(olympus_tweets))

if not os.path.exists(olympus_local):
    os.makedirs(olympus_local)
if not os.path.exists(collection_local):
    os.makedirs(collection_local)
    
def bunzip(f):
    '''
    Unzip a file!
    Uses the Process open (Popen) to access the commandline.
    '''
    process = Popen(['/usr/bin/bunzip2', f], 
                    stdout=PIPE, stderr=PIPE)

def clean_file(f):
    '''
    Cleans a tweet.
    JSON blobs that are corrupt will be written to a new file (dirty)
    '''
    clean = f + '.clean_temp'
    dirty = f + '.dirty'

    clean_tweets(f, clean, dirty)
    
    os.remove(f)
    os.rename(clean, f)
    
    if os.stat(dirty).st_size == 0:
        os.remove(dirty)

def bootstrap(f, collection_name):
    '''
    Get the local file path for compressed and uncompressed tweet.
    '''
    f_name = f.split('/')[-1]
    f_compressed = os.path.join(collection_name, f_name)
    f_uncompressed = f_compressed.replace('.bz2', '')
    
    return f_compressed, f_uncompressed

def copy_unzip_clean(f, collection_name):
    '''
    Bring together the four functions above.
    '''
    f_c, f_u = bootstrap(f, collection_name)

    if os.path.isfile(f_c):
        # if this is triggered, the file has already been processed.
        return
    copyfile(f, f_c)
    bunzip(f_c)
    while os.path.isfile(f_c):
        sleep(1)
    clean_file(f_u)

def main():
    '''
    Note that collection_name is the result of the -c flag, and
    n_jobs is the result of the -n flag.
    '''
    files = glob.glob(os.path.join(olympus_tweets, '*.bz2'))
    args = zip(files, repeat(collection_local))

    with Pool(n_jobs) as pool:
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

Last updated 2017-04-21
Author @yinleon
'''