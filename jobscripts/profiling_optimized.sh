#!/bin/bash
#SBATCH --nodes=1
#SBATCH --partition=intelsr_devel
#SBATCH --ntasks=96
#SBATCH --cpus-per-task=1
#SBATCH --time=00:30:00
#SBATCH --job-name=snowman_profiling_optimized
#SBATCH --output=profiling_optimized_%j.out
#SBATCH --error=profiling_optimized_%j.err
#SBATCH --exclusive

# start
unset SLURM_EXPORT_ENV

## Load modules (older OpenMPI required for the LinaroForge module)
module purge
module load OpenMPI/4.1.6-GCC-13.2.0
module load LinaroForge/25.0.3-GCCcore-13.2.0-linux-x86_64

## Build commands
make clean -C .. CXX=mpicxx
make -C .. CXX=mpicxx

mkdir -p logs/profiling_optimized

## run commands
# in assignment 2 we set up 1/medium/full-node framing, but now we need to shift to atleast 2 processes
# at the low end since master worker requires size>=2 (1 master + 1 worker)
for p in 2 48 96; do
    echo "Profiling optimized build, $p processes"

    (
        cd logs/profiling_optimized

        perf-report mpirun -np "$p" \
            ../../../snowman 1024 4 32 \
            > "perf_${p}.log" 2>&1

        map --profile mpirun -np "$p" \
            ../../../snowman 1024 4 32 \
            > "map_${p}.log" 2>&1
    )
done

echo "All profiling experiments completed"
