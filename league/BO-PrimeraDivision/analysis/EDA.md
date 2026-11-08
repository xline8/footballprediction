# Step 3 — EDA: BO-PrimeraDivision

All calculations are in `eda_compute.py`; results are in `eda_numbers.json` and the committed PNGs.

## Levels and home advantage

Score-derived goals/match are 3.0625 (2021), 2.7988 (2022), 2.7574 (2023), 2.9781 (2024), 3.6208 (2025), and 3.0402 (2026). The stats-era 2025 means are SOT 11.3250, corners 9.6417, total shots 30.0375, and event-unified yellows 6.2292. The 2025 home and away goal means are 2.2583 and 1.3625.

## Split-half reliability

The checklist is computed by chronological odd/even team-match splits, with at least six matches per team. In 2025 (16 teams), the correlations are goals for/against .408/.042, SOT for/against .705/.523, corners for/against .589/.358, yellows for/against .116/.231, total shots for .463, box touches for/against .703/.408, possession .775, and big chances .348. Full season-by-season values are in the JSON. This supports SOT, corners, box touches and possession as plausible traits, while yellow sanctions and big chances are weaker.

Two ratio traits were checked the same way (ratio of sums, 2025, n=16 teams): the on-target rate (SOT/shots) split-half is r=0.613 — a real team trait in Bolivia, unlike J1 where it was noise (r=0.06), so v5's ratio component has signal to work with here and the RS arm is a robustness arm, not a repair. Trailing finishing (goals/shot) is weak at r=0.261 and stays rejected.

## Frozen halves and cross-checks

The frozen ratio-of-sums constants are: goals **0.4323**, n=1,065 positive-goal matches, from 2021–2024 regular event times; SOT **0.4555**, n=240; corners **0.4866**, n=240; total shots **0.4633**, n=240; and event-unified yellows **0.3739**, n=239 positive-card matches. The stats-period yellow cross-check is 0.3980 on the same 239 matches (vs 0.3739 event-unified — a further 2.4pp reason the stats feed is not the cards target). These are presentation constants only and are not fitted or selected on virgin 2026.

Variance decomposition (per-match 1H share, weight = match total; true variance = observed minus binomial noise floor): goals −0.00509 (n=1,065), SOT −0.00059, corners −0.00070, total shots −0.00072 (all n=240, 2025) — at or below the noise floor, so the frozen-constant rule stands for all four. Event-unified yellows show a small positive residual, +0.00399 (n=239, single season): not enough to model per-team half shares, so cards also use the frozen constant; the residual is flagged for recheck at the confirmatory read.

## Referees and artefacts

Referee strictness is not measurable as a dev-era feature: names are absent through 2024 and only 40/240 in 2025. Stats-vs-events yellow totals are 1,324 versus 1,495 in 2025, agreeing exactly in 151 matches; this is why K-BO uses event-unified cards. Score goals and event Goal counts reconcile for all ordinary payloads; the only exception is awarded match 3777008 (0–3 score, zero Goal events), retained as a score-based goal observation. No 2025–2026 event feed lacked Half+Substitution markers (n=0).

## 2025 goals spike

The spike is not a single date artifact. Five-round regular blocks have means 3.050, 3.775, 3.525, 3.175, 3.625, and 4.575 (n=40 each). Monthly values and team totals are in `eda_numbers.json`; December is 4.7188 (n=32). The complete table is retained so this descriptive 2025 virgin aggregate is visible, while it remains excluded from goals fitting and line setting.
