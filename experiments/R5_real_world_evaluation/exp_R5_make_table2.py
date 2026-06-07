# exp_R5_make_table2.py
"""Assemble Table II (real-world validation) from the pipeline artifacts. Outputs:
  - flooding_decomposition.parquet  (genuine detection vs false-alarm flooding),
  - table2_values.csv               (raw values + paired difference + sign test),
  - table2_real_data_summary.tex    (the tabular BODY only; the caption and the
    \\begin{table*} wrapper stay in the manuscript, per arbitrage G2).
Significance is the seed-level paired sign test (unit of independence = seed)."""
import sys
import numpy as np
import pandas as pd
from scipy.stats import binomtest

import exp_R5_config as cfg

# (dataset, variant_key, LaTeX row label) in manuscript order.
ROW_ORDER = [
    ("baf", "Base",      "BAF Base"),
    ("baf", "VariantI",  "BAF Variant I"),
    ("baf", "VariantII", "BAF Variant II"),
    ("insects", "abrupt_balanced",                  r"INSECTS abrupt\_balanced"),
    ("insects", "gradual_balanced",                 r"INSECTS gradual\_balanced"),
    ("insects", "incremental_reoccurring_balanced", r"INSECTS reoccurring\_balanced"),
]


def p_chance(n_fp, tau, ntot):
    """Probability of matching a drift by chance given n_fp false alarms."""
    return 1.0 - (1.0 - tau / ntot) ** n_fp


def flooding_table(ep):
    """Per-(variant, pipeline) flooding decomposition from the per-episode records."""
    run = ep.groupby(["variant", "pipeline", "seed"]).first().reset_index()
    g = run.groupby(["variant", "pipeline"]).agg(
        recall=("run_recall", "mean"), precision=("run_precision", "mean"),
        n_alarms=("n_detections_total", "mean"), n_fp=("run_n_fp", "mean"),
        tau_tol=("tau_tol", "mean"), n_total=("n_total", "mean")).reset_index()
    g["recall_chance"] = p_chance(g["n_fp"], g["tau_tol"], g["n_total"])
    g["detection_genuine"] = g["recall"] > g["recall_chance"] + cfg.FLOODING_GENUINE_MARGIN
    return g.round(4)


def sci(p):
    """Format a p-value as $m \\cdot 10^{e}$ with a one-significant-figure mantissa."""
    if p is None or not np.isfinite(p):
        return "---"
    e = int(np.floor(np.log10(p)))
    m = int(round(p / 10.0 ** e))
    if m >= 10:
        m, e = 1, e + 1
    return rf"${m} \cdot 10^{{{e}}}$"


def bold(s):
    return rf"$\mathbf{{{s}}}$"


def main():
    de  = pd.read_parquet(cfg.OUT_DELTA_E)
    baf = pd.read_parquet(cfg.OUT_BAF)
    ins = pd.read_parquet(cfg.OUT_INSECTS)
    ep  = pd.read_parquet(cfg.OUT_EPISODE)

    flood = flooding_table(ep)
    flood.to_parquet(cfg.OUT_FLOODING, index=False)

    def f1_mean(df, v, pipeline):
        m = (df["variant"] == v) & (df["pipeline"] == pipeline)
        return float(df.loc[m, cfg.F1_COL].mean()) if m.any() else np.nan

    def f1_seed_vector(df, v, pipeline):
        sub = df[(df["variant"] == v) & (df["pipeline"] == pipeline)]
        return sub.sort_values("seed")[cfg.F1_COL].values

    def delta_row(dataset, v):
        r = de[(de["dataset"] == dataset) & (de["variant"] == v)]
        if r.empty:
            return np.nan, []
        return float(r["delta_e_mean"].values[0]), list(np.asarray(r["delta_e_per_drift"].values[0]))

    rows_csv, tex_lines = [], []
    for dataset, v, label in ROW_ORDER:
        src = baf if dataset == "baf" else ins
        f1_ht, f1_arf = f1_mean(src, v, "pht_ht"), f1_mean(src, v, "pht_arf_c1")
        f1_adw = f1_mean(src, v, "adwin_arf_c1")
        de_mean, de_parts = delta_row(dataset, v)

        ratio = f1_ht / f1_arf if (f1_arf is not None and f1_arf > 1e-9) else np.inf

        # Seed-level paired sign test (INSECTS only)
        if dataset == "insects":
            ht_v, arf_v = f1_seed_vector(ins, v, "pht_ht"), f1_seed_vector(ins, v, "pht_arf_c1")
            wins, loss = int((ht_v > arf_v).sum()), int((arf_v > ht_v).sum())
            n = wins + loss
            p = binomtest(max(wins, loss), n, 0.5, alternative="two-sided").pvalue if n > 0 else None
        else:
            p, wins, loss = None, None, None

        # --- Presentation layer (data-driven; reproduces the submitted Table II) ---
        if dataset == "baf" and abs(de_mean) < 0.01:
            de_txt = r"$\approx 0$"
        else:
            star = (len(de_parts) > 0 and min(de_parts) < 0 and de_mean < 0.20)  # weak witness
            base = f"{de_mean:.2f}" + (r"^{\ast}" if star else "")
            de_txt = bold(base) if de_mean >= 0.40 else f"${base}$"
        ht_txt, arf_txt = f"${f1_ht:.2f}$", f"${f1_arf:.2f}$"
        adw_max = (f1_adw >= 0.20 and f1_adw > f1_ht and f1_adw > f1_arf)  # ARF safe-zone win
        adw_txt = bold(f"{f1_adw:.2f}") if adw_max else f"${f1_adw:.2f}$"
        if not np.isfinite(ratio):
            ratio_cell = "---"
        else:
            ratio_cell = bold(f"{ratio:.2f}") if ratio > 1.5 else f"${ratio:.2f}$"
        p_txt = sci(p)

        tex_lines.append(f"      {label:<29} & {de_txt} & {ht_txt} & {arf_txt} "
                         f"& {adw_txt} & {ratio_cell} & {p_txt} \\\\")
        rows_csv.append({
            "row": label, "dataset": dataset, "variant": v,
            "delta_e": round(de_mean, 4), "F1_PHT_HT": round(f1_ht, 4),
            "F1_PHT_ARF": round(f1_arf, 4), "F1_ADW_ARF": round(f1_adw, 4),
            "ratio": round(ratio, 4) if np.isfinite(ratio) else np.inf,
            "diff_HT_minus_ARF": round(f1_ht - f1_arf, 4),
            "sign_test_p": p, "seeds_favor_HT": wins, "seeds_favor_ARF": loss})

    pd.DataFrame(rows_csv).to_csv(cfg.OUT_TABLE2_CSV, index=False)
    with open(cfg.OUT_TABLE2_TEX, "w") as f:
        f.write("\n".join(tex_lines) + "\n")

    print("=== Table II values (to report) ===")
    print(pd.DataFrame(rows_csv).to_string(index=False))
    print("\n=== Flooding decomposition: gradual_balanced (the clean proof) ===")
    print(flood[flood.variant == "gradual_balanced"].to_string(index=False))
    print(f"\n[SUCCESS] tabular body -> {cfg.OUT_TABLE2_TEX}")
    print(f"[SUCCESS] raw values   -> {cfg.OUT_TABLE2_CSV}")
    print(f"[SUCCESS] flooding      -> {cfg.OUT_FLOODING}")


if __name__ == "__main__":
    main()