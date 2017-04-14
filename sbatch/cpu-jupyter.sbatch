#!/bin/bash

#SBATCH --job-name=jupyterCPU
#SBATCH --nodes=1
#SBATCH --cpus-per-task=2
#SBATCH --mem=16GB
#SBATCH --time=12:00:00

:'This is a variation of the instructions offered by HPC 
see: https://wikis.nyu.edu/display/NYUHPC/Running+Jupyter+on+Prince
located here: /share/apps/examples/jupyter/run-jupyter.sbatch

Be advised!
Make sure SSH-authentication is enabled on Prince see: 
https://wikis.nyu.edu/display/NYUHPC/Configuring+SSH+Key-Based+Authentication

This implementation also assumes you use your own distro of Python (and Jupyter) via Anaconda.
To download Anaconda (https://www.continuum.io/downloads), 
you can the run the following in your Prince home:
```
wget https://repo.continuum.io/archive/Anaconda3-4.3.1-Linux-x86_64.sh
bash Anaconda3-4.3.0-Linux-x86_64.sh
```

Troubleshooting:
- If a session quits, you may need to increase the allocated memory (--mem).
- If you parallelize tasks you will need to increase the --cpus-per-task.

Last updated: 2017-04-14
'

module purge

jupyter_dir=/home/$USER/
cd $jupyter_dir

port=$(shuf -i 6000-9999 -n 1)

/usr/bin/ssh -N -f -R $port:localhost:$port log-0
/usr/bin/ssh -N -f -R $port:localhost:$port log-1

cat<<EOF

Jupyter server is running on: $(hostname)
Job starts at: $(date)

Step 1 :

If you are working in NYU campus, please open an iTerm window, run command

ssh -L $port:localhost:$port $USER@prince.hpc.nyu.edu

If you are working off campus, you should already have ssh tunneling setup through HPC bastion host, 
that you can directly login to prince with command

ssh $USER@prince

Please open an iTerm window, run command

ssh -L $port:localhost:$port $USER@prince

Step 2:

Keep the iTerm windows in the previouse step open. Now open browser, find the line with

The Jupyter Notebook is running at:

the URL is something: http://localhost:${jupyter_port}/?token=XXXXXXXX

you should be able to connect to jupyter notebook running remotly on prince compute node with above url

EOF

unset XDG_RUNTIME_DIR
if [ "$SLURM_JOBTMP" != "" ]; then
    export XDG_RUNTIME_DIR=$SLURM_JOBTMP
fi

/home/$USER/anaconda3/bin/jupyter notebook --no-browser --port $port
