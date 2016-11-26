'''
This is a simplified version of Jo's launch_n_jobs script for anaconda.
Usage:
anaconda/bin/python simple_launch_n_jobs.py -i inputfile_*.bson -c 'anaconda/bin/python myscript.py -a arg1 -b arg2'
It then launches multiple jobs from the PBS template below, where each job will run the command
    python myscript.py -a arg1 -b arg2 -i INPUTFILE_x
Note:
1. '-a' and '-b' are arguments to your myscript.py they are totally optional and depend on the
script you are running on each inputfile.
2. 'anaconda/bin/python' is the python binary that comes with anaconda, make sure you use This
and not simply 'python.'
'''

import os
import base64
import argparse
import subprocess

PBS_TEMPLATE='''
#!/bin/bash
#PBS -l nodes=1:ppn=1,walltime={hours}:00:00,mem=16gb
#PBS -N smapp_job
#PBS -V
#PBS -S /bin/bash
#PBS -M ${{LOGNAME}}@nyu.edu
#PBS -m n
#PBS -j oe
#PBS -o localhost:${{HOME}}/jobs/${{PBS_JOBNAME}}.${{PBS_JOBID}}.oe
echo 'Processing data...'
time {command}
echo 'Done!'
'''
def launch_job(command, inputfile, hours):
    #store the command to put inside the template
    file_command = '{command} -i {inputfile}'.format(command=command, inputfile=inputfile)

    #create a randomized string in base64 with a .pbs extension
    tempfilename = base64.b64encode(command + inputfile, 'ab')[:10]+'.pbs'
    #create/open a file with the write option, store its file handle, write to the file
    tempfile = open(tempfilename, 'w')
    tempfile.write(PBS_TEMPLATE.format(command=file_command,hours=hours))
    tempfile.close()

    #run the script by running qsub with the pbs file we just created
    qsub_cmd = 'qsub -V {jobscript}'.format(jobscript=tempfile.name)
    #the subprocess module pauses the execution of the script and waits for the output from stdout
    output = subprocess.check_output(qsub_cmd, shell=True)
    #delete the .pbs file we just made to keep stuff clean.
    os.remove(tempfile.name)
    return output.strip(), file_command


if __name__ == '__main__':
    #create a parser for arguments, add some arguments, parse arguments stored in argv
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input_files', nargs='+', help='list of different input files (one per job to be launced).')
    parser.add_argument('-c', '--command', required=True, help='Command to be injected into .pbs file. Each of the N runs will get a \'-i INPUTFILE_x\' appended to it.')
    parser.add_argument('-w', '--hours', type=int, default=1)
    args = parser.parse_args()

    #create an empty list
    jobnumbers = list()
    for inputfile in args.input_files:
        job_number, file_command = launch_job(args.command, inputfile, args.hours)
        jobnumbers.append(job_number)
        print('{jobnumber}: {filecommand} (walltime: {hours})').format(jobnumber=job_number, filecommand=file_command, hours=args.hours)

'''
author @yvan @jonathanronen
'''