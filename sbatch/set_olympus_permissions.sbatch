#!/bin/bash

#SBATCH --nodes=1
#SBATCH --tasks-per-node=1
#SBATCH --time=100:00:00
#SBATCH --mem=5GB
#SBATCH --job-name=set_olympus_permissions
#SBATCH --mail-type=END
#SBATCH --mail-user=yns207@nyu.edu
#SBATCH --output=/scratch/yns207/job_logs/set_olympus_permissions_%j.out
#SBATCH --error=/scratch/yns207/job_logs/set_olympus_permissions_%j.err
#SBATCH --get-user-env

# set all files already in olympus
# to have the smapp group
chown -R $USER:smapp /scratch/olympus

# make is so that all new files created in 
# olympus in the future have the smapp group
chmod g+s /scratch/olympus

# update the permissions to rwxr-x--- for all files and folders
# inside olympus recursively, this is rwx for user and r-x for
# the group which should be smapp
find /scratch/olympus -type d -exec chmod -R 750 {} \;
find /scratch/olympus -type f -exec chmod -R  750 {} \;

# author @yvan 01-05-2017
# this script sets the permissions on olympus and just makes sure they stay the way we want them
# find docs at https://github.com/SMAPPNYU/smapputil#set_olympus_permissions