# Verdict — K-AT2 (Austria 2. Liga cards, event yellows)

**FAIL — at the dev gate. Virgin window NOT read.**

## Dev (walk-forward; scored 2022/2023–2024/2025, n = 720, LL @ 4.5)

| arm | LL @ 4.5 |
|---|---|
| Gate Zero | 0.688079 |
| league base rate | 0.681079 |
| naive trailing-10 | 0.691114 |

Per-season LL: 0.705478 / 0.694211 / 0.664547. Gate Zero beats the
naive baseline but **loses to the league base rate** (0.688079 >
0.681079) → **dev gate FAIL**. Gate Zero is the only registered
arm (X8 referee arm impossible: referee coverage is 0.0% in this
league). Verdict FAIL; season 2025/2026 was **not read** by this
candidate. Nothing ships.

Reading: event-yellows traits are the weakest of the count traits
here (split-half r = 0.445 for / 0.574 against, EDA F2) and the
league's card level is high and stable (4.7–5.5 per match), so the
base rate is a hard baseline: the ratings add per-match variance
without beating the pooled rate on log-loss. Consistent with the
cards pattern across the program (referee-less cards arms rarely
clear their gates).

Target note (frozen in PREREG_K_AT2 before fitting): the target
is event-unified yellows (Yellow + YellowRed) because the stats
feed carries no cards key in any payload — the stats-vs-events
artefact check is moot in this league, as in RU-1.

Coordinator notes: pooled LLs recomputed independently from
`engine/cards/predictions_dev.csv` (720 rows); match the harness
to 6dp.
