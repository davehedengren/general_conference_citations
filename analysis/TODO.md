# Scripture Citation Analyses — TODO / Plan

Dataset: `conference_talks_2026-01.parquet` — 4,217 talks, 574 speakers, 1971–2025.
Columns: `Title, Speaker, URL_Suffix, Full_URL, Year, Month, talk_html_filepath, bom, dc, pgp, nt, ot, filename`.

Each analysis lives in its own numbered folder under `analysis/` with:
- `run.py` — the script
- `findings.md` — written findings + tables
- `*.csv` / `*.png` — supporting artifacts

## Status

- [x] 01_curriculum_effect — Does the year's Sunday-School / Come-Follow-Me book of study predict a bump in conference citations the following session?
- [x] 02_bom_challenges — ITS around Benson 1986, Hinckley 2005, Nelson 2017/2018 BoM-reading invitations.
- [x] 03_prophet_fingerprint — Does each prophet's pre-presidency personal citation mix pull conference-wide citations during his presidency?
- [x] 04_speaker_decomposition — Year-FE vs Speaker-FE decomposition of the BoM rise; identify ringleaders.
- [x] 05_speaker_clustering — k-means on normalized 5-vectors; do cluster assignments differ by calling/era?
- [x] 06_first_talk — Scripture distribution of each speaker's debut talk vs their steady-state.
- [x] 07_session_slot — Month (April vs October) and year-position effects on citation mix.
- [x] 08_christ_centering — NT+BoM share over time as a Christ-centering index; find inflection points.
- [x] 09_verse_adjusted_divergence — (Deferred — current parquet lacks verse-adjusted columns; documented.)
- [x] 10_change_points — Bayesian/greedy change-point detection per book; compare to known events.
- [x] 11_prophet_handoff — 2-conference window around presidency transitions; eulogy effect test.
- [x] 12_scripture_diversity — Shannon entropy of the 4-book mix (PGP excluded) per talk / per year; is conference getting more mono-book?

## Cross-cutting conventions

- All scripts are idempotent and runnable from the repo root: `python analysis/NN_*/run.py`.
- Each script loads data via `analysis/_shared/data.py` which normalizes Year/Month as ints and attaches a `Date` and `Conference` label (`YYYY-MM`).
- Prophet tenure dates kept in one place: `analysis/_shared/prophets.py`.
- Findings files include: question, method, key numbers, caveats.
