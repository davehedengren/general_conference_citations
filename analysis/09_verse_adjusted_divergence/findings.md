# 09 — Verse-Adjusted vs Raw Citation Divergence

**Question.** How does the picture change when we normalize citations by the length of each book? A citation to Pearl of Great Price (635 verses) represents far greater verse-density than a citation to Old Testament (23,145 verses).

**Method.** Divide each book's citation count by its verse total × 100 (standard "per 100 verses" scaling). Compare raw share to verse-adjusted share; compute per-speaker "density tilt".

## Cumulative 1971-2025: the headline

| book | total cites | verses | cites / 100v | raw share | verse-adj share | tilt (pp) |
|---|---:|---:|---:|---:|---:|---:|
| **PGP** | 2,636 | 635 | **415** | 5.5 % | **35.8 %** | **+30.4** |
| **D&C** | 11,662 | 3,654 | 319 | 24.1 % | 27.6 % | +3.4 |
| BoM  | 14,644 | 6,604 | 222 | 30.3 % | 19.2 % | **−11.2** |
| NT   | 14,357 | 7,957 | 180 | 29.7 % | 15.6 % | **−14.1** |
| **OT** | 5,023 | 23,145 | **22** | 10.4 % | 1.9 % | −8.5 |

## Takeaways

### 1. Pearl of Great Price is the most verse-dense book by a mile
PGP is cited **415 times per 100 verses** — nearly **2× the BoM rate** and **19× the OT rate**. Though it holds only 5.5 % of the raw pie, it holds **36 %** of the verse-adjusted pie. On a per-verse basis, PGP is effectively the center of General Conference scripture.

### 2. Old Testament is the most under-cited per verse
Just 22 citations per 100 OT verses. Even speakers with the "highest" verse-adjusted OT share barely clear 1 %. OT is long and under-mined.

### 3. BoM's raw dominance flips when adjusted for length
BoM's 30.3 % of raw citations shrinks to 19.2 % on a verse-adjusted basis. Verse-adjusted, the ordering becomes: **PGP (36 %) > D&C (28 %) > BoM (19 %) > NT (16 %) > OT (2 %)** — a very different picture.

## Per-speaker density tilts

### Biggest short-book (PGP) tilts
Old-guard mid-century speakers dominate — they cited PGP far more than average:

| speaker | n talks | PGP tilt (pp) | PGP raw share | PGP verse-adj share |
|---|---:|---:|---:|---:|
| John H. Vandenberg  | 10 | +55.9 | 22 % | 78 % |
| Eldred G. Smith     | 10 | +53.1 | 20 % | 74 % |
| Spencer W. Kimball  | 75 | +49.2 | 14 % | 63 % |
| Joseph Anderson     | 13 | +48.2 | 16 % | 64 % |
| S. Dilworth Young   | 12 | +47.6 |  9 % | 56 % |
| L. Tom Perry        | 87 | +47.5 | 13 % | 60 % |
| N. Eldon Tanner     | 64 | +46.4 | 12 % | 59 % |

**Kimball and N. Eldon Tanner stand out** among prophetic-era speakers for their heavy reliance on PGP material (Moses, Abraham, Joseph Smith—Matthew, JS—History, Articles of Faith).

### OT under-utilization is universal
Nobody *can* tilt strongly toward OT because it is so long. The least-OT-penalized speakers (Pinegar, Stevenson, Komatsu) only reach −3 pp tilts.

## Caveats
- Verse-density is a blunt length measure — not all verses carry equal content weight (e.g. genealogies vs. Sermon on the Mount).
- Verse counts are from LDS standard editions; some modern editions differ slightly on PGP (Facsimiles, etc.).
- Tilt metric is per-speaker; confounded with era (modern CFM curricula may disfavor PGP).

## Artifacts
- `book_summary.csv` — cumulative raw / verse-adjusted stats
- `per100_by_year.csv` — time series of per-100-verse rates
- `share_comparison_by_year.csv` — raw vs. verse-adj shares over time
- `speaker_density_tilt.csv` — per-speaker tilts (full list, ≥10 talks)
