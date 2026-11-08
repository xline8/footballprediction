# Exploratory data analysis — HU-NBII

All figures below are recomputed from `data/hu_nbii_matches.csv`; 2026/27 is
tallied descriptively only and is not virgin evaluation.

## F1 — finished-only levels

| season | n | goals | goals/match | home win | draw | away win | OU2.5 | SE | BTTS |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2025/26 | 96 | 232 | 2.417 | 38.5% | 27.1% | 34.4% | 44.8% | 5.1pp | 47.9% |
| 2026/27 | 104 | 301 | 2.894 | 47.1% | 22.1% | 30.8% | 55.8% | 4.9pp | 53.8% |
| pooled | 200 | 533 | 2.665 | 43.0% | 24.5% | 32.5% | 50.5% | 3.5pp | 51.0% |

The previously quoted 2025/26 levels based on 137 scored rows were contaminated
by partial captures; they are not league levels and are not used here.

## F2 — home advantage

Finished-only home-win/draw/away-win rates are shown in F1. The pooled home-win
rate is 43.0% against 32.5% away wins, with 24.5% draws; this is descriptive,
not a fitted home parameter.

## F3 — halves

No half constant is frozen: there is no gateable window and no period-market
source. Among 189 finished matches with a `Half` marker, first-half event goals
are 234 out of 533 final-score goals, or 43.9%. The chart compares this
descriptive value with the J1 reference 0.412 only; it is not adopted.

## F4 — team traits

Chronologically split each team's finished-season matches into two halves and
correlate GF/game across the 16 teams. Pearson r is 0.075 for 2025/26 and
0.186 for 2026/27. Both are noise-level with roughly 8–15 matches per team in
the first season and 13 per team in the second. The brief's approximate 0.10
and 0.25 are corrected here by the finished-only calculation.

## F5–F8 — target and quality checks

- F5 SOT, corners, cards, and total shots: stats and shotmap targets are absent
  in 344/344 payloads. The 47 total card events are not a usable cards target.
- F6 referee: `infoBox.Referee.text` is blank in 344/344.
- F7 X2: the five identified transition cases are recorded in
  DATA_UNDERSTANDING; the usable NB-II mover evidence is too small and there
  is no development window, so X2 is dropped.
- F8: 103 missing-score 2025/26 fetches and 41 partial 2025/26 captures form
  the fetch-wave defect. They are excluded, never repaired as 0-0.
