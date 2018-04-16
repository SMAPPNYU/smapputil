import os
import logging
import glob
import datetime
from subprocess import Popen, PIPE
from shutil import chown


def bzip(f):
    '''
    Bzips a file.
    When this is successful, the original file will have disappeared.
    When that happens this returns the new file name with the .bz2 extension.
    '''
    f_out = f + '.bz2'
    
    if os.path.exists(f_out):
        os.remove(f_out)
        
    command = ['/share/apps/pbzip2/1.1.13/intel/bin/pbzip2','-v', '-f',  f]
    process = Popen(command, stdout=PIPE, bufsize=1)
    with process.stdout:
        for line in iter(process.stdout.readline, b''): 
            handle(line)
            print(line)
    returncode = process.wait() 
        
    return f_out, returncode

today = datetime.datetime.now()
user = os.environ.get('USER')
pattern = '/scratch/olympus/*/data/*.json'
uncompressed_files = glob.glob(pattern)
logfile = '/scratch/{}/job_logs/bzip2/{}_bzip.log'.format(user, today.strftime('%Y-%m-%d'))

logging.basicConfig(filename=logfile, level=logging.INFO)
logger = logging.getLogger(__name__)
logger.info("Got {} uncompressed files".format(len(uncompressed_files)))
for file in uncompressed_files:
    logger.info("Compressing {}".format(file))
    file_bz2, code = bzip(file) # hopefully :)
    logger.info("File compression complete with code {}".format(code))
    chown(file_bz2, group='smapp')
    os.chmod(file_bz2, mode=0o770)
