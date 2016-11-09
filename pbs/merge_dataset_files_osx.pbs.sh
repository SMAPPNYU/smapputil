# job file for merging datasets on a mac

#!/bin/bash

#PBS -l nodes=1:ppn=1,walltime=100:00:00,mem=25gb
#PBS -N merge_dataset_files
#PBS -V
#PBS -S /bin/bash
#PBS -M ${LOGNAME}@nyu.edu
#PBS -m bae
#PBS -j oe
#PBS -o localhost:${HOME}/jobs/${PBS_JOBNAME}.${PBS_JOBID}.oe

echo "Running script..."

# get all the dates specified in the range
startdate=$(date -j -f "%m_%d_%Y" $3 "+%s")
enddate=$(date -j -f "%m_%d_%Y" $4 "+%s")
offset=86400
dates=()

while [ "$startdate" -le "$enddate" ]
do
  date=$(date -j -f "%s" $startdate "+%m_%d_%Y")
  dates+=( "$date" )
  startdate=$(($startdate+$offset))
done

# find files with these dates
filepaths=()
for date in "${dates[@]}"
do
    filepaths+=($(find $1 -name *$date*.bz2))
done

# merge these files into one file, dont need to unzip
echo "${filepaths[@]}" | xargs cat > "$2"

echo "Done"

# https://wikis.nyu.edu/display/NYUHPC/Writing+and+submitting+a+job
# http://www.glatter-gotz.com/blog/2011/02/19/looping-through-dates-in-a-bash-script-on-osx/