# 02 — BoM Reading Challenges (Interrupted Time-Series)

**Question.** Do prophet-issued Book of Mormon reading challenges visibly lift BoM citations in the following conferences?

**Method.** ±4-conference window mean BoM-share diff around three shocks:
- **Benson 1986** (shock = 1986-10, "Flooding the Earth with the BoM")
- **Hinckley 2005** (shock = 2005-10, challenge to finish by year-end)
- **Nelson 2018** (shock = 2018-10, BoM immersion invitations)

## Results

| event | pre BoM share | post BoM share | Δ (pp) | pre cites/talk | post cites/talk |
|-------|--------------:|---------------:|-------:|---------------:|----------------:|
| Benson 1986   | 29.9 % | 34.6 % | **+4.6** | 3.37 | 4.50 |
| Hinckley 2005 | 30.4 % | 35.7 % | **+5.2** | 3.43 | 3.97 |
| Nelson 2018   | 38.6 % | 39.1 % | +0.6 | 5.58 | 6.92 |

**Long-horizon Benson.** 4-year pre-shock BoM share (26.1 %) vs. 8-year post-shock (32.6 %) → **+6.6 pp**, suggesting a persistent, not transient, effect.

## Takeaways
- Benson (1986) and Hinckley (2005) challenges each produced a clear **~5 pp** bump in BoM share in the immediate window.
- Nelson (2018) shock looks null *in share terms* — but BoM was already at a post-Benson high (38.6 %), so ceiling effects or ongoing secular trend likely mask the marginal effect. The absolute cites-per-talk did jump (5.58 → 6.92).
- The Benson effect appears **durable** well beyond his own presidency.

## Caveats
- Simple mean-diff; no counterfactual modeling for secular trend.
- Nelson shock window overlaps with CFM rollout (2019) and home-centered emphasis — confounded.
- 4-conference window chosen a priori; sensitivity to window size not tested here.

Artifacts: `challenge_windows.csv`, `bom_share_timeseries.csv`.
