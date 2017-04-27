#!/bin/bash

#SBATCH --job-name=olympus2scratch_test
#SBATCH --nodes=1
#SBATCH --cpus-per-task=12
#SBATCH --mem=16GB
#SBATCH --time=6:00:00

/home/$USER/anaconda3/bin/python /home/$USER/smapputil/py/olympus_2_scratch/olympus2scratch.py -c nagler_unemployment_2_pre -n 12

:'
Read the docs:
https://github.com/SMAPPNYU/smapputil#olympus2scratch_ex

Change us_geobox for the collection you are interested in.

Last updated 2017-04-21
Author @yinleon
'
