# 05 — Speaker Clustering by Scriptural Fingerprint

**Question.** Do speakers fall into distinct "schools" of scripture citation?

**Method.** k-means (k=4) on normalized 5-book citation vectors, filtered to speakers with ≥10 talks and ≥20 total citations (73 speakers). Seed = 42.

## Cluster centers

| cluster | BoM | D&C | PGP | NT | OT | n | shorthand |
|---|---:|---:|---:|---:|---:|---:|---|
| 0 | **35 %** | **32 %** | 7 % | 17 % | 9 %  | 15 | Restoration-centric (BoM + D&C) |
| 1 | 33 % | 22 % | 4 % | **32 %** | 9 %  | 25 | BoM + NT balanced |
| 2 | 14 % | 17 % | 6 % | **46 %** | **17 %** | 17 | Bible-centric |
| 3 | 14 % | **34 %** | 9 % | 31 % | 12 % | 16 | D&C + NT (mid-era) |

## Exemplars

- **Cluster 0 — Restoration-centric:** Eyring, Nelson, Packer, Benson, Richard G. Scott. The "Benson school."
- **Cluster 1 — BoM + NT:** Oaks, Ballard, Perry, Uchtdorf, Holland. Modern apostolic mainstream.
- **Cluster 2 — Bible-centric:** **Monson (46 % NT)**, Hinckley, Haight, Hunter, Marvin Ashton. Clearly older-generation Bible-forward homilists.
- **Cluster 3 — D&C + NT mid-century:** Faust, Kimball, Romney, N. Eldon Tanner, McConkie.

## Takeaways
- Cluster assignment cleanly tracks **era** — Cluster 2 is dominated by pre-2010 presidents; Clusters 0 & 1 are modern.
- Benson, Eyring, and R. G. Scott form a distinct **BoM+D&C heavy** camp that is very different from the Hinckley/Monson Bible-forward camp.
- Holland is an NT outlier *within* the modern cluster (NT share = 41 %).
- Two modern presidents (Nelson, Eyring) sit in the same cluster as Benson — a structural echo of the Benson fingerprint in the current First Presidency.

Artifacts: `cluster_centers.csv`, `speakers_by_cluster.csv`.
