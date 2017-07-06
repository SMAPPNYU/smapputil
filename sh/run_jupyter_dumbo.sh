module load python/gnu/2.7.11 
module load R/3.3.2 
module load java/1.8.0_72
module load spark/2.1.0

PORT=$(shuf -i 6000-9999 -n 1)

echo ssh -L $PORT:localhost:$PORT $USER@dumbo.es.its.nyu.edu
jupyter notebook --port=$PORT --no-browser

':
Run this in the Dumbo cluster to run a Jupyter notebook.
Rather than the sbatch command in the Prince cluster,
you can use the sh command to run this script.

It loads Python, R, and Spark, for their respective
kernel in Jupyter.

Author: Leon Yin
Last updated: 2017-07-05
'
