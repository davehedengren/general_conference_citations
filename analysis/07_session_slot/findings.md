# 07 — Session / Slot Effects

**Question.** Do April vs. October conferences differ? Do early-in-conference talks differ from late-in-conference?

**Method.** Month-level aggregation (April=4, October=10) and within-conference quartile by URL-sort position (rough session-order proxy — URL sort is alphabetic within conference, so this is *noisy*).

## April vs October

| month | n | cites/talk | BoM | D&C | PGP | NT | OT |
|---|---:|---:|---:|---:|---:|---:|---:|
| April   | 2111 | 11.22 | 29.9 % | 24.2 % | 5.1 % | 30.5 % | 10.4 % |
| October | 2106 | 11.70 | 30.7 % | 24.1 % | 5.8 % | 29.0 % | 10.4 % |

Effectively **identical** — the two annual conferences show no systematic citation-mix difference. October talks are slightly denser in citations (11.7 vs 11.2 per talk).

## Within-conference position (alphabetic proxy, noisy)

Across four quartiles, BoM share drifts 30.7 % → 31.6 % → 29.0 % → 29.9 % and NT 29.3 % → 29.5 % → 29.6 % → 30.5 %. Differences within ~1-2 pp; **nothing material**.

## Takeaway
No meaningful session or position effect in the aggregate. If session ordering matters, the true session order (Sat AM vs Sun PM) would need to be extracted from URL metadata — our alphabetic proxy is too coarse to detect prestige-slot effects.

Artifacts: `by_month.csv`, `by_quartile.csv`.
