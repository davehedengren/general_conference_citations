# 10 — Change-Point Detection per Book

**Method.** Recursive binary segmentation (L2 cost) on per-conference book-share series, up to 4 change points per book, min segment length = 6 conferences.

## Detected break points

### BoM
| conf | pre (8) | post (8) | Δ pp | context |
|---|---:|---:|---:|---|
| **1983-10** | 17.2 % | 25.0 % | **+7.9** | Pre-Benson ramp (Kimball BoM emphasis 1982) |
| 1994-04 | 35.9 % | 24.9 % | **−11.1** | Post-Benson dip |
| **1999-10** | 25.8 % | 36.0 % | **+10.2** | Hinckley-era resurgence |
| 2016-10 | 32.3 % | 38.6 % | +6.3 | Pre-Nelson apostolic emphasis |

### NT
| conf | Δ pp |
|---|---:|
| 1985-10 | **−8.0** (coincides with Benson BoM shift) |
| **2021-10** | **+8.3** (CFM NT rotation + Christ-centering) |

### D&C — four moderate oscillations between 21 % and 32 %; no durable break.
### OT — slow decline, main drop 2004-10 (−5 pp).
### PGP — minor (<3 pp) shifts only.

## Takeaways
- The BoM series has **four detected breaks**, clustered around 1983 (Kimball/Benson pivot) and 1999 (mid-Hinckley).
- The biggest unexplained break is **2021-10 NT surge (+8 pp)** — likely the 2023 NT curriculum buildup and Nelson-era Christ-centering.
- OT shows a long, gentle decline rather than a single shock.
- The 1994 BoM dip (−11 pp) aligns with Benson's death (May 1994) and the brief Hunter presidency.

Artifact: `change_points.csv`.
