# Stage A — EDA: USA USL League One

All headline values below come from `eda_summary.json` or the verified brief.
Playoffs are excluded from the fitting/scoring analysis; 2026 is inventory
only. The regular model corpus is 867 matches (2021–25); dev is 2022–24,
n=489, and virgin is 2025, n=210.

## Findings

**F1 — Levels and home advantage.** Regular-season goals by year are
2.625, 2.739, 2.979, 2.932, and 2.843. Home advantage is 0.315, 0.279,
0.188, 0.205, and 0.376. SOT is 8.377 / 8.091 / 8.476 / 9.223 / 8.143;
corners 9.066 / 8.964 / 9.848 / 9.362 / 9.071; total shots 24.491 /
24.261 / 24.890 / 25.492 / 24.367. Broken 2021–22 yellow values are not
treated as levels; valid yellows are 4.780 (2023), 5.344 (2024), and 5.029
(2025). The levels chart therefore omits yellows.

**F2 — Cards are a feed artefact.** Stats yellows average 0.88 with 79.8%
zero in 2021 and 1.49 with 71.8% zero in 2022. Event yellow means are 0.00
in every season 2021–25. From 2023 the valid stats means are plausible, with
zero-share 6.6% / 7.2% / 0.5% in 2023–25. The frozen target is stats yellows
where `cards_target_valid` is true.

**F3 — Dispersion.** Variance/mean is 1.057 for goals, 1.246 SOT, 1.139
corners, 1.312 shots, and 0.931 valid-frame yellows.

**F4 — Trait reliability is mixed.** Thirty-repetition split-half results
are goals-for −0.019 (noise), goals-against 0.528, SOT-for 0.118,
corners-for 0.158, shots-for 0.462, box-touches-for 0.388,
box-touches-against 0.516, big-chance-for 0.309, and yellow-for 0.498
(2023+ rows, 18 teams for cards). The goals-for noise result does not remove
the program-required Gate Zero DC reference pattern.

**F5 — Territorial correlations support an arm, not a replacement.**
Corners correlate 0.469 with box touches and 0.299 with possession, n=928
team rows. Box-touch coverage rises 30.5% in 2023 to 100% in 2025, so the
arm needs a minimum-8 trailing rule and Gate Zero fallback.

**F6 — Referee strictness is an arm.** Split-half r=0.379 at the ≥10-match
threshold, across 13 referees and 496 valid regular card matches in 2023–25.
Only one referee reaches ≥20 matches, so the sibling ≥20 screen is not
estimable; X8 is adopted as an arm with the ≥10 evidence.

**F7 — Halves constants are presentation-only.** For consistency-filtered
2023–25 rows, frozen first-half shares are goals 0.468 (n=480), SOT 0.465,
corners 0.469, shots 0.461 (each n=517), and yellows 0.373 (n=482).
True share variance is ≤0 for goals/SOT/corners/yellows and +0.00068 for
shots, approximately noise. Splits are nearly absent in 2021–22; no halves
model is used.

**F8 — Dev line screen.** Pooled dev over-rates are OU 2.5: 0.556, SOT
8.5: 0.464, corners 9.5: 0.423 and 8.5: 0.577, cards 4.5: 0.607 and
5.5: 0.406, and total shots 24.5: 0.497. Corners 8.5 and 9.5 are exactly
equidistant from 0.5; program convention keeps 9.5. Cards chooses 5.5
because |0.406−0.5|=0.094 versus |0.607−0.5|=0.107.

**F9 — Windows.** Warm-up is 2021; dev is 2022–24 (cards 2023–24, cold
start at the 2023 opener because no earlier valid card target exists);
virgin is 2025; 2026 is reserved/transitional.
