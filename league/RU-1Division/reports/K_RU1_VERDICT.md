# Verdict — K-RU1 (Russia 1. Division cards, event yellows)

**FAIL at the dev gate. Virgin NOT read. Nothing ships.**

## Dev (n = 918, LL @ 4.5)

| arm | LL @ 4.5 | calibration |
|---|---|---|
| Gate Zero | 0.640449 | −8.26 pp |
| league base | 0.669929 | |
| naive trailing-10 | 0.628969 | |

Per-season LL: 0.697695 / 0.623376 / 0.600278.

Dev gate (verbatim): pooled dev LL@4.5 beats BOTH baselines, else
the candidate is dead, no virgin read. Gate Zero beats the league
base (0.640449 < 0.669929) but loses to naive trailing-10
(0.640449 > 0.628969) — **FAIL**. The virgin is NOT read and
K-RU1 is closed as FAIL.

Context: the event-yellow level fell hard after the seed season
(5.84/match in 2021/2022 → 4.77 → 3.61 → 3.66 in the scored
seasons), and the model's pooled dev calibration is −8.26 pp
(actual − predicted): it systematically over-predicts the
over-4.5 rate in a falling-level regime, while the naive
trailing-10 tracker adapts faster. Target note: the stats feed
carries no yellow_cards in this league at all, so the artefact
question was moot and the target was event yellows by
construction (frozen in the prereg).

All numbers recomputed by the coordinator from
`engine/cards/predictions_dev.csv`. No fitted params, no
predictions.
