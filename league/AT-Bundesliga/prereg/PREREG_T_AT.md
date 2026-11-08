# Pre-registration — T-AT (AT-Bundesliga total-shots model)

Frozen: 2026-11-09, before any fitting. Branch `build/at-bundesliga`.
Provenance: built ahead of the top-5 total-shots prospective verdict
by the same user order recorded for T-J1 (MODEL_DESIGN §5); different
corpus, different virgin window, no shared fitting — the top-5 trial
is untouched and neither result contaminates the other.
Design authority: `MODEL_DESIGN.md` §5; features per `FEATURES.md`
(X5); evidence per `EDA.md` (F2; dispersion 1.24). Reference: the
shots family via the J1 engine `league/J1/engine/total_shots/`.

## Target and lines
- Target: total shots = `total_shots_home + total_shots_away`.
  **Primary line 24.5** (dev over-rate 50.1%). Ladder 23.5 / 24.5 /
  25.5. All gate legs use binary LL at 24.5.

## Arms (exactly the J1 engine's methods, retargeted)
1. **Arm A (v1 pattern)** — ratings + NB + naive ensemble, NB r
   fitted on the tuning window by the J1 engine's frozen method.
2. **Arm C (E9 trailing-r)** — Arm A with the NB r taken from a
   trailing window (league-level trailing r), the J1 engine's E9
   method unchanged. (The v2 level-layer arm B of T-J1 is not run
   here: two arms bound the comparison to the dispersion question
   this league's EDA raises — shots dispersion 1.24, the highest of
   any AT market.)
The J1 engine's tuning-season / gate-pool split is retargeted:
tuning season 2022/2023, gate pool = scored dev seasons 2023/2024 +
2024/2025 pooled for the dev gate (2022/2023 reported, not gated —
it is the tuning season, exactly as T-J1 treated its 2022).

## Baselines
League base rate (prior-seasons over-24.5 rate) and naive
trailing-10 through the same NB machinery, as the J1 engine
computes them.

## Dev protocol
Warm-up 2021/2022; tuning 2022/2023; scored gate pool 2023/2024 +
2024/2025 (n=390). Dev harness must not read 2025/2026 or 2026/2027
rows. **Dev gate (this candidate's reading of the shared legs)**:
pooled gate-pool LL@24.5 beats BOTH baselines. The per-season sign
check (leg iii) is read on the two gate-pool seasons.

## Virgin protocol
Season 2025/2026 (n=195), read ONCE, only for arms passing the dev
gate, walk-forward continuing from the dev end state. Calibration =
mean P(over 24.5) − actual over-rate, SE reported.

## GATE LEGS (verbatim, frozen — identical across the program)

Dev gate — pooled dev LL at the primary line beats BOTH baselines (league base rate; naive trailing-10 / climatology), else arm dead, no virgin read. Virgin legs — (i) LL ≤ Gate Zero's and ≤ best baseline's; (ii) calibration |mean P(over) − actual| ≤ 1.0pp, SE reported, breach within 1 SE = PROVISIONAL PASS; (iii) dev per-season sign check for both-pass (variant dev LL ≤ Gate Zero's in at least half the dev seasons; Gate Zero exempt). Both-pass: both → lower pooled virgin LL ships; one → ships; none → FAIL. Ties → simpler arm (Gate Zero first). If Gate Zero fails its own dev gate, the variants are moot — verdict FAIL regardless of variant dev numbers, and the virgin window is not read.

(With the dev-gate reading above substituted for the pooled-dev
wording: gate pool = 2023/2024 + 2024/2025; sign check over those
two seasons, at least half = 1 of 2 — a variant must not lose both.)

## Forbidden
Halves modelling (presentation via frozen constant 0.454 only);
absence features; snapshot features; any distribution family outside
the shots family's NB pattern.

## Outputs
- Engine: `league/AT-Bundesliga/engine/total_shots/`;
  `results_dev.json` (+ CSV), `results_virgin.json`,
  `fitted_params.json`.
- Virgin predictions: `league/AT-Bundesliga/predictions/t_at_virgin_predictions.csv`
  (shipped arm; arm A labelled if nothing ships): match_id, date,
  teams, actual total shots, exp_shots_total, FT ladder P(over
  23.5/24.5/25.5), 1H/2H ladders presentation-only via frozen constant
  0.454 with the arm's NB r (1H lines 9.5/10.5/11.5; 2H lines
  11.5/12.5/13.5).
- Verdict: `league/AT-Bundesliga/reports/T_AT_VERDICT.md`.
