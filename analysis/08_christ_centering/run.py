"""Christ-centering index: (NT + BoM) / total citations per conference.

These two volumes contain the life and ministry of Christ (NT) and His
visit to the Americas / Atonement teachings (BoM). Their combined share
is a crude but interpretable Christ-centering proxy.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from analysis._shared.data import by_conference, by_year, load  # noqa: E402

OUT = Path(__file__).parent


def main() -> None:
    df = load()
    conf = by_conference(df)
    conf["christ_index"] = conf["nt_share"] + conf["bom_share"]
    conf[["Year", "Month", "Conference", "nt_share", "bom_share", "christ_index"]] \
        .to_csv(OUT / "christ_index_by_conference.csv", index=False)

    yr = by_year(df)
    yr["christ_index"] = yr["nt_share"] + yr["bom_share"]
    yr[["Year", "n_talks", "nt_share", "bom_share", "christ_index"]] \
        .to_csv(OUT / "christ_index_by_year.csv", index=False)

    print("Christ-centering index (NT+BoM share of citations), selected years:")
    for y in [1971, 1980, 1990, 2000, 2010, 2018, 2020, 2024, 2025]:
        row = yr[yr["Year"] == y]
        if len(row):
            r = row.iloc[0]
            print(f"  {y}: {r['christ_index']:.3f}  "
                  f"(NT={r['nt_share']:.3f}, BoM={r['bom_share']:.3f})")

    # 5-year rolling
    yr["rolling_5yr"] = yr["christ_index"].rolling(5).mean()
    yr[["Year", "christ_index", "rolling_5yr"]].to_csv(OUT / "christ_index_rolling.csv", index=False)

    # min/max
    hi = yr.loc[yr["christ_index"].idxmax()]
    lo = yr.loc[yr["christ_index"].idxmin()]
    print(f"\nPeak: {int(hi['Year'])} at {hi['christ_index']:.3f}")
    print(f"Low:  {int(lo['Year'])} at {lo['christ_index']:.3f}")


if __name__ == "__main__":
    main()
