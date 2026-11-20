#!/bin/bash
#SBATCH --job-name=snowman_scaling
#SBATCH --partition=intelsr_devel
#SBATCH --nodes=1
#SBATCH --ntasks=96
#SBATCH --cpus-per-task=1
#SBATCH --exclusive
#SBATCH --time=00:30:00
#SBATCH --output=scaling_%j.out

set -e

cd ~/Snowman

module purge
module load OpenMPI/4.1.6-GCC-13.2.0
module load LinaroForge/25.0.3-GCCcore-13.2.0-linux-x86_64

make clean
make CXX=mpicxx

cp snowman snowman_profiling

# =====================================
# PART 5: LINARO FORGE PROFILING
# =====================================

for p in 1 48 96; do
    echo "Profiling $p processes"

    (
        cd logs/profiling

        perf-report mpirun -np "$p" \
            ../../snowman_profiling 1024 4 \
            > "perf_${p}.log" 2>&1

        map --profile mpirun -np "$p" \
            ../../snowman_profiling 1024 4 \
            > "map_${p}.log" 2>&1
    )
done

echo "All experiments completed"
