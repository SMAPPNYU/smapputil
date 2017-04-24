#!/bin/bash

srun -n$1 -t$2:00:00 --mem=$3 --pty /bin/bash