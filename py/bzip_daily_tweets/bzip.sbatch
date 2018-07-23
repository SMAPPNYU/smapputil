#!/bin/bash

#SBATCH --job-name=bzip
#SBATCH --nodes=1
#SBATCH --cpus-per-task=2
#SBATCH --mem=50GB
#SBATCH --time=100:00:00

module purge
/home/nhb228/anaconda3/bin/python /home/nhb228/smapprepos/smapputil/py/bzip_daily_tweets/bzip_all.py
