# 09 — Verse-Adjusted vs Raw Divergence (Deferred)

**Status.** Deferred. The loaded parquet has only raw citation counts:
`bom, dc, pgp, nt, ot`. The README promises verse-adjusted counts, but
those columns are not present in `conference_talks_2026-01.parquet`.

**Proposed method when columns are added.**
For each talk compute `divergence_b = rank(verse_adj_b) − rank(raw_b)` across all talks.
Speakers with consistently large gap have a "verse-density" signature —
either citing many short verses (raw >> verse-adj) or citing long passages
(verse-adj >> raw).

**To enable this analysis:** extend `download.py` to emit columns like
`bom_verses, nt_verses, ...` and rerun.
