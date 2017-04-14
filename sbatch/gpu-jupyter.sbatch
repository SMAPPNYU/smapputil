#!/bin/bash

#SBATCH --job-name=jupyterGPU
#SBATCH --nodes=1
#SBATCH --cpus-per-task=2
#SBATCH --mem=64GB
#SBATCH --time=12:00:00
#SBATCH --gres=gpu:1

:'
================================
Only use this is you NEED A GPU!
================================

If you are using Theano, please alter/create the .theanorc file as follows:
```
[global]
device = gpu
floatx = float32

[lib]
cnmem=.5
```

If you are using Keras, there are currently buffering issues when fitting a model. 
The current solution is to set the verbose argument for model.fit() to 2

Also note Keras default backend is Tensorflow.
You will need to change ~/.keras/keras.json

Last updated: 2017-04-17
'
module purge
module load cuda
module load cudnn

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
