#!/bin/bash

#SBATCH --job-name=olympus2scratch_test
#SBATCH --nodes=1
#SBATCH --cpus-per-task=12
#SBATCH --mem=16GB
#SBATCH --time=48:00:00

/home/$USER/anaconda3/bin/python /home/$USER/smapprepos/smapputil/py/olympus_2_scratch/olympus2scratch.py -c random_collection_4  -n 12

:'
Change the -c flag from us_geobox to the collection of interest.

All available collections are here:
ls /scratch/olympus

For info and prequisites for this sbatch script please read the docs here:
https://github.com/SMAPPNYU/smapputil#olympus2scratch_ex

Last updated 2017-05-30
Author @yinleon
'
