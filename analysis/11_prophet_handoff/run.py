"""Prophet-handoff transition window.

For each presidency transition, look at:
    - Outgoing prophet's average BoM share (last 8 confs of presidency)
    - Incoming prophet's average BoM share (first 8 confs of presidency)
    - The 2 conferences around the transition (one before, one after)
Does the conference "eulogize" the outgoing prophet's fingerprint?
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from analysis._shared.data import by_conference, load  # noqa: E402
from analysis._shared.prophets import PROPHETS  # noqa: E402

OUT = Path(__file__).parent


def main() -> None:
    conf = by_conference(load()).sort_values(["Year", "Month"]).reset_index(drop=True)
    # Assign prophet to each conference (using month-level dates)
    def prophet(year, month):
        ym = year * 100 + month
        for name, sy, sm, ey, em in PROPHETS:
            s = sy * 100 + sm
            e = (ey * 100 + em) if ey else 999999
            if s <= ym <= e:
                return name
        return "Unknown"
    conf["prophet"] = [prophet(y, m) for y, m in zip(conf["Year"], conf["Month"])]

    # Identify transitions
    transitions = []
    for i in range(1, len(conf)):
        if conf.iloc[i]["prophet"] != conf.iloc[i - 1]["prophet"]:
            transitions.append(i)

    rows = []
    for ti in transitions:
        out_prophet = conf.iloc[ti - 1]["prophet"]
        in_prophet = conf.iloc[ti]["prophet"]
        pre_window = conf.iloc[max(0, ti - 8):ti]
        post_window = conf.iloc[ti:ti + 8]
        rows.append({
            "transition_at": conf.iloc[ti]["Conference"],
            "outgoing": out_prophet, "incoming": in_prophet,
            "pre_bom_share": pre_window["bom_share"].mean(),
            "post_bom_share": post_window["bom_share"].mean(),
            "delta_pp": (post_window["bom_share"].mean() - pre_window["bom_share"].mean()) * 100,
            "pre_nt_share": pre_window["nt_share"].mean(),
            "post_nt_share": post_window["nt_share"].mean(),
            "nt_delta_pp": (post_window["nt_share"].mean() - pre_window["nt_share"].mean()) * 100,
        })
    out = pd.DataFrame(rows)
    out.to_csv(OUT / "transitions.csv", index=False)
    print(out.to_string(index=False))


if __name__ == "__main__":
    main()
