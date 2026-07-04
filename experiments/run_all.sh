#!/bin/bash
# Run full expanded experiment pipeline on RTX 3090
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

PYTHON="${PYTHON:-/data/workspace/venv/bin/python3}"
export HF_HOME="/data/workspace/huggingface_cache"
export TRANSFORMERS_CACHE="$HF_HOME"
export CUDA_VISIBLE_DEVICES=0

echo "=============================================="
echo " DriftSup BRI-MAIR Expanded Experiments"
echo " Server: $(hostname)"
echo " GPU: $(nvidia-smi --query-gpu=name --format=csv,noheader 2>/dev/null || echo N/A)"
echo " Python: $($PYTHON --version)"
echo " Workspace: /data/workspace/drift-suppression"
echo "=============================================="

mkdir -p /data/workspace/drift-suppression/{corpus,models,results,kg,logs,code}

$PYTHON step1_build_corpus.py 2>&1 | tee /data/workspace/drift-suppression/logs/step1.log
$PYTHON step2_build_queries.py 2>&1 | tee /data/workspace/drift-suppression/logs/step2.log
$PYTHON step3_encode_gpu.py    2>&1 | tee /data/workspace/drift-suppression/logs/step3.log
$PYTHON step4_train_driftsup.py 2>&1 | tee /data/workspace/drift-suppression/logs/step4.log
$PYTHON step5_run_experiments.py 2>&1 | tee /data/workspace/drift-suppression/logs/step5.log

echo "=============================================="
echo " All steps completed."
echo " Results: /data/workspace/drift-suppression/results/experiment_results.json"
echo "=============================================="