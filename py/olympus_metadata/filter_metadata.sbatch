#!/bin/bash

#SBATCH --job-name=filter_meta
#SBATCH --nodes=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=24GB
#SBATCH --time=50:00:00

module purge
module load rclone/1.35

/home/$USER/anaconda3/bin/python /home/$USER/smapprepos/smapputil/py/olympus_metadata/aggregate_filters.py
