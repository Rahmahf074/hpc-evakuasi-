#!/bin/bash
# Template batch job SLURM. TIDAK DIUJI di cluster nyata oleh penulis.
# Nama partition/module berbeda tiap pusat HPC - sesuaikan dokumentasi cluster tujuan.
#SBATCH --job-name=evakuasi-mc
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --time=00:30:00
#SBATCH --output=logs/%x-%j.out

mkdir -p logs
# module load python/3.x     # <- sesuaikan dengan cluster
# source .venv/bin/activate
python -m src.benchmark --workers 1 2 4 8 16 --replicates 10
