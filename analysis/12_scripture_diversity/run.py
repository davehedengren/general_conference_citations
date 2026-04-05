"""Shannon entropy of the 5-book citation mix per talk and per year.

Higher entropy = more balanced (talk draws evenly from all 5 books).
Lower entropy = more mono-book.
Max entropy (5 books) = log2(5) ≈ 2.322.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from analysis._shared.data import BOOKS, load  # noqa: E402

OUT = Path(__file__).parent


def shannon(vec: np.ndarray) -> float:
    s = vec.sum()
    if s == 0:
        return float("nan")
    p = vec / s
    p = p[p > 0]
    return float(-(p * np.log2(p)).sum())


def main() -> None:
    df = load()
    ents = []
    for _, row in df.iterrows():
        v = np.array([row[b] for b in BOOKS], dtype=float)
        ents.append(shannon(v))
    df["entropy"] = ents

    # Per year: mean talk entropy, and entropy of aggregated counts
    rows = []
    for y, g in df.groupby("Year"):
        agg = g[BOOKS].sum().to_numpy(dtype=float)
        rows.append({
            "Year": int(y),
            "mean_talk_entropy": g["entropy"].mean(),
            "agg_entropy": shannon(agg),
            "n_talks_with_cites": int((g["total_cites"] > 0).sum()),
        })
    yr = pd.DataFrame(rows)
    yr.to_csv(OUT / "entropy_by_year.csv", index=False)
    print(yr.to_string(index=False))

    # Mono-book talks (entropy near 0, uses only 1-2 books)
    monodf = df[(df["total_cites"] >= 3) & (df["entropy"] <= 0.7)]
    mono_by_year = monodf.groupby("Year").size() / df[df["total_cites"] >= 3].groupby("Year").size()
    mono_by_year.to_csv(OUT / "monobook_share_by_year.csv", header=["monobook_fraction"])
    print("\nMono-book share (≥3 citations, entropy ≤ 0.7):")
    print(mono_by_year.round(3).to_string())


if __name__ == "__main__":
    main()
