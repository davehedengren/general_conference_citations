# 03 — Prophet Citation Fingerprint → Presidency

**Question.** When a man becomes prophet, does his *pre-presidency* citation pattern predict how the conference body cites scripture during his presidency?

**Method.** For each prophet P:
- Build `fp_personal_pre` = normalized BoM/DC/PGP/NT/OT share of P's own talks before his presidency.
- Build `fp_conf_during` = same vector computed from **all other speakers** during P's presidency.
- Compare to `fp_conf_pre` (the conference baseline immediately before P).

## BoM-share only (most interpretable slice)

| prophet | personal pre | conf pre | conf during | during − pre |
|---|---:|---:|---:|---:|
| Harold B. Lee       | 19.4 % | 12.3 % | 14.8 % | +2.4 |
| Spencer W. Kimball  |  8.9 % | 13.5 % | 18.7 % | +5.2 |
| **Ezra Taft Benson**| **30.3 %** | **16.6 %** | **31.4 %** | **+14.8** |
| Howard W. Hunter    | 14.1 % | 24.1 % | 26.9 % | +2.7 |
| Gordon B. Hinckley  | 11.6 % | 24.4 % | 32.2 % | +7.8 |
| Thomas S. Monson    |  9.6 % | 27.5 % | 33.4 % | +5.9 |
| **Russell M. Nelson**| **29.4 %** | **28.3 %** | **37.5 %** | **+9.2** |

## Takeaway

Two prophets stand out for having a **BoM-heavy personal fingerprint** *and* a large BoM lift during their presidency:
- **Benson**: personal 30 % / conf jumped from 17 % → 31 % (+14.8 pp). Strongest alignment case.
- **Nelson**: personal 29 % / conf jumped 28 % → 37.5 % (+9.2 pp). The body moved toward him.

Conversely, BoM share climbed *during* Hinckley and Monson presidencies even though their personal fingerprints skewed strongly toward NT — consistent with a broader secular uptrend independent of the individual prophet.

The cosine-similarity comparison (`cos_personal_vs_during` − `cos_confpre_vs_during`) is **negative for every prophet**, because conference-wide citation patterns have enough autocorrelation that the immediate past is always the best predictor of the present. The BoM-share table is the cleaner lens.

## Caveats
- Pre-presidency talks counted only from 1971+ (dataset start), so earlier tenures (Lee, Kimball) have tiny personal-pre samples (~6 talks).
- Does not control for calling trajectory — older apostles naturally have more talks.
- Nelson effect confounded with CFM, COVID, and broader trends.

Artifacts: `fingerprint_similarity.csv`, `prophet_fingerprints.csv`.
