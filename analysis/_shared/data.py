"""Shared data loader for citation analyses."""
from __future__ import annotations

import glob
import os
import re
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[2]
BOOKS = ["bom", "dc", "pgp", "nt", "ot"]

# Verses per book (LDS standard editions). Static; safe to hard-code.
VERSE_COUNTS = {
    "ot":  23145,
    "nt":   7957,
    "bom":  6604,
    "dc":   3654,
    "pgp":   635,
}


def fix_mojibake(s: str) -> str:
    """Repair latin-1-as-utf-8 mojibake and normalize whitespace.

    The upstream parquet has two related encoding issues:
      1. UTF-8 bytes re-read as Latin-1, so "é" shows as "Ã©" (classic
         mojibake). Fixed by re-encoding as Latin-1 then decoding UTF-8.
      2. Non-breaking spaces (U+00A0) in names like "DallinÂ\xa0H. Oaks"
         which split the same speaker into two rows. Replaced with a
         regular space.
    """
    if not isinstance(s, str) or not s:
        return s
    try:
        s = s.encode("latin-1").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        pass
    s = s.replace("\u00a0", " ")
    s = re.sub(r"\s+", " ", s).strip()
    return s


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
    # Normalize speaker names: fix mojibake + collapse NBSP duplicates
    df["Speaker"] = df["Speaker"].fillna("").map(fix_mojibake)
    # Fix titles similarly (they have the same encoding issue)
    if "Title" in df.columns:
        df["Title"] = df["Title"].fillna("").map(fix_mojibake)
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
