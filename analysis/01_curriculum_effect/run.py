"""Does the year's Sunday-School / Come-Follow-Me book of study bump
citations to that book in the conferences held during that year?

Cycle used (Sunday School Gospel Doctrine / Come Follow Me):
    4-year rotation: OT, NT, BoM, D&C (w/ Church History).
    Anchor: 2024 = BoM, 2025 = D&C, 2023 = NT, 2022 = OT.
Earlier years extrapolated backwards with the same rotation. This is
an approximation; pre-CFM curricula varied and home-study materials
shifted in 2019. We still test the rotation as a simple instrument.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from analysis._shared.data import BOOKS, by_conference, load  # noqa: E402

OUT = Path(__file__).parent


def curriculum_book(year: int) -> str:
    """Return the book-of-study for a given year (one of bom/dc/nt/ot)."""
    # Anchor: 2024 -> bom. Rotation: OT, NT, BoM, DC
    rot = ["ot", "nt", "bom", "dc"]
    idx = (year - 2022) % 4  # 2022=ot
    return rot[idx]


def main() -> None:
    df = load()
    conf = by_conference(df)
    conf["curriculum"] = conf["Year"].map(curriculum_book)

    # For each conference, compute the share of citations going to THE curriculum book
    # vs the share NOT going to it. Then compare: when book X is "in study" year,
    # is X's share higher than in other years?
    rows = []
    for b in ["bom", "dc", "nt", "ot"]:
        in_year = conf[conf["curriculum"] == b][f"{b}_share"].mean()
        out_year = conf[conf["curriculum"] != b][f"{b}_share"].mean()
        rows.append({
            "book": b,
            "share_when_in_curriculum": in_year,
            "share_when_not": out_year,
            "lift_pp": (in_year - out_year) * 100,
            "lift_ratio": in_year / out_year,
        })
    summary = pd.DataFrame(rows)
    summary.to_csv(OUT / "curriculum_lift_all_years.csv", index=False)

    # Post-2019 (Come Follow Me era) is the cleanest test
    modern = conf[conf["Year"] >= 2019]
    rows_m = []
    for b in ["bom", "dc", "nt", "ot"]:
        in_year = modern[modern["curriculum"] == b][f"{b}_share"].mean()
        out_year = modern[modern["curriculum"] != b][f"{b}_share"].mean()
        rows_m.append({
            "book": b,
            "share_when_in_curriculum": in_year,
            "share_when_not": out_year,
            "lift_pp": (in_year - out_year) * 100,
            "lift_ratio": in_year / out_year if out_year else float("nan"),
        })
    summary_m = pd.DataFrame(rows_m)
    summary_m.to_csv(OUT / "curriculum_lift_2019plus.csv", index=False)

    # Per-year time series with the curriculum book highlighted
    ts = conf[["Year", "Month", "Conference", "curriculum",
               "bom_share", "dc_share", "nt_share", "ot_share"]].copy()
    ts["curriculum_book_share"] = ts.apply(lambda r: r[f"{r['curriculum']}_share"], axis=1)
    ts.to_csv(OUT / "conference_level_shares.csv", index=False)

    # By-session effect: does April or October show the bigger bump?
    # April comes BEFORE the bulk of year's study, October in the middle.
    rows_s = []
    for month in (4, 10):
        sub = modern[modern["Month"] == month]
        for b in ["bom", "dc", "nt", "ot"]:
            in_year = sub[sub["curriculum"] == b][f"{b}_share"].mean()
            out_year = sub[sub["curriculum"] != b][f"{b}_share"].mean()
            rows_s.append({
                "month": month,
                "book": b,
                "in_curr": in_year,
                "out_curr": out_year,
                "lift_pp": (in_year - out_year) * 100,
            })
    pd.DataFrame(rows_s).to_csv(OUT / "curriculum_lift_by_session.csv", index=False)

    print("== All years (1971-2025) ==")
    print(summary.to_string(index=False))
    print("\n== 2019+ (Come Follow Me era) ==")
    print(summary_m.to_string(index=False))


if __name__ == "__main__":
    main()
