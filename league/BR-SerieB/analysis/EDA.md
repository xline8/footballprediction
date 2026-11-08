# Phase 3 — EDA: Brazil Série B (2021–2026 partial)

Computed from `brb_matches.csv`; 60 random career-pooled split halves use a
minimum of 24 matches per team. Virgin 2025 is descriptive only.

## Levels

| season | goals | SOT | corners | stats yellows | target yellows | shots | xG |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2021 | 2.17 | 7.89 | 10.45 | 1.20 | — | 25.82 | — |
| 2022 | 2.02 | 7.66 | 10.21 | 1.20 | — | 26.06 | — |
| 2023 | 2.10 | 8.04 | 10.25 | 5.06 | 5.06 | 26.52 | — |
| 2024 | 2.19 | 8.25 | 10.46 | 5.11 | 5.11 | 26.00 | — |
| 2025 | 2.22 | 8.35 | 10.18 | 4.92 | 4.92 | 27.26 | 2.22* |
| 2026 partial | 2.35 | 8.57 | 10.74 | 4.55 | 4.55 | 28.20 | 2.37* |

*xG only exists in 2025 (380) and 2026 (369), so it is not a dev level.*
Pooled home/away goals are 1.28/0.89: home win/draw/away win = 47.1%/28.9%/24.1%.
Dispersion (variance/mean) is goals 0.923, SOT 1.076, corners 1.142, shots
1.267, and valid-era yellows 1.045. The apparent 2021–2022 card collapse is a
feed break, not a football conclusion.

## Findings and reliability

- Half-share noise test on complete splits 2023–2025 found no excess variance.
  Frozen ratio-of-sums constants are goals .455, SOT .467, corners .472, shots
  .473, yellows .352. Constants are presentation only.
- Career split-half r: goals-for .361, SOT-for .395, corners-for .406,
  shots-for .543, box-touches-for .586, valid yellows-for .262. xG-for is
  .374 on 2025+ only. Referee yellow-rate r is .397 across 20 referees with
  at least 20 valid matches. These are weaker than Série A in several traits,
  so gates matter.
- Set-play share and xG/shot are measurable only in 2025+ (the virgin era);
  they are not eligible dev evidence. xG calibration on the 2025 covered
  season is close to one (goals/xG ≈ 1.00), but is design-level evidence only.
- Movers are four ex-A and four ex-C clubs per transition. The X2 analysis
  compares each club's first B season with its prior A/C season and the B
  season mean; offsets are estimated inside dev only. Across the five
  transitions, ex-A first-B GF/GA averages are 1.19/1.01 versus 0.93/1.55
  in their prior A seasons; ex-C first-B GF/GA averages are 1.03/1.12 versus
  1.21/0.87 in their prior C seasons. The direction is not uniform club by
  club, but the tier step is large enough to justify a two-sided, separately
  parameterised arm. The largest thin-data exposure is eight movers per
  season, supporting the sanctioned SHRINK arm. Examples include Bahia,
  Sport Recife, Grêmio, Criciúma, Tombense and Ituano in 2022; Santos,
  América-MG, Goiás, Coritiba, Paysandu and Brusque in 2024; and Sport,
  Ceará, Fortaleza, Náutico, São Bernardo, Londrina and Ponte Preta in 2026.

## Feasibility

Goals, SOT, corners, and total shots are complete for all windows. Cards are
feasible only on 2023–2025 onward. xG-dependent arms are not dev-feasible.
All five candidates can run, with era guards and the preregistered baseline
gates described in MODEL_DESIGN.md.
