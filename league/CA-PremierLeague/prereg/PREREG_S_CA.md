# Pre-registration — S-CA (CA-PremierLeague shots-on-target model)

Frozen: 2026-11-10, before any fitting. Branch `build/ca-premier`.
Design authority: `analysis/MODEL_DESIGN.md` (S-CA); features X5
base (FEATURES.md); evidence per `analysis/EDA.md`. Reference:
production `model_sot.py` v5; SK analogue `PREREG_S_SK.md` — the
v5 architecture constants are carried over verbatim (ridge
lambda = 100, HL = 365, lazy refit 7 days, total-shots ratings
prior K = 8, Beta-Binomial prior P = 200, ensemble 50/50 with naive
trailing-10, NB size r = 79.94 frozen). X4/X6 are NOT arms: no
shotmap and no xG exist in this league (data absent, FEATURES).

- Target: total SOT = `ShotsOnTarget_home + ShotsOnTarget_away`
  (stats feed, present 699/699). Primary line **7.5** (dev
  over-rate 0.546875, closest to 0.5). Ladder 7.5 / 8.5 / 9.5
  reported, gate at 7.5.
- Arms: **Gate Zero** (v5 unmodified); **RS** (Gate Zero with the
  BB prior raised P = 200 → 20,000).
- Walk-forward: per-match, chronological (date, match_id),
  predict-then-update, date-grouped (same-date matches never see
  each other). Warm-up: 2021 updates state, never scored.
- Dev: scored seasons 2022–2024 (stats-target n = 336). The dev
  harness must not read 2025 or 2026 rows at all.
- Baselines: league base rate (prior-seasons over-7.5 rate,
  constant per season) and naive trailing-10 through the same NB.
- Virgin: 2025 (stats n = 112), read ONCE, only for dev-passing
  arms, continuing from the dev end state. Calibration = mean
  P(over 7.5) − actual rate, SE = sd(p_i − y_i)/√n.

## GATE LEGS (verbatim, frozen)

Dev gate — pooled dev LL@7.5 beats BOTH baselines (league base rate; naive trailing-10), else arm dead, no virgin read. Virgin legs — (i) LL@7.5 ≤ Gate Zero's and ≤ best baseline's; (ii) calibration |mean P(over 7.5) − actual| ≤ 1.0pp, SE reported, breach within 1 SE = PROVISIONAL PASS; (iii) dev per-season sign check for both-pass. Both-pass: both → lower pooled virgin LL ships; one → ships; none → FAIL.

Mechanical reading: an arm passes iff it survives the dev gate AND
passes virgin legs (i)–(ii) (PROVISIONAL counts) AND, for variants,
leg (iii) — variant dev LL@7.5 ≤ Gate Zero's in at least half of
the dev seasons (≥2 of 3). Ties → simpler arm (Gate Zero before
RS). If Gate Zero fails its dev gate, variants are moot, verdict
FAIL, virgin NOT read.

## Outputs

Engine `engine/sot/`; `results_dev.json` (+ CSV);
`results_virgin.json`; `fitted_params_virgin.json`; on PASS,
`predictions/s_ca_virgin_predictions.csv` (FT ladder 7.5/8.5/9.5
plus 1H/2H presentation-only via frozen SOT constant 0.435196).
Verdict `reports/S_CA_VERDICT.md`.
