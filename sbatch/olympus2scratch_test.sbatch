#!/bin/bash

#SBATCH --job-name=olympus2scratch_test
#SBATCH --nodes=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=8GB
#SBATCH --time=6:00:00

/home/$USER/anaconda3/bin/python /home/$USER/smapputil/py/olympus_2_scratch/olympus2scratch.py -c us_geobox -n 4

:'
This is an example of a slurm/sbatch script:
https://wikis.nyu.edu/display/NYUHPC/Slurm+Tutorial

Specifically, it's an sbatch implementation of olympus2scratch.py 
for the /scratch/olympus/us_geobox collection using 4 8GB memory CPUs.

See source for olympus2scratch:
https://github.com/SMAPPNYU/smapputil/blob/master/py/olympus_2_scratch/olympus2scratch.py

...and explanatory Jupyter notebook here:
http://nbviewer.jupyter.org/github/SMAPPNYU/smapputil/blob/master/nbs/olympus2scratch.ipynb

The script will copy, uncompress, and clean all tweets from the us_geobox
olympus collection on your local scratch space
/scratch/$USER/olympus_local/

This assumes you're using conda distributed Python.
You can get this using the following command in your HPC Prince home
```
cd /home/$USER

wget https://repo.continuum.io/archive/Anaconda3-4.3.1-Linux-x86_64.sh
bash Anaconda3-4.3.0-Linux-x86_64.sh
```

You're also going to need smappdragon, for the tweet cleaner
https://github.com/SMAPPNYU/smappdragon
```
pip install smappdragon
```

Last updated: 2017/04/20
Author @yinleon
'