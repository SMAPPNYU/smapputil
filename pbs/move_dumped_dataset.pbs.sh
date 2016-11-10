# moves old data set to appropriate pre files

#!/bin/bash

#PBS -l nodes=1:ppn=1,walltime=100:00:00,mem=25gb
#PBS -N move_dumped_dataset
#PBS -V
#PBS -S /bin/bash
#PBS -M ${LOGNAME}@nyu.edu
#PBS -m bae
#PBS -j oe
#PBS -o localhost:${HOME}/jobs/${PBS_JOBNAME}.${PBS_JOBID}.oe

echo "Running script..."
# remove indexes
rm system.indexes.json

# rename files
cp smapp_metadata.json metadata_pre.json
cp tweets_limits.json metadata_limits_pre.json
cp tweets_filter_criteria.json filters_pre.json
cp check_dump_integrity.log check_dump_integrity_pre.log
rename tweets $1_pre tweets_*.json tweets.json data.json

# compress
bzip2 $1*.json

# copy files to scratch
cp *.bz2 /scratch/olympus/$1/data/
cp check_dump_integrity_pre.log /scratch/olympus/$1/metadata/
cp metadata_limits_pre.json /scratch/olympus/$1/metadata/
cp metadata_pre.json /scratch/olympus/$1/metadata/
cp filters_pre.json /scratch/olympus/$1/filters/
echo "Done"

# https://wikis.nyu.edu/display/NYUHPC/Writing+and+submitting+a+job

