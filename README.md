# The Blind Spot Paradox Experiments

## 1. Environment and Dependencies (Prerequisites)

The experiments were executed on an AMD EPYC 8224P with 192 GB RAM under **Python 3.12**. To ensure bit-wise reproducibility, especially concerning the internal ADWIN clock artifact documented in the paper, we strictly pin the `river` library to version `0.23.0`. The interpreter version is part of the determinism contract: the RNG-overflow guards in the scripts assume Python 3.12 / NumPy 1.26 native `uint32` handling.

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
gunzip -k data/baf/*.gz
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
├── run_experiment_R2.sh                     
├── run_experiment_R3.sh
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
│   │   ├── exp_R1_generate_data.py
│   │   └── exp_R1_plot_figure.py
│   ├── R2_instrumented_blind_spot/
│   │   └── exp_R2_instrumented_blind_spot.py
│   ├── R3_regime_crossover/
│   │   └── exp_R3_regime_crossover.py
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
│   │   ├── data/                            
│   │   └── figures/
│   ├── R2_instrumented_blind_spot/
│   │   ├── data/                            
│   │   └── figures/
│   ├── R3_regime_crossover/
│   │   ├── data/                            
│   │   └── figures/
│   ├── R4_proteus_evaluation/
│   │   ├── data/                            
│   │   └── tables/
│   └── R5_real_world_evaluation/
│       ├── data/                            
│       └── tables/                        
└── logs/
    ├── R1_race_condition/
    ├── R2_instrumented_blind_spot/
    ├── R3_regime_crossover/
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
- **Data:** `results/R1_race_condition/data/R1_race_condition.parquet`
- **Diagnostic:** `results/R1_race_condition/data/R1_race_condition_diagnostic.md` (Tabular summary of the Blind Spot evolution).
- **Figure:** `results/R1_race_condition/figures/Fig_R1_race_condition.png` (Directly corresponds to **Figure 1** in the manuscript).

> 💡 **Reviewer Transparency Note regarding Figure 1 (Jitter Effect):**
> The generated figure perfectly reproduces the exact $\tau_{ARF}$ and $\tau_{det}$ stopping times reported in the submitted paper (green and red markers match bit-wise). However, you may notice a slight visual difference in the exact placement of the gray crosses ("Starved" / Censored runs at the far right) compared to the submitted PDF. 
> This is expected and strictly visual. In the original research script, these censored crosses were scattered using an unseeded random jitter to prevent overplotting. To comply with rigorous Artifact Evaluation standards, this repository explicitly seeds the jitter generator (one independent generator per $\lambda$ panel: `rng_jitter = np.random.default_rng(int(l) * 42)`) to guarantee a deterministic, bit-wise identical output PNG across all future runs. The underlying mathematical count of starved runs remains perfectly identical.

### Experiment R2: Instrumented Asymptotic Complexity & The Blind Spot (Figures 2A, 2B, 2C)
This experiment directly instruments the ARF's internal drift tracking versus the external CUSUM (PHT) across a continuous sweep of drift magnitudes ($\Delta e$). It isolates the Starvation Effect under high CUSUM thresholds ($\lambda=50$, Figure 2A), exposes the paradoxical failure increase at intermediate thresholds ($\lambda=25$, Figure 2B), and recovers the safe zone under a hyper-reactive threshold ($\lambda=8$, Figure 2C).

To reproduce the instrumented tracking and re-render the 3-panel figures:

```bash
chmod +x run_experiment_R2.sh
./run_experiment_R2.sh
```

**Expected Artifacts:**
- **Data:** `results/R2_instrumented_blind_spot/data/R2_instrumented_*.parquet`
- **Figures:** `results/R2_instrumented_blind_spot/figures/Fig_R2_A_PHT_ARF.png`, `Fig_R2_B_PHT_ARF.png`, and `Fig_R2_C_PHT_ARF.png` (Directly correspond to **Figures 2A, 2B, 2C** in the manuscript).

### Experiment R3: The Regime Crossover & Non-Adaptive RF (Figure 3)
This experiment deconstructs the paradox continuously across drift magnitudes ($\Delta e \in [0.02, 0.50]$) over Bernoulli streams. It reconciles the Blind Spot hypothesis with classical literature by mapping three regimes (Weak Signal, Safe Zone, Blind Spot). Crucially, it validates the architectural resolution proposed in the paper: deploying a Non-Adaptive Random Forest (static bagging of Hoeffding Trees) entirely eradicates the Starvation Effect on CUSUM monitors, though at an expected post-drift predictive cost.

To reproduce the crossover data and re-render the 3-panel figure:

```bash
chmod +x run_experiment_R3.sh
./run_experiment_R3.sh
```

**Expected Artifacts:**
- **Data:** `results/R3_regime_crossover/data/R3_regime_crossover_metrics.parquet`
- **Figure:** `results/R3_regime_crossover/figures/Fig_R3_Regime_Crossover.png` (Directly corresponds to **Figure 3** in the manuscript).

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

### Experiment R5: Real-World Evaluation on BAF & INSECTS (Table II)
This experiment validates the starvation/flooding dichotomy on six real-world streams. It contrasts a non-adaptive Hoeffding Tree (HT) against the Adaptive Random Forest (ARF), under both a CUSUM-family monitor (PageHinkley) and a windowed monitor (ADWIN), over 30 seeds per cell. The reoccurring stream is scored on its $K{=}2$ in-stream transitions: the two canonical positions lying beyond the stream length are phantom drifts, removed by the valid-window filter (consistent with the Table II caption).

To reproduce the full pipeline (integrity checks, BAF/INSECTS evaluation, adaptive $\Delta e$ estimation, flooding decomposition, and the final LaTeX table body), execute the orchestrator from the repository root:

```bash
chmod +x run_experiment_R5.sh
./run_experiment_R5.sh
```

The orchestrator pins `PYTHONHASHSEED=0`, and every cell pins its `random`/`numpy`/`river` seed through `numpy.random.SeedSequence(42)`, guaranteeing bit-wise reproducibility. The BAF stage is checkpointed and long-running (~4.5 h on the reference server); the INSECTS stage completes in minutes.

**Expected Artifacts:**
- **Table:** `results/R5_real_world_evaluation/tables/table2_real_data_summary.tex` (a complete, standalone `table*` environment for **Table II** with an auto-generated caption; this is a reference render parallel to the hand-maintained Table II in the manuscript — keep the two in sync rather than `\input`-ing this file alongside the manuscript copy).
- **Table Values:** `results/R5_real_world_evaluation/tables/table2_values.csv` (raw values, paired difference, and seed-level sign test).
- **Per-run metrics:** `baf_results.parquet`, `insects_results.parquet`, `insects_per_episode.parquet`, `delta_e.parquet`, `flooding_decomposition.parquet` in `results/R5_real_world_evaluation/data/`.
- **Manuscript mapping:** Table II (`tab:real_data_summary`) and the flooding analysis of Section IV-C (genuine detection vs false-alarm flooding) are derived directly from these artifacts.

## 5. Artifact Scope & Configuration Notes

**Pipelines covered by this repository:** Figure 1 (R1), Figures 2A–2C (R2), Figure 3 (R3), Table I and the KSWIN $\alpha$-sweep (R4), Table II and the flooding decomposition (R5).

**Manuscript results NOT regenerated here** (produced by exploratory instrumentation and reported in the paper for transparency): the single-tree HAT instrumentation ($M=1$) and the Hydra amplification factors ($4.1\times$–$8.0\times$, $K_{\mathrm{HAT}}\approx 102$); the clock-mismatch configuration matrix; the $\lambda_{\mathrm{op}}$ sweep illustrating the Decoupling Principle; the worked $M_{\mathrm{crit}}$ example.

**ARF detector configuration (intentional heterogeneity):** in R1, R2 and R5 the ARF pins both its internal `drift_detector` and `warning_detector` to `ADWIN(clock=c_int)`. In R3 and R4 only the `drift_detector` is pinned; the `warning_detector` keeps river's default (`ADWIN(clock=32)`). This matches exactly how the submitted manuscript artifacts were generated. Throughout the paper, $c_{\mathrm{int}}$ refers to the clock of the **drift** detector.
