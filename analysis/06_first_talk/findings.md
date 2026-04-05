# 06 — First Talk vs. Steady-State Fingerprint

**Question.** Does a speaker's debut conference talk predict his long-run citation mix?

**Method.** For speakers with ≥8 talks (79 speakers), compare the 5-vector of their first talk to the aggregated remainder.

## Results
- **Mean cos(debut, rest) = 0.705**, median 0.729.
- Pearson correlation of **debut BoM-share** vs **steady-state BoM-share = 0.37** (moderate positive).

## Takeaways
- A single debut talk is a **noisy but non-trivial** predictor of a speaker's long-run fingerprint. The typical debut looks like a blurry version of the final style.
- Loudest signal: BoM emphasis debuts tend to persist (r = 0.37).
- Biggest *drifters* from their debut: **Bruce R. McConkie, Mark E. Petersen, Howard W. Hunter** — all had debut talks heavy in a book they subsequently de-emphasized. McConkie debuted 80 % BoM but settled to just 9 %; Petersen debuted 100 % BoM and settled to 13 %.
- **Thomas S. Monson**'s debut was 0 % BoM — consistent with his lifelong NT-forward style; it appears in the "most similar" list precisely because his steady-state is also low-BoM.

## Caveats
- Debut is noisy (single talk, often ~15–20 citations).
- Cosine is dominated by whichever book is most-cited; small counts inflate variance.

Artifact: `debut_vs_steady_state.csv`.
