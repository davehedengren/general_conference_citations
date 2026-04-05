"""Greedy binary-segmentation change-point detection for each book's
share time series at conference resolution.

Uses L2 cost and a simple recursive binary segmentation to locate up to
N_CP change points per series. No external dependency required.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from analysis._shared.data import by_conference, load  # noqa: E402

OUT = Path(__file__).parent
N_CP = 4  # up to 4 change points per book


def l2_cost(x):
    return float(((x - x.mean()) ** 2).sum())


def best_split(x, lo, hi, min_size=6):
    """Find best single split index in [lo, hi)."""
    best, best_cost = None, l2_cost(x[lo:hi])
    for i in range(lo + min_size, hi - min_size):
        c = l2_cost(x[lo:i]) + l2_cost(x[i:hi])
        if c < best_cost:
            best_cost = c
            best = i
    return best, best_cost


def binseg(x, n, min_size=6):
    """Recursive binary segmentation returning up to n change points (indices)."""
    segs = [(0, len(x))]
    cps = []
    for _ in range(n):
        # Find the segment whose split gives the biggest gain
        best_gain, best_cp, best_seg = -1, None, None
        for lo, hi in segs:
            if hi - lo < 2 * min_size:
                continue
            cp, cost_after = best_split(x, lo, hi, min_size)
            if cp is None:
                continue
            cost_before = l2_cost(x[lo:hi])
            gain = cost_before - cost_after
            if gain > best_gain:
                best_gain, best_cp, best_seg = gain, cp, (lo, hi)
        if best_cp is None:
            break
        cps.append(best_cp)
        lo, hi = best_seg
        segs.remove((lo, hi))
        segs.append((lo, best_cp))
        segs.append((best_cp, hi))
    return sorted(cps)


def main() -> None:
    conf = by_conference(load()).sort_values(["Year", "Month"]).reset_index(drop=True)
    conf["label"] = conf["Conference"]

    rows = []
    for b in ["bom", "dc", "pgp", "nt", "ot"]:
        x = conf[f"{b}_share"].to_numpy(dtype=float)
        cps = binseg(x, N_CP)
        for cp in cps:
            lo = max(0, cp - 4); hi = min(len(x), cp + 4)
            pre_mean = x[lo:cp].mean() if cp > lo else float("nan")
            post_mean = x[cp:hi].mean() if cp < hi else float("nan")
            rows.append({
                "book": b,
                "cp_index": cp,
                "conference": conf.iloc[cp]["Conference"],
                "pre_8conf_mean": round(pre_mean, 4),
                "post_8conf_mean": round(post_mean, 4),
                "delta_pp": round((post_mean - pre_mean) * 100, 2),
            })
    out = pd.DataFrame(rows).sort_values(["book", "cp_index"])
    out.to_csv(OUT / "change_points.csv", index=False)
    print(out.to_string(index=False))


if __name__ == "__main__":
    main()
