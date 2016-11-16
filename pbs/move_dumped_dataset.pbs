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
mv $1smapp_metadata.json $1metadata_pre.json
mv $1tweets_limits.json $1metadata_limits_pre.json
mv $1tweets_filter_criteria.json $1filters_pre.json
mv $1check_dump_integrity.log $1check_dump_integrity_pre.log
rename tweets $1_pre tweets_*.json $1tweets.json $1data.json

# compress
bzip2 $1*.json

# copy files to scratch
cp *.bz2 /scratch/olympus/$2/data/
cp $1check_dump_integrity_pre.log /scratch/olympus/$2/metadata/
cp $1metadata_limits_pre.json /scratch/olympus/$2/metadata/
cp $1metadata_pre.json /scratch/olympus/$2/metadata/
cp $1filters_pre.json /scratch/olympus/$2/filters/
echo "Done"

# https://wikis.nyu.edu/display/NYUHPC/Writing+and+submitting+a+job

