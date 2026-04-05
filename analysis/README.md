# Scripture Citation Analyses

Twelve analyses of the General Conference citation dataset (1971–2025, 4,217 talks, 574 speakers). Each lives in its own numbered folder with a runnable `run.py`, a `findings.md`, and supporting CSVs.

Run any analysis from the repo root:
```bash
python analysis/01_curriculum_effect/run.py
```

## Analyses

| # | Folder | Question | Headline finding |
|---|---|---|---|
| 01 | `01_curriculum_effect` | Does the year's book-of-study bump citations? | Null pre-2019; **+3.5 pp BoM** lift in BoM-curriculum years since CFM (2020, 2024) |
| 02 | `02_bom_challenges` | Do BoM reading challenges move citations? | **Benson 1986 +4.6 pp, Hinckley 2005 +5.2 pp** in ±4 conf window; Nelson 2018 null at the margin (ceiling) |
| 03 | `03_prophet_fingerprint` | Does a prophet's pre-presidency style pull the body? | **Benson (+14.8 pp) and Nelson (+9.2 pp)** — their BoM-heavy fingerprints were mirrored in conference during their tenures |
| 04 | `04_speaker_decomposition` | Composition vs behavior? | Speaker FE R²=0.33 vs Year FE R²=0.13 → BoM rise is mostly a **generational handoff**. Ringleaders: Bednar (44 %), Renlund (47 %), Christofferson, Nelson |
| 05 | `05_speaker_clustering` | Citation "schools" among speakers? | 4 clean clusters: Restoration-centric (Benson/Eyring/Nelson), BoM+NT (Oaks/Ballard/Holland), Bible-centric (Monson/Hinckley), mid-century D&C+NT (Faust/Kimball) |
| 06 | `06_first_talk` | Does a debut predict long-run style? | Moderate signal (r = 0.37 for BoM share); mean cos(debut, rest) = 0.71. McConkie & Petersen are the biggest drifters |
| 07 | `07_session_slot` | April vs October, session order effects? | Null — April and October are citation-twins; position proxy too coarse |
| 08 | `08_christ_centering` | Is conference more Christ-centered over time? | **NT+BoM share rose 44 % → 68 %** (1980 → 2023). Entirely BoM-driven until ~2020 |
| 09 | `09_verse_adjusted_divergence` | Raw vs verse-adjusted style? | **Deferred** — parquet lacks verse-adjusted columns |
| 10 | `10_change_points` | Where are the structural breaks? | BoM: 1983 (Kimball pre-Benson), 1999 (Hinckley revival), 2016 (Nelson lead-up). NT: 2021-10 surge (+8 pp) |
| 11 | `11_prophet_handoff` | Abrupt or gradual transitions? | **No eulogy effect**. Benson transition +12 pp BoM, Nelson +3.5 pp — both immediate. Post-Benson dropoff -6 pp |
| 12 | `12_scripture_diversity` | Are talks getting mono-book? | **Within-talk entropy up (1.06 → 1.45); between-talk aggregate entropy slightly down**. Modern talks are individually more diverse but collectively more BoM-centered |

## Cross-analysis themes

1. **Benson is the pivot.** Nearly every analysis identifies 1985-86 as the structural break where the BoM dimension of conference citations undergoes a step-change (analyses 02, 03, 04, 08, 10, 11).
2. **The BoM rise is compositional, not behavioral.** Analyses 04 and 05 show it is a generational handoff — new apostles like Bednar, Renlund, and Christofferson are BoM-forward, and they increasingly own conference airtime.
3. **Nelson extends, rather than starts, the BoM emphasis.** By his 2018 ascension, BoM share was already 38 %. His personal fingerprint reinforces the existing trajectory (analyses 02, 03, 11).
4. **Curriculum effects exist only post-CFM (2019+)** and only for BoM (analysis 01), and are likely confounded with Nelson-era emphasis.
5. **Christ-centering (NT+BoM)** is at an all-time high (~68 %) — not because of NT expansion but because BoM has replaced D&C and OT share (analysis 08).

## Shared modules
- `analysis/_shared/data.py` — data loader with Year/Month normalization, conference labels, BoM list, and per-conference / per-year aggregators.
- `analysis/_shared/prophets.py` — prophet tenure table for 1971+.

See `TODO.md` for the original plan.
