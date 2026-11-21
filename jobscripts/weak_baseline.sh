#!/bin/bash
#SBATCH --nodes=1
#SBATCH --partition=intelsr_short
#SBATCH --account=tmp_hpca_workshop
#SBATCH --ntasks=96
#SBATCH --cpus-per-task=1
#SBATCH --time=08:00:00
#SBATCH --job-name=weak_scaling_baseline
#SBATCH --exclusive
# first non-empty non-comment line ends SBATCH options 
unset SLURM_EXPORT_ENV
## Load modules
module load GCC/13.3.0 OpenMPI/5.0.3-GCC-13.3.0

## Build commands
make clean -C ..
make -C ..

## run commands

for i in {1..96}
do
	pixels=$(echo "128 * sqrt($i)" | bc -l | cut -d. -f1)
	mpirun -n $i ../snowman $pixels 3 > weak_baseline/ntasks_${i}_pixels_${pixels}.out 2>&1
	echo "Finished $i processes"
done

