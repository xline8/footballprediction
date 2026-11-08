# Model design

## Candidate feasibility

G-UYSEG is the only candidate. S is not buildable because no SOT target exists in any payload; C is not buildable because no corners target exists; T is not buildable because no total-shots target exists; K is not buildable because there are zero plain Yellow events and only rare Red/YellowRed events, about 0.44 dev card events per finished match in dev, which the production cards design excludes.

## G-UYSEG

Reference is the production Dixon–Coles `model_v2.py` pattern: goals-only observation, `hl=270`, rho grid, and fitted home advantage. Arms are Gate Zero; SHRINK, which multiplies attack and defence ratings by `n/6` for teams with 1–5 prior in-league matches and leaves unseen teams at the mean; and X2, which applies the frozen cumulative relegated-mover offsets in `eda_summary.json` before each target season. The X2 offsets are computed only from transitions completed before that target season; 2022 has none, 2023 uses 2022, 2024 uses 2022–2023, and 2025 uses 2022–2024.

Training is season-blocked walk-forward: 2021 is the seed (85 finished), evaluation is 2022–2025 (`n=863`), and 2026 is the virgin (`n=218`) transitional season. The 2026 read is reserved until completeness is confirmed and is not performed in this design step.

The dev gate requires pooled 1X2 log loss and RPS to beat climatology and OU2.5 log loss to beat the base-rate baseline. Virgin legs are the LL leg, pooled home-win and OU2.5 calibration within 1.0 percentage point (within 1 SE is provisional), and a per-season sign check for variants; both-pass rule applies. Gate Zero failure makes variants moot and leaves virgin unread. Halves are FT plus 1H/2H presentation using only the frozen goals 1H constant 0.433; no other halves constants exist.
