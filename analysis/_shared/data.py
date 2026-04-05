"""Shared data loader for citation analyses."""
from __future__ import annotations

import glob
import os
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[2]
BOOKS = ["bom", "dc", "pgp", "nt", "ot"]


def latest_parquet() -> Path:
    candidates = sorted(glob.glob(str(REPO_ROOT / "conference_talks_*.parquet")))
    if not candidates:
        raise FileNotFoundError("No conference_talks_*.parquet found")
    return Path(candidates[-1])


def load() -> pd.DataFrame:
    df = pd.read_parquet(latest_parquet())
    df = df.copy()
    df["Year"] = df["Year"].astype(int)
    df["Month"] = df["Month"].astype(int)
    df["Conference"] = df["Year"].astype(str) + "-" + df["Month"].astype(str).str.zfill(2)
    df["ConfIndex"] = df["Year"] * 2 + (df["Month"] == 10).astype(int)  # 2 confs/yr
    # Normalize speaker names (strip whitespace, collapse)
    df["Speaker"] = df["Speaker"].fillna("").str.strip()
    # total citations per talk
    df["total_cites"] = df[BOOKS].sum(axis=1)
    return df.sort_values(["Year", "Month"]).reset_index(drop=True)


def by_conference(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate citations per conference (Year-Month)."""
    g = df.groupby(["Year", "Month", "Conference"], as_index=False)[BOOKS + ["total_cites"]].sum()
    g["n_talks"] = df.groupby(["Year", "Month", "Conference"]).size().values
    for b in BOOKS:
        g[f"{b}_share"] = g[b] / g["total_cites"].replace(0, pd.NA)
    return g


def by_year(df: pd.DataFrame) -> pd.DataFrame:
    g = df.groupby("Year", as_index=False)[BOOKS + ["total_cites"]].sum()
    g["n_talks"] = df.groupby("Year").size().values
    for b in BOOKS:
        g[f"{b}_share"] = g[b] / g["total_cites"].replace(0, pd.NA)
    return g
