#!/bin/bash
#SBATCH --nodes=1
#SBATCH --partition=intelsr_short
#SBATCH --ntasks=96
#SBATCH --cpus-per-task=1
#SBATCH --time=08:00:00
#SBATCH --job-name=strong_scaling_optimized
#SBATCH --output=strong_optimized_%j.out
#SBATCH --error=strong_optimized_%j.err
#SBATCH --exclusive


# start
unset SLURM_EXPORT_ENV

## Load modules
module load GCC/13.3.0 OpenMPI/5.0.3-GCC-13.3.0

## Build commands
#Overriding CXX to plain mpicxx - the Makefile's default (scorep mpic++) adds.
make clean -C .. CXX=mpicxx
make -C .. CXX=mpicxx

mkdir -p strong_optimized

## run commands
# Tile size fixed at the program default; process count is 
# independent, swept over the same 1..96 grid as baseline/strong
# so the two can be plotted on the same x-axis. Master-worker needs size>=2,
# so we start at 2.
for i in {2..96}
do
	mpirun -n $i ../snowman 1024 4 32 > strong_optimized/ntasks_${i}.out 2>&1
	echo "Finished $i processes"
done
