# 12 — Scripture Diversity (Shannon Entropy)

**Question.** Are individual talks getting more or less scripture-diverse over time? Is conference as a whole more concentrated on a single book?

**Method.** Shannon entropy over the **4-book** citation vector (BoM, D&C, NT, OT), computed both per-talk (then averaged) and on the aggregate counts of the year. Max entropy (perfect balance) = log₂(4) = 2.0.

**Why PGP is excluded.** Pearl of Great Price is tiny (635 verses) and its citation count is dominated by a handful of recurring passages (Moses 1:39, Articles of Faith, JS—History 1). Including PGP as a 5th bin made the entropy series noisy and mixed two very different signals (book-length diversity vs. passage-repetition). Dropping PGP isolates diversity across the four "major" volumes.

## Results — per-year (PGP excluded)

| era | mean talk entropy | aggregate entropy |
|---|---:|---:|
| 1971-80 | 0.95 | 1.88 |
| 1981-90 | 1.12 | 1.89 |
| 1991-00 | 1.11 | 1.90 |
| 2001-10 | 1.21 | 1.89 |
| 2011-20 | 1.26 | 1.85 |
| 2021-25 | **1.34** | **1.84** |

Max = 2.0. Per-talk entropy has moved from **~48 % of max → ~67 % of max**. Aggregate entropy has slipped slightly (~94 % → ~92 %).

## Takeaways
- **Per-talk entropy rose** from ~0.95 (1970s) to ~1.34 (2020s). Individual talks today cite from more of the four major books than their 1970s counterparts — they are less mono-focused.
- **Aggregate entropy has slightly *fallen*** (1.88 → 1.84). Across all talks in a year, the distribution is slightly more concentrated (BoM pulling share).
- The paradox is preserved: **within-talk diversity up, between-talk diversity down**. Modern speakers each dip into BoM + NT + D&C within a single talk, but the overall pulpit centers more on BoM.

## Caveats
- Entropy on only 4 bins is still coarse.
- Treats all books symmetrically.
- Excluding PGP discards ~5 % of citations; the 5-book version (archived in git history) shows the same qualitative trend with more volatility.

Artifacts: `entropy_by_year.csv`, `monobook_share_by_year.csv`.
