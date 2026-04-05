"""Decompose the rise in BoM citations into:
    - Speaker fixed effects (generational handoff)
    - Year fixed effects (secular trend)
    - Ringleader contributions (top individuals driving year-over-year change)

Method:
    Outcome y = bom_share at talk level (weighted by total_cites).
    Fit: y_it = alpha_i + gamma_t + e_it  via iterative demeaning.
    Compare variance explained by speaker vs year FEs.
    Then: compute each speaker's total contribution to the aggregate BoM rise
    between 1971-1985 (pre-Benson) and 2011-2025 (modern) as:
        contribution_s = sum over their talks of (bom/total_cites_modern - baseline_share) * weight.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from analysis._shared.data import load  # noqa: E402

OUT = Path(__file__).parent


def two_way_demean(df, y_col, group1, group2, n_iter=30, tol=1e-6):
    """Iterative within-transform for unbalanced two-way FE."""
    y = df[y_col].to_numpy(dtype=float).copy()
    g1 = df[group1].to_numpy()
    g2 = df[group2].to_numpy()
    w = df["total_cites"].to_numpy(dtype=float)
    prev = np.inf
    for _ in range(n_iter):
        # subtract weighted mean by group1
        s = pd.Series(y * w).groupby(g1).sum() / pd.Series(w).groupby(g1).sum()
        y = y - pd.Series(g1).map(s).to_numpy()
        s = pd.Series(y * w).groupby(g2).sum() / pd.Series(w).groupby(g2).sum()
        y = y - pd.Series(g2).map(s).to_numpy()
        ss = float(np.sum(w * y * y))
        if abs(prev - ss) < tol:
            break
        prev = ss
    return y


def main() -> None:
    df = load()
    df = df[df["total_cites"] > 0].copy()
    df["bom_share"] = df["bom"] / df["total_cites"]

    # Variance decomposition via sequential FE (nested R^2 contributions)
    y = df["bom_share"].to_numpy(dtype=float)
    w = df["total_cites"].to_numpy(dtype=float)

    def wvar(v):
        m = np.sum(v * w) / np.sum(w)
        return float(np.sum(w * (v - m) ** 2))

    tss = wvar(y)

    # Year only
    e_year = two_way_demean(df.assign(_g2=0), "bom_share", "Year", "_g2")
    rss_year = float(np.sum(w * e_year * e_year))

    # Speaker only
    e_sp = two_way_demean(df.assign(_g2=0), "bom_share", "Speaker", "_g2")
    rss_sp = float(np.sum(w * e_sp * e_sp))

    # Both
    e_both = two_way_demean(df, "bom_share", "Speaker", "Year")
    rss_both = float(np.sum(w * e_both * e_both))

    decomp = {
        "tss": tss,
        "r2_year_only":    1 - rss_year / tss,
        "r2_speaker_only": 1 - rss_sp / tss,
        "r2_both":         1 - rss_both / tss,
    }
    pd.DataFrame([decomp]).to_csv(OUT / "variance_decomposition.csv", index=False)
    print("Variance decomposition (R^2 in predicting talk-level BoM share):")
    for k, v in decomp.items():
        print(f"  {k}: {v:.4f}")

    # Ringleaders: who contributed most to the TOTAL BoM citation increase
    # between baseline (1971-1985) and modern (2011-2025)?
    early = df[df["Year"].between(1971, 1985)]
    late  = df[df["Year"].between(2011, 2025)]

    early_share = early["bom"].sum() / early["total_cites"].sum()
    late_share  = late["bom"].sum()  / late["total_cites"].sum()
    print(f"\nBaseline BoM share 1971-85: {early_share:.3f}  "
          f"Modern 2011-25: {late_share:.3f}  "
          f"Δ={late_share-early_share:+.3f}")

    # Per-speaker contribution to the late-era aggregate BoM share relative to baseline
    late_by_sp = late.groupby("Speaker").agg(
        bom=("bom", "sum"),
        tot=("total_cites", "sum"),
        n_talks=("Title", "count"),
    )
    late_by_sp["bom_share"] = late_by_sp["bom"] / late_by_sp["tot"]
    # contribution to the modern aggregate share above baseline, weighted by share of modern cites
    late_total = late_by_sp["tot"].sum()
    late_by_sp["weight"] = late_by_sp["tot"] / late_total
    late_by_sp["contrib_vs_baseline_pp"] = (
        (late_by_sp["bom_share"] - early_share) * late_by_sp["weight"] * 100
    )
    ringleaders = late_by_sp.sort_values("contrib_vs_baseline_pp", ascending=False)
    ringleaders[["n_talks", "tot", "bom_share", "weight", "contrib_vs_baseline_pp"]] \
        .head(25).to_csv(OUT / "top_ringleaders.csv")
    print("\nTop contributors to the late-era BoM-share rise (vs 1971-85 baseline):")
    print(ringleaders[["n_talks", "bom_share", "weight", "contrib_vs_baseline_pp"]]
          .head(15).to_string())

    # Year-over-year BoM share trend, saved for plotting
    yrs = df.groupby("Year").apply(
        lambda g: pd.Series({"bom_share": g["bom"].sum() / g["total_cites"].sum(),
                             "n_talks": len(g)})
    )
    yrs.to_csv(OUT / "bom_share_by_year.csv")


if __name__ == "__main__":
    main()
