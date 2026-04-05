"""Does each prophet's pre-presidency personal citation mix pull
conference-wide citations during his presidency?

For each prophet P:
    fp_personal_pre = normalized vector of P's talks BEFORE presidency
    fp_conf_pre    = normalized vector of ALL other talks BEFORE P's presidency start
    fp_conf_during = normalized vector of ALL OTHER speakers' talks during P's presidency

Compute cosine similarity of (personal_pre, conf_during) vs (conf_pre, conf_during).
If former > latter, the prophet "pulled" the body toward his fingerprint.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from analysis._shared.data import BOOKS, load  # noqa: E402
from analysis._shared.prophets import PROPHETS  # noqa: E402

OUT = Path(__file__).parent


def norm_vec(df: pd.DataFrame) -> np.ndarray:
    v = df[BOOKS].sum().to_numpy(dtype=float)
    s = v.sum()
    return v / s if s else v


def cos(a: np.ndarray, b: np.ndarray) -> float:
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    if na == 0 or nb == 0:
        return float("nan")
    return float(np.dot(a, b) / (na * nb))


def ym_key(y: int, m: int) -> int:
    return y * 100 + m


def main() -> None:
    df = load()
    df["ym"] = df["Year"] * 100 + df["Month"]

    rows = []
    for name, sy, sm, ey, em in PROPHETS:
        start = ym_key(sy, sm)
        end = ym_key(ey, em) if ey else 999999

        personal_pre = df[(df["Speaker"] == name) & (df["ym"] < start)]
        conf_pre = df[(df["Speaker"] != name) & (df["ym"] < start)]
        conf_during = df[(df["Speaker"] != name) & (df["ym"] >= start) & (df["ym"] <= end)]

        if len(personal_pre) == 0 or len(conf_during) == 0:
            continue

        fp_personal = norm_vec(personal_pre)
        fp_conf_pre = norm_vec(conf_pre)
        fp_conf_during = norm_vec(conf_during)

        rows.append({
            "prophet": name,
            "n_personal_pre": len(personal_pre),
            "n_conf_during": len(conf_during),
            "cos_personal_vs_during": cos(fp_personal, fp_conf_during),
            "cos_confpre_vs_during":  cos(fp_conf_pre, fp_conf_during),
            "delta": cos(fp_personal, fp_conf_during) - cos(fp_conf_pre, fp_conf_during),
            "personal_bom_share": fp_personal[0],
            "confpre_bom_share":  fp_conf_pre[0],
            "during_bom_share":   fp_conf_during[0],
        })

    results = pd.DataFrame(rows)
    results.to_csv(OUT / "fingerprint_similarity.csv", index=False)
    print(results.to_string(index=False))

    # Also write per-prophet fingerprint vectors
    fps = []
    for name, sy, sm, ey, em in PROPHETS:
        start = ym_key(sy, sm)
        personal_pre = df[(df["Speaker"] == name) & (df["ym"] < start)]
        if len(personal_pre) == 0:
            continue
        vec = norm_vec(personal_pre)
        fps.append({"prophet": name, "n_pre_talks": len(personal_pre),
                    **{b: float(v) for b, v in zip(BOOKS, vec)}})
    pd.DataFrame(fps).to_csv(OUT / "prophet_fingerprints.csv", index=False)


if __name__ == "__main__":
    main()
