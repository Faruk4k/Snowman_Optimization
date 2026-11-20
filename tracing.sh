#!/bin/bash
#SBATCH --job-name=snowman_tracing
#SBATCH --partition=intelsr_devel
#SBATCH --nodes=1
#SBATCH --ntasks=16
#SBATCH --cpus-per-task=1
#SBATCH --time=00:30:00
#SBATCH --output=tracing%j.out
#SBATCH --error=error%j.txt

set -e

cd ~/Snowman

module purge
module load OpenMPI/4.1.6-GCC-13.2.0
module load Score-P/8.4-gompi-2024a-CUDA-12.6.0


make clean
make

export SCOREP_VERBOSE=True
export SCOREP_ENABLE_TRACING=True
export SCOREP_ENABLE_PROFILLING=False
export SCOREP_EXPERIMENT_DIRECTORY= tracing


mpirun  -n 16 ./snowman 1024 4
