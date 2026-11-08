# Step 3 — EDA: Indonesia Super League (regular season only)

## Levels by season

| season | n | goals | home−away goals | stats n | yellows* | SOT† | corners† | total shots† |
|---|---|---|---|---|---|---|---|---|
| 2021/2022 | 306 | 2.412 | −0.059 | 140 | 4.09 | 10.05 | 9.88 | 19.46 |
| 2022/2023 | 306 | 2.761 | +0.474 | 306 | 4.48 | 9.24 | 9.94 | 17.05 |
| 2023/2024 | 306 | 2.879 | +0.454 | 153 | 5.34 | 9.02 | 10.44 | corrupt |
| 2024/2025 | 306 | 2.611 | +0.186 | 8 | 4.32 | — | — | — |
| 2025/2026 | 306 | 2.797 | +0.366 | 0 | 4.40 | — | — | — |
| 2026/2027‡ | 80 | 2.862 | +0.612 | 0 | 3.71 | — | — | — |

\* on events_complete matches only (267/306/144/281/306/72 per season).
The 2023/2024 yellow mean (5.34) is measured on the Jul–Oct 2023
complete-feed subset only — an early-season slice, not the season.
† on stats rows only. 2023/2024 "total shots" is the corrupted copy of
SOT (Step 1 §4.2) and is not a level. 2024/2025's 8 stats rows are not
a level either (SOT 6.6 on n=8 is small-sample noise).

Notes: goals level (2.4–2.9) sits near the J1/European reference band;
the 2021/2022 dip and its absent home advantage match the Bali bubble
format. Dev-era (2021/2022–2024/2025) base rates: over 2.5 = 0.508,
home win = 0.424. Dev-era yellows: mean 4.455 per match (home 2.126,
away 2.329 — away teams collect more, the usual direction), over 4.5
rate 0.452, over 3.5 rate 0.644 → primary line 4.5.

## Trait reliability (split-half, within team-season, chronological)

Pearson r between first-half-of-season and second-half-of-season team
means, pooled over team-seasons (n = team-seasons with ≥16 matches):

| trait | r | n | read |
|---|---|---|---|
| goals for | 0.356 | 90 | modest signal |
| goals against | 0.407 | 90 | modest signal |
| yellows for | 0.402 | 90 | modest signal |
| yellows against | 0.338 | 90 | modest signal |
| SOT for | 0.287 | 47 | weak (stats era only) |
| corners for | 0.240 | 47 | weak (stats era only) |
| total shots for | 0.850 | 47 | inflated — 2023/2024 values are SOT copies |
| possession for | 0.672 | 47 | strong but era-bound (no virgin-era data) |

All traits are weaker than their J1 counterparts (J1: goals/SOT/
corners/yellows for-traits 0.65–0.80). Expect Gate Zero patterns to
earn less here; the dev gate decides.

## Halves (frozen-constant question)

Per-match 1H share variance vs binomial noise, event-verified regular
matches with at least one goal/card:

- Goals: pooled 1H share 0.4456 (n=1,491 matches with goals); observed
  share variance 0.1128 vs binomial noise 0.1156 → true variance
  ≈ −0.003, i.e. zero. Per-match half share is noise around a league
  constant, replicating the programme-wide finding.
- Yellows: pooled 1H share 0.3765 (n=1,369); observed 0.0732 vs noise
  0.0714 → true variance ≈ +0.002, effectively zero.

But the goals constant itself drifts by season (0.485, 0.462, 0.457,
0.438, 0.407, 0.389) — an era drift, not a per-match signal. Frozen
constants are therefore measured on the recent era only
(2023/2024–2025/2026, event-verified regular matches), presentation
only: **goals 0.434, yellows 0.385**. No team half features (R1).

## Referee

No referee identity exists (Step 1 §2), so no strictness check can be
run. X8 is dropped on data absence, not on a failed reliability test.
