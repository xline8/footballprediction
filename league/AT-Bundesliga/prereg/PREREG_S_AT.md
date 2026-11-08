# Pre-registration — S-AT (AT-Bundesliga shots-on-target model)

Frozen: 2026-11-09, before any fitting. Branch `build/at-bundesliga`.
Design authority: `MODEL_DESIGN.md` §2; features per `FEATURES.md`
(X5 base; X4 arm; X6 DROPPED — F7); evidence per `EDA.md` (F6/F7).
Reference: production `model_sot.py` v5 via the J1 engine
`league/J1/engine/sot/` (model.py copied; constants unchanged).

Scope: predictions-only (no AT SOT odds source in-system).

## Target and lines
- Target: total SOT = `ShotsOnTarget_home + ShotsOnTarget_away`
  (stats feed). **Primary line 8.5** (dev over-rate 48.2%). Ladder
  7.5 / 8.5 / 9.5. All gate legs use binary LL at 8.5.

## Reference architecture — v5, frozen constants (all arms share)
Exactly as PREREG_S_J1: joint ridge Poisson (lambda_ridge=100,
HL=365d, 7-day lazy refit, eta clip [−6, 4]); venue-split decayed
total-shots ratings shrunk with prior K=8; Beta-Binomial on-target
ratio (P=200); per-team exp = 0.5·regression + 0.5·implied-shots;
ensemble 0.5·NB(model) + 0.5·NB(naive trailing-10); NB size
r = 79.94 frozen (v5 value, not re-estimated).

## Walk-forward protocol
Per-match predict-then-update, chronological (date, match_id).
Warm-up: 2021/2022 matches update state but are never scored.
Scored dev: 2022/2023–2024/2025 (n=585). Dev harness must not read
2025/2026 or 2026/2027 rows at all.

## Arms
1. **Gate Zero (GZ)** — v5 pattern unmodified.
2. **Arm RS (ratio-shrink)** — GZ with the BB prior raised P=200 →
   **P=20,000** (tests F6: team SOT-rate trait NOISE, r=−0.114).
3. **Arm X4 (xG/shot quality input)** — GZ with the BB ratio replaced
   by `ratio_X4 = rho_venue · (q_team / q_league)` clamped
   [0.15, 0.50], q = Σ sm_xg / Σ sm_shots over trailing 25 shotmap
   matches (min 8, else GZ BB fallback), q_league expanding —
   constructed exactly as S-J1's X4 arm.
No X6 arm exists for this league (F7: xGOT trait r=0.273 — dropped).

## Baselines
League base rate (prior-seasons over-8.5 rate, constant within a
season) and naive trailing-10 through the same NB (r=79.94).

## Virgin protocol
Season 2025/2026 (n=195), read ONCE, only for dev-passing arms,
walk-forward continuing from the dev end state. Calibration =
mean P(over 8.5) − actual over-rate, SE = sd(p_i − y_i)/√n.

## GATE LEGS (verbatim, frozen — identical across the program)

Dev gate — pooled dev LL at the primary line beats BOTH baselines (league base rate; naive trailing-10 / climatology), else arm dead, no virgin read. Virgin legs — (i) LL ≤ Gate Zero's and ≤ best baseline's; (ii) calibration |mean P(over) − actual| ≤ 1.0pp, SE reported, breach within 1 SE = PROVISIONAL PASS; (iii) dev per-season sign check for both-pass (variant dev LL ≤ Gate Zero's in at least half the dev seasons; Gate Zero exempt). Both-pass: both → lower pooled virgin LL ships; one → ships; none → FAIL. Ties → simpler arm (Gate Zero first). If Gate Zero fails its own dev gate, the variants are moot — verdict FAIL regardless of variant dev numbers, and the virgin window is not read.

## Forbidden
As PREREG_S_J1: absence features; trailing conversion/finishing/
on-target-rate form features (standalone rate covariate is R4);
halves modelling (presentation via frozen constant 0.447 only);
two-stage generative distributions; defensive xGOT; snapshots.

## Outputs
- Engine: `league/AT-Bundesliga/engine/sot/`; `results_dev.json`
  (+ CSV), `results_virgin.json`, `fitted_params_virgin.json`.
- Virgin predictions: `league/AT-Bundesliga/predictions/s_at_virgin_predictions.csv`
  (shipped arm; GZ labelled if nothing ships): match_id, date, teams,
  actual total SOT, exp_sot_home/away/total, FT ladder P(over
  7.5/8.5/9.5), 1H/2H ladders presentation-only via frozen constant
  0.447 with NB r=79.94 (1H lines 2.5/3.5/4.5; 2H lines 3.5/4.5/5.5).
- Verdict: `league/AT-Bundesliga/reports/S_AT_VERDICT.md`.
