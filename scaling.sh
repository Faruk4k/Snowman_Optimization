#!/bin/bash
#SBATCH --job-name=snowman_scaling
#SBATCH --partition=intelsr_short
#SBATCH --nodes=1
#SBATCH --ntasks=96
#SBATCH --cpus-per-task=1
#SBATCH --exclusive
#SBATCH --time=03:00:00
#SBATCH --output=scaling_%j.out

set -e

cd ~/Snowman
mkdir -p logs/strong logs/weak logs/profiling

# =====================================
# PART 1: BUILD WITH OPENMPI 5.0.3
# =====================================

module purge
module load GCC/13.3.0 OpenMPI/5.0.3-GCC-13.3.0

make clean
make CXX=mpicxx

cp snowman snowman_scaling

# =====================================
# PART 2: STRONG SCALING
# =====================================

for p in 1 2 4 8 16 24 32 48 64 96; do
    echo "Strong scaling: $p processes"

    mpirun -np "$p" ./snowman_scaling 1024 4 \
        > "logs/strong/mpi_${p}.log" 2>&1
done

# =====================================
# PART 3: WEAK SCALING
# =====================================

for p in 1 2 4 8 16 24 32 48 64 96; do
    n=$(awk -v p="$p" 'BEGIN {printf "%.0f",128*sqrt(p)}')

    echo "Weak scaling: $p processes, ${n}x${n}"

    mpirun -np "$p" ./snowman_scaling "$n" 3 \
        > "logs/weak/mpi_${p}.log" 2>&1
done

# =====================================
# PART 4: SWITCH MPI ENVIRONMENT
# =====================================

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
