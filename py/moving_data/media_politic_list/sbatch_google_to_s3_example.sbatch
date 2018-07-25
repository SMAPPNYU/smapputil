#!/bin/bash

#SBATCH --job-name=media_politic_list
#SBATCH --nodes=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=10GB
#SBATCH --time=1:00:00

module purge

/home/$USER/anaconda3/bin/python /home/$USER/smapprepos/smapputil/py/moving_data/media_politic_list/google_to_s3.py
