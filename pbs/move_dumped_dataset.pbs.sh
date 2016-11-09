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

module purge
echo "Running script..."
# remove indexes
rm system.indexes.json

# rename files
mv smapp_metadata.json metadata_pre.json
mv tweets_limits.json metadata_limits_pre.json
mv tweets_filter_criteria.json filters_pre.json
mv check_dump_integrity.log check_dump_integrity_pre.log
rename .json _pre.json tweets_*.json tweets.json

# compress
bzip2 tweets_*.json

# copy files to scratch
cp *.bz2 /scratch/olympus/eric_garner_2016/data/
cp check_dump_integrity_pre.log /scratch/olympus/eric_garner_2016/metadata/
cp metadata_limits_pre.json /scratch/olympus/eric_garner_2016/metadata/
cp metadata_pre.json /scratch/olympus/eric_garner_2016/metadata/
cp filters_pre.json /scratch/olympus/eric_garner_2016/filters/
echo "Done"

# https://wikis.nyu.edu/display/NYUHPC/Writing+and+submitting+a+job