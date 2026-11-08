# Pre-registration — S-US (US-MLS shots-on-target model)

Frozen: 2026-11-09, before any fitting. Branch `build/us-mls`.
Design authority: `league/US-MLS/analysis/MODEL_DESIGN.md` §2; features per
`league/US-MLS/analysis/FEATURES.md` (X5 base; X4 arm; X6 era-guarded arm);
evidence per `league/US-MLS/analysis/EDA.md` (F6/F7). Reference: production
`model_sot.py` v5 via the J1 engine `league/J1/engine/sot/`.

## Target and lines

- Target: total SOT = `ShotsOnTarget_home + ShotsOnTarget_away` in
  `league/US-MLS/data/us_matches.csv` (stats feed). **Primary line 8.5**
  (dev over-rate 0.558). Ladder 7.5 / 8.5 / 9.5. All gate legs use binary LL
  at 8.5.

## Reference architecture — v5, frozen constants (all arms share)

Exactly as PREREG_S_J1: joint ridge Poisson (lambda_ridge=100, HL=365d,
7-day lazy refit, eta clip [−6, 4]); venue-split decayed total-shots ratings
shrunk with prior K=8; Beta-Binomial on-target ratio (P=200); per-team
expectation = 0.5·regression + 0.5·implied-shots; ensemble
0.5·NB(model) + 0.5·NB(naive trailing-10); NB size r = 79.94 frozen.

## Walk-forward protocol

Per-match predict-then-update, chronological (date, match_id). Warm-up 2021
matches update state but are never scored. Scored dev seasons are 2022, 2023,
2024 (n=1532). The dev harness must not read 2025 rows at all; 2025 is read
ONCE only for dev-passing arms. Season 2026 is reserved and its rows must not
be read at all. Regular and playoff matches remain in every window, with phase
flagged rather than filtered.

## Arms

1. **Gate Zero (GZ)** — v5 pattern unmodified.
2. **Arm RS (ratio-shrink)** — GZ with the BB prior raised P=200 → 20,000
   (tests F6: team SOT-rate trait noise, r=−0.114).
3. **Arm X4 (xG/shot quality input)** — GZ with the BB ratio replaced by
   `ratio_X4 = rho_venue · (q_team / q_league)` clamped [0.15, 0.50], where
   q is Σ sm_xg / Σ sm_shots over trailing 25 shotmap matches (minimum 8,
   otherwise GZ BB fallback), and q_league is expanding; constructed exactly
   as S-J1's X4 arm.
4. **Arm X6 (xGOT, era-guarded)** — X4 as its base, plus X6 exactly as S-J1:
   only matches dated **2024-01-01 or later** contribute xGOT sums; for a team,
   `g_t` is Σ sm_xgot / Σ sm_xgot_n over its trailing 25 era-valid matches and
   `g_L` is the expanding league ratio. With minimum 8 era-valid matches,
   `mult_t = clamp(1 + 0.5·(g_t/g_L − 1), 0.85, 1.15)` scales attacking
   expected SOT only; otherwise the X4 value is used. Outside the era or
   without data, X6 ≡ X4 exactly. This is the weakest adopted trait (r=0.355)
   and the dev gate decides whether it ships.

## Baselines

League base rate (prior-seasons over-8.5 rate, constant within a season) and
naive trailing-10 through the same NB (r=79.94).

## Dev protocol

Evaluation seasons 2022, 2023, 2024 (n=1532); 2021 is warm-up. The dev harness
must not read 2025 rows at all or any 2026 rows.

## Virgin protocol

Season 2025 (n=540), read ONCE, only for dev-passing arms, walk-forward
continuing from the dev end state. Calibration = mean P(over 8.5) − actual
over-rate, SE reported.

## GATE LEGS (verbatim, frozen — identical across the program)

Dev gate — pooled dev LL at the primary line beats BOTH baselines (league base rate; naive trailing-10 / climatology), else arm dead, no virgin read. Virgin legs — (i) LL ≤ Gate Zero's and ≤ best baseline's; (ii) calibration |mean P(over) − actual| ≤ 1.0pp, SE reported, breach within 1 SE = PROVISIONAL PASS; (iii) dev per-season sign check for both-pass (variant dev LL ≤ Gate Zero's in at least half the dev seasons; Gate Zero exempt). Both-pass: both → lower pooled virgin LL ships; one → ships; none → FAIL. Ties → simpler arm (Gate Zero first). If Gate Zero fails its own dev gate, the variants are moot — verdict FAIL regardless of variant dev numbers, and the virgin window is not read.

For this candidate the "primary line" in the gate text is 8.5 and LL means binary log-loss at 8.5. The X6 arm uses the same era guard beginning 2024-01-01 for its feature construction; its reliability is recorded, but no 2025 rows are read before the dev gate passes.

## Forbidden

As PREREG_S_J1: absence features; trailing conversion/finishing/on-target-rate
form features (standalone rate covariate is R4); halves modelling (presentation
via frozen constant 0.450 only); two-stage generative distributions; defensive
xGOT; snapshots.

## Outputs

- Engine: `league/US-MLS/engine/sot/`; `results_dev.json` (+ CSV),
  `results_virgin.json`, `fitted_params_virgin.json`.
- Virgin predictions: `league/US-MLS/predictions/s_us_virgin_predictions.csv`
  (shipped arm; GZ labelled if nothing ships): match_id, date, teams, actual
  total SOT, exp_sot_home/away/total, FT ladder P(over 7.5/8.5/9.5), 1H/2H
  ladders presentation-only via frozen constant 0.450 with NB r=79.94 (1H
  lines 2.5/3.5/4.5; 2H lines 3.5/4.5/5.5).
- Verdict: `league/US-MLS/reports/S_US_VERDICT.md`.
