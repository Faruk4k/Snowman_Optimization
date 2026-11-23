#!/bin/bash
#SBATCH --nodes=1
#SBATCH --partition=intelsr_devel
#SBATCH --ntasks=4
#SBATCH --cpus-per-task=1
#SBATCH --time=00:10:00
#SBATCH --job-name=test_snowflakes
#SBATCH --output=test_snowflakes_%j.out
#SBATCH --error=test_snowflakes_%j.err
#SBATCH --exclusive

# start
unset SLURM_EXPORT_ENV

## Load modules
module load GCC/13.3.0 OpenMPI/5.0.3-GCC-13.3.0

## Build commands
make clean -C .. CXX=mpicxx
make -C .. CXX=mpicxx

## run commands
mpirun -n 4 ../snowman 256 3 32
