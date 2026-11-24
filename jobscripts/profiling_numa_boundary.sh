#!/bin/bash
#SBATCH --nodes=1
#SBATCH --partition=intelsr_devel
#SBATCH --ntasks=49
#SBATCH --cpus-per-task=1
#SBATCH --time=00:15:00
#SBATCH --job-name=snowman_profiling_numa
#SBATCH --output=profiling_numa_%j.out
#SBATCH --error=profiling_numa_%j.err
#SBATCH --exclusive
# first non-empty non-comment line ends SBATCH options
unset SLURM_EXPORT_ENV

## Load modules (older OpenMPI required for the LinaroForge module, same as profiling_optimized.sh)
module purge
module load OpenMPI/4.1.6-GCC-13.2.0
module load LinaroForge/25.0.3-GCCcore-13.2.0-linux-x86_64

## Build commands
make clean -C .. CXX=mpicxx
make -C .. CXX=mpicxx

mkdir -p logs/profiling_numa

## check node topology once, to confirm/refute the NUMA-boundary hypothesis
lscpu > logs/profiling_numa/lscpu.log
numactl --hardware > logs/profiling_numa/numactl.log 2>&1

## run commands
# 48 vs 49 processes, same node, same job -- isolates the step right at the
# suspected socket/NUMA boundary instead of comparing against the older,
# separately-run p=48 profiling data.
for p in 48 49; do
    echo "Profiling optimized build, $p processes"

    (
        cd logs/profiling_numa

        perf-report mpirun -np "$p" \
            ../../../snowman 1024 4 32 \
            > "perf_${p}.log" 2>&1

        map --profile mpirun -np "$p" \
            ../../../snowman 1024 4 32 \
            > "map_${p}.log" 2>&1
    )
done

echo "All NUMA-boundary profiling experiments completed"
