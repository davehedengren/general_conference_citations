"""Interrupted time-series around major Book of Mormon reading challenges.

Known challenges:
    - 1986-04 / 1986-10: President Benson's BoM emphasis (1986-11 General Conference
      "Flooding the Earth with the Book of Mormon"). Use 1986-10 as shock.
    - 2005-08: President Hinckley's challenge to read the BoM by year-end 2005.
      Shock = 2005-10 conference.
    - 2018-04/10: President Nelson's invitation to immerse in the BoM
      (women's session Oct 2017; men's Oct 2017; general Oct 2018). Shock = 2018-10.
We test the BoM *share* of citations (robust to changing talk length) with a
simple pre/post mean difference in a +/- 4 conference window.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from analysis._shared.data import by_conference, load  # noqa: E402

OUT = Path(__file__).parent
SHOCKS = {
    "Benson 1986":   (1986, 10),
    "Hinckley 2005": (2005, 10),
    "Nelson 2018":   (2018, 10),
}
WINDOW = 4  # conferences before/after


def main() -> None:
    conf = by_conference(load()).sort_values(["Year", "Month"]).reset_index(drop=True)
    conf["t"] = range(len(conf))

    rows = []
    for name, (sy, sm) in SHOCKS.items():
        idx = conf[(conf["Year"] == sy) & (conf["Month"] == sm)].index
        if len(idx) == 0:
            continue
        i = int(idx[0])
        pre = conf.iloc[max(0, i - WINDOW):i]
        post = conf.iloc[i: i + WINDOW + 1]   # include shock conf itself
        rows.append({
            "event": name,
            "shock_conference": f"{sy}-{sm:02d}",
            "pre_bom_share":  pre["bom_share"].mean(),
            "post_bom_share": post["bom_share"].mean(),
            "delta_pp":       (post["bom_share"].mean() - pre["bom_share"].mean()) * 100,
            "pre_bom_per_talk":  (pre["bom"].sum() / pre["n_talks"].sum()),
            "post_bom_per_talk": (post["bom"].sum() / post["n_talks"].sum()),
        })
    results = pd.DataFrame(rows)
    results.to_csv(OUT / "challenge_windows.csv", index=False)
    print(results.to_string(index=False))

    # Also save the BoM share time series with shock markers for plotting later
    ts = conf[["Year", "Month", "Conference", "bom", "bom_share", "n_talks"]].copy()
    ts.to_csv(OUT / "bom_share_timeseries.csv", index=False)

    # Long pre/post (2yr = 4 confs vs entire subsequent presidency) for Benson
    benson_idx = conf[(conf["Year"] == 1986) & (conf["Month"] == 10)].index[0]
    benson_pre = conf.iloc[max(0, benson_idx - 8):benson_idx]["bom_share"].mean()
    benson_post = conf.iloc[benson_idx:benson_idx + 16]["bom_share"].mean()  # 8 years
    print(f"\nBenson long-horizon: pre 4yr={benson_pre:.3f}  post 8yr={benson_post:.3f}  Δ={benson_post-benson_pre:+.3f}")


if __name__ == "__main__":
    main()
