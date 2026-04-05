"""Verse-adjusted vs raw citation analysis.

Each book has a fixed number of verses. A citation to Pearl of Great
Price (635 verses) represents far more verse-density than a citation
to the Old Testament (23,145 verses). Normalizing by verse count asks
a different question: "holding book length constant, which book does
conference favor per unit of scripture?"

Metrics produced:
    - citations per 100 verses, per book, cumulative 1971-2025
    - time series of each book's per-100-verse rate
    - raw vs verse-adjusted share comparison by year
    - per-speaker short-book preference: a speaker's "density tilt"
      is (speaker_share_verseadj - speaker_share_raw) for each book.
      A positive tilt on PGP means they favor it more than average
      once we control for its small size.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from analysis._shared.data import BOOKS, VERSE_COUNTS, load  # noqa: E402

OUT = Path(__file__).parent
MIN_TALKS = 10
MIN_CITES = 20


def add_verse_adjusted(df: pd.DataFrame) -> pd.DataFrame:
    for b in BOOKS:
        df[f"{b}_per100"] = df[b] / VERSE_COUNTS[b] * 100
    df["total_per100"] = df[[f"{b}_per100" for b in BOOKS]].sum(axis=1)
    return df


def main() -> None:
    df = add_verse_adjusted(load())

    # 1) Cumulative citations per 100 verses, by book
    totals = df[BOOKS].sum()
    per100 = (totals / pd.Series(VERSE_COUNTS) * 100).round(2)
    raw_share = (totals / totals.sum()).round(4)
    va_share  = (per100 / per100.sum()).round(4)
    summary = pd.DataFrame({
        "citations_total":   totals,
        "verses":            pd.Series(VERSE_COUNTS),
        "cites_per_100v":    per100,
        "raw_share":         raw_share,
        "verse_adj_share":   va_share,
        "share_tilt_pp":     ((va_share - raw_share) * 100).round(2),
    })
    summary.index.name = "book"
    summary.to_csv(OUT / "book_summary.csv")
    print("Cumulative 1971-2025:")
    print(summary.to_string())

    # 2) Time series: per-100-verse citation rate by year
    yr = df.groupby("Year")[BOOKS].sum()
    for b in BOOKS:
        yr[f"{b}_per100"] = yr[b] / VERSE_COUNTS[b] * 100
    yr[[f"{b}_per100" for b in BOOKS]].to_csv(OUT / "per100_by_year.csv")

    # 3) Raw share vs verse-adjusted share, by year
    share_rows = []
    for y, g in df.groupby("Year"):
        raw_tot = g[BOOKS].sum().sum()
        va_tot  = g[[f"{b}_per100" for b in BOOKS]].sum().sum()
        row = {"Year": int(y)}
        for b in BOOKS:
            row[f"{b}_raw_share"] = g[b].sum() / raw_tot if raw_tot else np.nan
            row[f"{b}_va_share"]  = g[f"{b}_per100"].sum() / va_tot if va_tot else np.nan
        share_rows.append(row)
    pd.DataFrame(share_rows).to_csv(OUT / "share_comparison_by_year.csv", index=False)

    # 4) Per-speaker density tilt (verse-adjusted share - raw share, per book)
    by_sp = df.groupby("Speaker")[BOOKS + [f"{b}_per100" for b in BOOKS]].sum()
    by_sp["n_talks"] = df.groupby("Speaker").size()
    by_sp = by_sp[(by_sp[BOOKS].sum(axis=1) >= MIN_CITES) & (by_sp["n_talks"] >= MIN_TALKS)]
    raw_tot = by_sp[BOOKS].sum(axis=1)
    va_tot  = by_sp[[f"{b}_per100" for b in BOOKS]].sum(axis=1)
    for b in BOOKS:
        by_sp[f"{b}_raw_share"] = by_sp[b] / raw_tot
        by_sp[f"{b}_va_share"]  = by_sp[f"{b}_per100"] / va_tot
        by_sp[f"{b}_tilt_pp"]   = (by_sp[f"{b}_va_share"] - by_sp[f"{b}_raw_share"]) * 100
    tilt_cols = ["n_talks"] + [f"{b}_tilt_pp" for b in BOOKS] \
                + [f"{b}_raw_share" for b in BOOKS] + [f"{b}_va_share" for b in BOOKS]
    by_sp[tilt_cols].to_csv(OUT / "speaker_density_tilt.csv")

    # Who tilts most toward the short books (PGP, D&C, BoM)?
    print("\nTop 10 speakers with biggest PGP tilt (favor short book):")
    print(by_sp.nlargest(10, "pgp_tilt_pp")[["n_talks", "pgp_tilt_pp",
          "pgp_raw_share", "pgp_va_share"]].to_string())
    print("\nTop 10 speakers with biggest OT tilt (favor long book):")
    print(by_sp.nlargest(10, "ot_tilt_pp")[["n_talks", "ot_tilt_pp",
          "ot_raw_share", "ot_va_share"]].to_string())


if __name__ == "__main__":
    main()
