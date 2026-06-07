#!/bin/bash
set -e
set -o pipefail

echo "============================================================"
echo " Starting Experiment R4: ProteuS Heteroscedastic Evaluation "
echo "============================================================"

# Ensure directories exist
LOG_DIR="logs/R4_proteus_evaluation"
mkdir -p "$LOG_DIR"

# Ensure dependencies are available
if ! command -v python &> /dev/null; then
    echo "Error: Python is not available in the current path. Please activate your environment."
    exit 1
fi

echo ">>> Running Main Table Generation (PHT, EDDM, ADWIN, SRP, KSWIN)..."
python experiments/R4_proteus_evaluation/exp_R4_main_table.py 2>&1 | tee "$LOG_DIR/exp_R4_main_table.log"

echo ">>> Running KSWIN Alpha Sweep..."
python experiments/R4_proteus_evaluation/exp_R4_kswin_sweep.py 2>&1 | tee "$LOG_DIR/exp_R4_kswin_sweep.log"

echo "============================================================"
echo " Experiment R4 completed successfully!"
echo " Results -> results/R4_proteus_evaluation/"
echo " Logs    -> $LOG_DIR/"
echo "============================================================"