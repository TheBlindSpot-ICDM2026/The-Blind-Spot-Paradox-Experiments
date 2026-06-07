# The Blind Spot Paradox Experiments

## 1. Environment and Dependencies (Prerequisites)

The experiments were executed on an AMD EPYC 8224P with 192 GB RAM. To ensure bit-wise reproducibility, especially concerning the internal ADWIN clock artifact documented in the paper, we strictly pin the `river` library to version `0.23.0`.

```bash
# It is highly recommended to use a virtual environment
python -m venv blindspot_env
source blindspot_env/bin/activate  # On Windows use `blindspot_env\Scripts\activate`

# Install dependencies
pip install -r requirements.txt
```

## 2. Datasets & Data Preparation

To comply with anonymous repository size limits, some large datasets are provided in a compressed format. Before running the real-world evaluations, please decompress the Bank Account Fraud (BAF) dataset.

**Execute the following command from the repository root:**
```bash
gunzip data/baf/*.gz
```

### Data Sources
*   **Bank Account Fraud (BAF):** The `Base.csv`, `VariantI.csv`, and `VariantII.csv` files originate from the [NeurIPS 2022 Bank Account Fraud Dataset](https://www.kaggle.com/datasets/sgpjesus/bank-account-fraud-dataset-neurips-2022?resource=download).
*   **INSECTS Dataset:** The `abrupt_balanced.csv`, `gradual_balanced.csv`, and `incremental_reoccurring_balanced.csv` streams are sourced from the official [INSECTS repository](https://drive.google.com/drive/folders/1v-iRL6X4yWhKIn82-eS-w93wb-gxjSiz).

## 3. Repository Structure

```text
.
├── requirements.txt
├── README.md
├── run_experiment_R1.sh                     
├── run_experiment_R4.sh
├── run_experiment_R5.sh
├── data/
│   ├── baf/
│   │   ├── Base.csv.gz
│   │   ├── VariantI.csv.gz
│   │   └── VariantII.csv.gz
│   └── insects/
│       ├── abrupt_balanced.csv
│       ├── gradual_balanced.csv
│       └── incremental_reoccurring_balanced.csv
├── experiments/
│   ├── R1_race_condition/
│   ├── R4_proteus_evaluation/
│   │   ├── exp_R4_main_table.py
│   │   └── exp_R4_kswin_sweep.py
│   └── R5_real_world_evaluation/
│       ├── exp_R5_config.py
│       ├── exp_R5_common.py
│       ├── exp_R5_compute_baf.py
│       ├── exp_R5_compute_delta_e.py
│       ├── exp_R5_compute_insects.py
│       ├── exp_R5_make_table2.py
│       ├── exp_R5_preflight.py
│       └── exp_R5_smoke_test.py
├── results/
│   ├── R1_race_condition/
│   ├── R4_proteus_evaluation/
│   │   ├── data/                            
│   │   └── tables/
│   └── R5_real_world_evaluation/
│       ├── data/                            
│       └── tables/                        
└── logs/
    ├── R1_race_condition/
    ├── R4_proteus_evaluation/
    └── R5_real_world_evaluation/
```

## 4. Reproducing the Experiments

### Experiment R1: The Race Condition (Figure 1)
This experiment demonstrates the "Blind Spot" paradox by simulating the race condition between the internal Adaptive Random Forest (ARF) stopping time ($\tau_{ARF}$) and the external drift detector stopping time ($\tau_{det}$).

To reproduce the data generation and the final plot, simply run the orchestrator script from the root of the repository:

```bash
chmod +x run_experiment_R1.sh
./run_experiment_R1.sh
```

**Expected Artifacts:**
- **Data:** `results/R1_race_condition/data/R1_v7_protocol_diff.parquet`
- **Figure:** `results/R1_race_condition/figures/Fig_R1_v3_tau_arf_distribution.png` (Directly corresponds to **Figure 1** in the manuscript).

### Experiment R4: Heteroscedastic ARMA-GARCH Streams Evaluation (Table I & KSWIN Sweep)
This experiment validates the agnostic nature of the Starvation Effect across cumulative-evidence detectors (PHT, EDDM) against heteroscedastic ProteuS streams, and demonstrates the structural resolution provided by the distributional KSWIN monitor across an $\alpha$-sensitivity sweep.

To reproduce the full pipeline (data generation, metrics, significance tests, and LaTeX table compilation), execute the orchestrator:

```bash
chmod +x run_experiment_R4.sh
./run_experiment_R4.sh
```

**Expected Artifacts:**
- **Main Table:** `results/R4_proteus_evaluation/tables/exp_R4_table_I_III_merged.tex` (Directly corresponds to **Table I**).
- **KSWIN Sweep Table:** `results/R4_proteus_evaluation/tables/exp_R4_table_KSWIN_alpha_sweep.tex`
- **Significance Tests:** `exp_R4_seed_level_tests.csv` and `exp_R4_seed_level_tests_KSWIN_alpha_sweep.csv` in `results/R4_proteus_evaluation/data/`.
