# 04 — Speaker-level Decomposition of the BoM Rise

**Question.** Was the 1971 → 2025 rise in BoM citation share a *generational handoff* (new speakers citing differently) or a *behavior change* (same speakers changing)?

**Method.** Weighted two-way fixed-effects decomposition of talk-level BoM share.
Also compute per-speaker contribution to the modern-era (2011-25) BoM share above the 1971-85 baseline, weighted by the speaker's fraction of modern citations.

## Variance decomposition (R² of predicting talk-level BoM share)

| spec | R² |
|---|---:|
| Year only | 0.131 |
| Speaker only | 0.335 |
| Speaker + Year | 0.369 |

**Reading.** Speaker FEs explain **~2.5×** more of the variance than year FEs do. The incremental R² from adding year on top of speaker is just 3.4 pp, meaning the time trend is mostly **realized through who speaks**, not through individuals changing behavior. The BoM rise is chiefly a **generational handoff**.

## Aggregate shift
BoM share of all citations: **17.3 %** (1971-85) → **35.7 %** (2011-25). Δ = **+18.4 pp**.

## Top ringleaders (contribution to modern-era BoM share above 1971-85 baseline)

| speaker | modern BoM share | weight | contribution (pp) |
|---|---:|---:|---:|
| David A. Bednar         | 43 % | 4.5 % | +1.16 |
| Dale G. Renlund         | 45 % | 3.5 % | +0.97 |
| D. Todd Christofferson  | 35 % | 5.1 % | +0.89 |
| Russell M. Nelson       | 32 % | 5.5 % | +0.82 |
| Quentin L. Cook         | 36 % | 3.3 % | +0.63 |
| Dallin H. Oaks          | 32 % | 4.0 % | +0.61 |
| Gerrit W. Gong          | 35 % | 3.1 % | +0.56 |
| Ulisses Soares          | 36 % | 2.8 % | +0.50 |

Bednar and Renlund pop out as the highest per-talk BoM-citers among modern apostles who also have a substantial share of conference airtime.

## Takeaways
- The BoM rise is **not driven by broad, uniform drift** — it is mostly a **cohort effect** from a handful of modern apostles with BoM-heavy styles.
- Bednar (43 %) and Renlund (45 %) are the standout BoM-centric voices; Nelson and Christofferson contribute by volume as much as style.
- This explains why the Nelson-2018 ITS showed a null share-effect (Analysis 02): the BoM share had already been lifted by these speakers before 2018.

## Caveats
- Contribution metric is a simple Oaxaca-style decomposition; ignores interaction with talk length.
- Speaker identity is exact-match only after mojibake + NBSP normalization (see `_shared/data.py::fix_mojibake`). Any remaining spelling drift (e.g. middle-initial omitted in one talk) would still split a speaker.

Artifacts: `variance_decomposition.csv`, `top_ringleaders.csv`, `bom_share_by_year.csv`.
