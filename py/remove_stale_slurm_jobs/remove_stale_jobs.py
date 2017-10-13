import os
import glob
from subprocess import Popen, PIPE

import pandas as pd

USER = os.environ.get("USER")

proc = Popen('/opt/slurm/bin/squeue -u $USER', shell=True, stdout=PIPE)
out = [_ for _ in proc.stdout]

# Parse the stdout, to give it structure.
columns = out[0].decode().split()
data = [_.decode().replace('\n', '').split() for _ in out[1:]]

# read the structured data into a pandas dataframe
df = pd.DataFrame(data, columns=columns)

# get the running jobs and the slurm files
running_jobs = df[df.ST == 'R']['JOBID'].tolist()
slurm_files = glob.glob('/home/{}/slurm-*'.format(USER))

# The stale jobs are the slurm files that aren't active.
stale_jobs = [_ for _ in slurm_files if not any(job in _ for job in running_jobs)]

if stale_jobs:
    for job in stale_jobs:
        os.remove(job)
