"""April vs October (month) and within-conference position effects.

Position proxy: within each conference, rank the talks by their order
of appearance in the sorted dataframe (our sort by URL is a rough
approximation of session order). Compare first-quartile vs last-quartile
talks for each citation book.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from analysis._shared.data import BOOKS, load  # noqa: E402

OUT = Path(__file__).parent


def main() -> None:
    df = load().copy()
    # Month effect
    rows = []
    for m in (4, 10):
        sub = df[df["Month"] == m]
        tot = sub["total_cites"].sum()
        r = {"month": m, "n_talks": len(sub), "cites_per_talk": sub["total_cites"].mean()}
        for b in BOOKS:
            r[f"{b}_share"] = sub[b].sum() / tot
        rows.append(r)
    month_tab = pd.DataFrame(rows)
    month_tab.to_csv(OUT / "by_month.csv", index=False)
    print("By month:")
    print(month_tab.to_string(index=False))

    # Position within conference: quartiles by URL-sorted filename position
    df["pos"] = df.groupby("Conference").cumcount()
    df["n_in_conf"] = df.groupby("Conference")["Conference"].transform("count")
    df["q"] = ((df["pos"] / df["n_in_conf"]) * 4).astype(int).clip(0, 3)
    rows = []
    for q in range(4):
        sub = df[df["q"] == q]
        tot = sub["total_cites"].sum()
        r = {"quartile": q, "n_talks": len(sub), "cites_per_talk": sub["total_cites"].mean()}
        for b in BOOKS:
            r[f"{b}_share"] = sub[b].sum() / tot
        rows.append(r)
    q_tab = pd.DataFrame(rows)
    q_tab.to_csv(OUT / "by_quartile.csv", index=False)
    print("\nBy within-conference quartile (sorted by URL/title; rough proxy for session order):")
    print(q_tab.to_string(index=False))


if __name__ == "__main__":
    main()
