#!/bin/bash
#SBATCH --nodes=1
#SBATCH --partition=intelsr_short
#SBATCH --ntasks=96
#SBATCH --cpus-per-task=1
#SBATCH --time=02:00:00
#SBATCH --job-name=tile_size_sweep
#SBATCH --output=tile_size_sweep_%j.out
#SBATCH --error=tile_size_sweep_%j.err
#SBATCH --exclusive
# start
unset SLURM_EXPORT_ENV

## Load modules
module load GCC/13.3.0 OpenMPI/5.0.3-GCC-13.3.0

## Build commands
make clean -C .. CXX=mpicxx
make -C .. CXX=mpicxx

mkdir -p tile_sweep

## run commands
# Full node (96), tile_size changes and at 1024 as only 1 tile(worst case) 
# only one worker ever gets work) to show the load-balancing tradeoff.
for tile in 8 16 32 64 128 256 512 1024
do
	mpirun -n 96 ../snowman 1024 4 $tile > tile_sweep/tilesize_${tile}.out 2>&1
	echo "Finished tile_size=$tile"
done
