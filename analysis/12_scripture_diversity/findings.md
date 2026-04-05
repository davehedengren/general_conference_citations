# 12 — Scripture Diversity (Shannon Entropy)

**Question.** Are individual talks getting more or less scripture-diverse over time? Is conference as a whole more concentrated on a single book?

**Method.** Shannon entropy over the 5-book citation vector, computed both per-talk (then averaged) and on the aggregate counts of the year. Max entropy (perfect balance) = log₂(5) ≈ 2.322.

## Results — per-year

| era | mean talk entropy | aggregate entropy |
|---|---:|---:|
| 1971-80 | ~1.06 | ~2.10 |
| 1981-90 | ~1.20 | ~2.09 |
| 1991-00 | ~1.23 | ~2.09 |
| 2001-10 | ~1.33 | ~2.09 |
| 2011-20 | ~1.40 | ~2.04 |
| 2021-25 | **1.45** | **2.02** |

## Takeaways
- **Per-talk entropy has *risen*** from ~1.06 (1970s) to ~1.45 (2020s). **Individual talks today cite from more books** than their 1970s counterparts — they are less mono-focused.
- **Aggregate entropy has slightly *fallen*** (2.10 → 2.02). Across all talks in a year, the distribution is slightly more concentrated (BoM pulling share).
- These two trends resolve a paradox: **within-talk diversity up, between-talk diversity down**. Speakers now each dip into BoM + NT + D&C in a single talk, but the overall pulpit centers more on BoM and NT.

## Caveats
- Shannon entropy on only 5 bins is coarse.
- Entropy metric treats all books symmetrically.

Artifacts: `entropy_by_year.csv`, `monobook_share_by_year.csv`.
