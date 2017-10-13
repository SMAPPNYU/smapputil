#!/bin/bash

#SBATCH --job-name=filter_meta
#SBATCH --nodes=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=12GB
#SBATCH --time=30:00

module purge

/home/$USER/anaconda3/bin/python /home/$USER/smapprepos/smapputil/py/olympus_metadata/aggregate_filters.py