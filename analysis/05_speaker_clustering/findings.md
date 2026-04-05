# 05 — Speaker Clustering by Scriptural Fingerprint

**Question.** Do speakers fall into distinct "schools" of scripture citation?

**Method.** k-means (k=4) on normalized 5-book citation vectors, filtered to speakers with ≥10 talks and ≥20 total citations (73 speakers). Seed = 42.

## Cluster centers

| cluster | BoM | D&C | PGP | NT | OT | n | shorthand |
|---|---:|---:|---:|---:|---:|---:|---|
| 0 | **35 %** | **32 %** | 7 % | 17 % | 9 %  | 15 | Restoration-centric (BoM + D&C) |
| 1 | 14 % | 18 % | 7 % | **45 %** | **17 %** | 18 | Bible-centric |
| 2 | 14 % | **35 %** | 8 % | 31 % | 12 % | 15 | D&C + NT (mid-era) |
| 3 | 33 % | 21 % | 4 % | **32 %** | 9 %  | 25 | BoM + NT balanced |

## Exemplars

- **Cluster 0 — Restoration-centric:** Eyring, Nelson, Packer, Benson, Richard G. Scott. The "Benson school."
- **Cluster 1 — Bible-centric:** **Monson (50 % NT)**, Hinckley, Kimball, Haight, Hunter, Marvin Ashton. Older-generation Bible-forward homilists.
- **Cluster 2 — D&C + NT mid-century:** Faust, Romney, N. Eldon Tanner, McConkie, Victor L. Brown.
- **Cluster 3 — BoM + NT balanced:** Oaks, Ballard, Perry, Uchtdorf, Holland. Modern apostolic mainstream.

## Takeaways
- Cluster assignment cleanly tracks **era** — Cluster 1 is dominated by pre-2010 presidents; Clusters 0 & 3 are modern.
- Benson, Eyring, and R. G. Scott form a distinct **BoM+D&C heavy** camp (Cluster 0) that is very different from the Hinckley/Monson Bible-forward camp (Cluster 1).
- Holland is an NT outlier *within* the modern cluster (NT share ≈ 42 %).
- Two modern presidents (Nelson, Eyring) sit in the same cluster as Benson — a structural echo of the Benson fingerprint in the current First Presidency.

Artifacts: `cluster_centers.csv`, `speakers_by_cluster.csv`.
