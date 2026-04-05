"""k-means clustering of speakers by their normalized 5-book citation fingerprint.

Filter to speakers with >= 10 talks (stable fingerprints) and >= 20 total citations.
Report cluster centers and the highest-prolific speakers per cluster.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from analysis._shared.data import BOOKS, load  # noqa: E402

OUT = Path(__file__).parent
K = 4
MIN_TALKS = 10
MIN_CITES = 20


def main() -> None:
    df = load()
    g = df.groupby("Speaker").agg(
        n_talks=("Title", "count"),
        bom=("bom", "sum"), dc=("dc", "sum"), pgp=("pgp", "sum"),
        nt=("nt", "sum"), ot=("ot", "sum"),
    )
    g["total"] = g[BOOKS].sum(axis=1)
    g = g[(g["n_talks"] >= MIN_TALKS) & (g["total"] >= MIN_CITES)].copy()
    X = g[BOOKS].to_numpy(dtype=float)
    X = X / X.sum(axis=1, keepdims=True)

    km = KMeans(n_clusters=K, n_init=20, random_state=42)
    labels = km.fit_predict(X)
    g["cluster"] = labels
    for i, b in enumerate(BOOKS):
        g[f"share_{b}"] = X[:, i]

    centers = pd.DataFrame(km.cluster_centers_, columns=BOOKS)
    centers["cluster"] = range(K)
    centers["size"] = [(labels == c).sum() for c in range(K)]
    centers.to_csv(OUT / "cluster_centers.csv", index=False)
    print("Cluster centers (normalized shares):")
    print(centers.to_string(index=False))

    # Speakers per cluster, top by talks
    g = g.sort_values(["cluster", "n_talks"], ascending=[True, False])
    g.to_csv(OUT / "speakers_by_cluster.csv")
    print("\nTop 5 by talks in each cluster:")
    for c in range(K):
        sub = g[g["cluster"] == c].head(5)
        print(f"\n-- cluster {c} (n={len(g[g['cluster']==c])}) --")
        cols = ["n_talks", "share_bom", "share_dc", "share_pgp", "share_nt", "share_ot"]
        print(sub[cols].to_string())


if __name__ == "__main__":
    main()
