"""First-talk effect: does a speaker's *debut* conference talk predict
their long-run citation fingerprint?

For speakers with >= 8 talks in the dataset, compare the first talk vs
the remainder. Report cosine similarity & BoM-share delta.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from analysis._shared.data import BOOKS, load  # noqa: E402

OUT = Path(__file__).parent
MIN_TALKS = 8


def safe_norm(v):
    s = v.sum()
    return v / s if s else v


def cos(a, b):
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    return float(np.dot(a, b) / (na * nb)) if na and nb else float("nan")


def main() -> None:
    df = load().sort_values(["Speaker", "Year", "Month"])
    rows = []
    for sp, g in df.groupby("Speaker"):
        if len(g) < MIN_TALKS:
            continue
        first = g.iloc[0][BOOKS].to_numpy(dtype=float)
        rest = g.iloc[1:][BOOKS].sum().to_numpy(dtype=float)
        if first.sum() == 0 or rest.sum() == 0:
            continue
        fv = safe_norm(first)
        rv = safe_norm(rest)
        rows.append({
            "speaker": sp,
            "n_talks": len(g),
            "debut_year": int(g.iloc[0]["Year"]),
            "cos_debut_vs_rest": cos(fv, rv),
            "bom_debut": fv[0], "bom_rest": rv[0],
            "nt_debut": fv[3], "nt_rest": rv[3],
        })
    res = pd.DataFrame(rows).sort_values("cos_debut_vs_rest", ascending=False)
    res.to_csv(OUT / "debut_vs_steady_state.csv", index=False)
    print("Summary:")
    print(f"  speakers: {len(res)}")
    print(f"  mean cos(debut, rest): {res['cos_debut_vs_rest'].mean():.3f}")
    print(f"  median: {res['cos_debut_vs_rest'].median():.3f}")
    # Correlation of debut BoM share with steady-state BoM share
    corr = res["bom_debut"].corr(res["bom_rest"])
    print(f"  pearson(bom_debut, bom_rest) = {corr:.3f}")
    print("\nMost-similar debut->rest (top 5):")
    print(res.head(5)[["speaker", "n_talks", "cos_debut_vs_rest", "bom_debut", "bom_rest"]].to_string(index=False))
    print("\nLeast-similar debut->rest (bottom 5):")
    print(res.tail(5)[["speaker", "n_talks", "cos_debut_vs_rest", "bom_debut", "bom_rest"]].to_string(index=False))


if __name__ == "__main__":
    main()
