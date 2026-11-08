# Pre-registration — S-NO-OBOS (NO-OBOSLigaen shots-on-target model)

Frozen: 2026-11-10, before any fitting. Branch `build/no-obos`.
Design authority: `MODEL_DESIGN.md` §2; features per `FEATURES.md`
(X5 base; X4/X6 DROPPED — F5/F7); evidence per `EDA.md` (F2/F9).
Reference: production `model_sot.py` v5 via the NO-Eliteserien engine
`league/NO-Eliteserien/engine/sot/` (model.py copied; constants
unchanged).

Scope: predictions-only (no OBOS SOT odds source in-system).

## Target and lines
- Target: total SOT = `ShotsOnTarget_home + ShotsOnTarget_away`
  (stats feed). **Primary line 9.5** (dev over-rate 47.13%). Ladder
  8.5 / 9.5 / 10.5. All gate legs use binary LL at 9.5.
- Rows without the stats keys (1 in dev, 3 in the virgin season) are
  skipped by scoring and never update the target state; they are
  never imputed (PREPROCESSING rule 5).

## Reference architecture — v5, frozen constants (all arms share)
Exactly as PREREG_S_NO: joint ridge Poisson (lambda_ridge=100,
HL=365d, 7-day lazy refit, eta clip [−6, 4]); venue-split decayed
total-shots ratings shrunk with prior K=8; Beta-Binomial on-target
ratio (P=200); per-team exp = 0.5·regression + 0.5·implied-shots;
ensemble 0.5·NB(model) + 0.5·NB(naive trailing-10); NB size
r = 79.94 frozen (v5 value, not re-estimated). The total-shots
ratings read the stats feed's `total_shots` — the only shots input
this league has (no shotmap exists; the pattern does not need one).
Recorded caveat: the feed's counting regime jumped in 2024 (F9); the
pattern consumes the feed as recorded, no correction.

## Walk-forward protocol
Per-match predict-then-update, chronological (date, match_id).
Warm-up: 2021 matches update state but are never scored.
Scored dev: 2022–2025 (n=959 with target). Dev harness must not read
2026 rows at all.

## Arms
1. **Gate Zero (GZ)** — v5 pattern unmodified.
2. **Arm RS (ratio-shrink)** — GZ with the BB prior raised P=200 →
   **P=20,000** (tests how much team ratio variation to keep).
No X4/X6 arms exist for this league (F5/F7: no shotmap — dropped at
the feature step).

## Baselines
League base rate (prior-seasons over-9.5 rate, constant within a
season) and naive trailing-10 through the same NB (r=79.94).

## Virgin protocol
Season 2026 (complete regular season, n=240; 237 with target), read
ONCE, only for dev-passing arms, walk-forward continuing from the dev
end state. Calibration = mean P(over 9.5) − actual over-rate,
SE = sd(p_i − y_i)/√n.

## GATE LEGS (verbatim, frozen — identical across the program)

Dev gate — pooled dev LL at the primary line beats BOTH baselines (league base rate; naive trailing-10 / climatology), else arm dead, no virgin read. Virgin legs — (i) LL ≤ Gate Zero's and ≤ best baseline's; (ii) calibration |mean P(over) − actual| ≤ 1.0pp, SE reported, breach within 1 SE = PROVISIONAL PASS; (iii) dev per-season sign check for both-pass (variant dev LL ≤ Gate Zero's in at least half the dev seasons; Gate Zero exempt). Both-pass: both → lower pooled virgin LL ships; one → ships; none → FAIL. Ties → simpler arm (Gate Zero first). If Gate Zero fails its own dev gate, the variants are moot — verdict FAIL regardless of variant dev numbers, and the virgin window is not read.

## Forbidden
As PREREG_S_J1: absence features; trailing conversion/finishing/
on-target-rate form features (standalone rate covariate is R4);
halves modelling — **this market is FT-only** (no halves source
exists, F3; no halves ladders are produced); two-stage generative
distributions; defensive xGOT; snapshots.

## Outputs
- Engine: `league/NO-OBOSLigaen/engine/sot/`; `results_dev.json`
  (+ CSV), `results_virgin.json`, `fitted_params_virgin.json`.
- Virgin predictions: `league/NO-OBOSLigaen/predictions/s_no_obos_virgin_predictions.csv`
  (shipped arm; GZ labelled if nothing ships): match_id, date, teams,
  actual total SOT, exp_sot_home/away/total, FT ladder P(over
  8.5/9.5/10.5). FT only — no halves ladders.
- Verdict: `league/NO-OBOSLigaen/reports/S_NO_OBOS_VERDICT.md`.
