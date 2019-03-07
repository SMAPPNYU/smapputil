#!/bin/bash

#SBATCH --job-name=weekly_collection_charts
#SBATCH --nodes=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=32GB
#SBATCH --time=05:30:00

module purge

/home/$USER/miniconda3/bin/python /home/$USER/smapprepos/smapputil/py/olympus_metadata/daily_collection_charts/weekly_collection_charts.py --log /home/$USER/smapprepos/smapputil/py/olympus_metadata/daily_collection_charts/logging/todays_collection_charts.log
