# Pre-registration — T-HR (HR-HNL total-shots model)

Frozen: 2026-11-10, before any fitting. Branch `build/hr-hnl`.
Design authority: `analysis/MODEL_DESIGN.md` (T-HR); feature X5; evidence F1/F2.
Reference: the programme shots family as frozen in the J1/CY T engines
(joint home/away log-linear Poisson ratings store, ridge tuned on dev,
lazy refit 7 days, HL = 365; arm A = v1 pattern through the fitted NB
size; arm B = A plus the v2 level layer; arm C = A with the E9
trailing-200-match NB size). The level layer's centre constant is this
league's dev-era total-shots mean, 24.10/match (EDA F1, pooled
2022/2023–2024/2025: (23.900 + 25.017 + 23.372) / 3, equal n per season), frozen here in place of the reference leagues'
own constants.

- Target: total shots = `total_shots_home + total_shots_away` (stats feed;
  definition stable across all seasons — EDA F1).
  Primary line **23.5** (dev over-rate 0.524). Ladder 22.5 / 23.5 / 24.5, gate at 23.5.
- Arms: **A** (v1), **B** (v2 level layer), **C** (E9 trailing-200 r).
- Walk-forward per-match chronological (date, match_id), predict-then-update,
  date-grouped. Warm-up: 2021/2022 updates state, never scored.
- Dev: scored seasons 2022/2023–2024/2025 (n = 540). The dev harness must not
  read 2025/2026 rows at all.
- Baselines: league base rate; naive trailing-10 (through the same probability family as the reference harness).
- Virgin: 2025/2026 (n = 180), read ONCE, only for dev-passing arms.
  Calibration = mean P(over 23.5) − actual rate, SE = sd(p_i − y_i)/√n.

## GATE LEGS (verbatim, frozen)
Dev gate — pooled dev LL at the primary line beats BOTH baselines (league base rate; naive trailing-10), else arm dead, no virgin read. Virgin legs — (i) LL ≤ Gate Zero's (arm A's) and ≤ best baseline's (arm A: ≤ best baseline's); (ii) calibration |mean P(over) − actual| ≤ 1.0pp clean PASS, breach within 1 SE = PROVISIONAL PASS, else FAIL; (iii) dev per-season sign check for both-pass (variant dev LL ≤ arm A's in at least half the dev seasons — ≥2 of 3). Both-pass: lower pooled virgin LL ships; one → ships; none → FAIL. Ties → simpler arm (A before B before C). If arm A fails its dev gate, variants are moot, verdict FAIL, virgin NOT read.

## Outputs
Engine `engine/total_shots/`; `results_dev.json` (+ CSV); `results_virgin.json`;
`fitted_params_virgin.json`; on PASS, `predictions/t_hr_virgin_predictions.csv`
(FT ladder + 1H/2H presentation via frozen total-shots constant 0.4661). Verdict `reports/T_HR_VERDICT.md`.
