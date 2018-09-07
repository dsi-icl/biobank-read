#!/bin/bash

#PBS -l walltime=06:00:00
#PBS -l select=1:ncpus=4:mem=64gb
#PBS -q med-bio
#PBS -k oe
#PBS -N BBR


cp -r  /work/ds711/BBR/* $TMPDIR


module load anaconda3/personal
source activate py36

python test-BiobankRead-Bash-script.py

#cp *.csv $PBS_O_WORKDIR
