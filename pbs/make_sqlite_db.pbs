# makes an sqlite db for use with json1 extension

# job file for merging datasets

#!/bin/bash

#PBS -l nodes=1:ppn=1,walltime=100:00:00,mem=25gb
#PBS -N make_sqlite_db
#PBS -V
#PBS -S /bin/bash
#PBS -M ${LOGNAME}@nyu.edu
#PBS -m bae
#PBS -j oe
#PBS -o localhost:${HOME}/jobs/${PBS_JOBNAME}.${PBS_JOBID}.oe

echo "Running script..."

# make statging directories
mkdir /scratch/smapp/sqlite_staging/
mkdir /scratch/smapp/sqlite_staging/$1

# copy data to staging directories
cp -r /scratch/olympus/$1/data/ /scratch/smapp/sqlite_staging/$1/

# unzip all data in staging directory
bzip2 -d /scratch/smapp/sqlite_staging/$1/*.bz2
filepaths = /scratch/smapp/sqlite_staging/$1/*.json

for filepath in $filepaths
do
    while IFS='' read -r line || [[ -n "$line" ]];
    do
        sqlite testingjson.db "SELECT load_extension('/Users/yvanscher/smappwork/sqlite_testing/json1'); insert into testtable (id, json_field) values (1, json('{\"test\":\"dacmd\"}'));"
        sqlite testingjson.db "SELECT load_extension('json1'); insert into testtable (id, json_field) values (1, json('$line'));'"
        sqlite testingjson.db "select * from testtable;"
        echo "Text read from file: $line"
    done < "$1"
done

echo "Done"

# https://wikis.nyu.edu/display/NYUHPC/Writing+and+submitting+a+job
# http://www.glatter-gotz.com/blog/2011/02/19/looping-through-dates-in-a-bash-script-on-osx/
# https://mailliststock.wordpress.com/2007/03/01/sqlite-examples-with-bash-perl-and-python/