# Pre-registration — T-NO-OBOS (NO-OBOSLigaen total-shots model)

Frozen: 2026-11-10, before any fitting. Branch `build/no-obos`.
Provenance: built ahead of the top-5 total-shots prospective verdict
by the same user order recorded for T-J1 (MODEL_DESIGN §5); different
corpus, different virgin window, no shared fitting — the top-5 trial
is untouched and neither result contaminates the other.
Design authority: `MODEL_DESIGN.md` §5; features per `FEATURES.md`
(X5); evidence per `EDA.md` (F2/F9; dispersion 2.03). Reference: the
shots family via the NO-Eliteserien engine
`league/NO-Eliteserien/engine/total_shots/`.

## Target and lines
- Target: total shots = `total_shots_home + total_shots_away`.
  **Primary line 20.5** (dev over-rate 48.28% — the ladder line
  closest to 50%; dev mean 20.9). Ladder 19.5 / 20.5 /
  21.5. All gate legs use binary LL at 20.5.
- Rows without the stats keys (1 in dev, 3 in the virgin season) are
  skipped by scoring, never imputed (PREPROCESSING rule 5).
- Recorded caveat: the feed's counting regime jumped in 2024 (F9);
  the tuning/dev windows span both regimes and the virgin sits in
  the new one. Consumed as recorded, no correction.

## Arms (exactly the J1 engine's methods, retargeted)
1. **Arm A (v1 pattern)** — ratings + NB + naive ensemble, NB r
   fitted on the tuning window by the J1 engine's frozen method.
2. **Arm C (E9 trailing-r)** — Arm A with the NB r taken from a
   trailing window (league-level trailing r), the J1 engine's E9
   method unchanged. (The v2 level-layer arm B of T-J1 is not run
   here: two arms bound the comparison to the dispersion question
   this league's EDA raises — shots dispersion 2.03, the highest of
   any OBOS market.)
The J1 engine's tuning-season / gate-pool split is retargeted:
tuning season 2022, gate pool = scored dev seasons 2023 + 2024 +
2025 pooled for the dev gate (2022 reported, not gated — it is the
tuning season, exactly as T-J1/T-NO treated theirs).

## Baselines
League base rate (prior-seasons over-20.5 rate) and naive
trailing-10 through the same NB machinery, as the J1 engine
computes them.

## Dev protocol
Warm-up 2021; tuning 2022; scored gate pool 2023 + 2024 + 2025
(n=719 with target). Dev harness must not read 2026 rows.
**Dev gate (this candidate's reading of the shared legs)**: pooled
gate-pool LL@20.5 beats BOTH baselines. The per-season sign check
(leg iii) is read on the three gate-pool seasons.

## Virgin protocol
Season 2026 (complete regular season, n=240; 237 with target), read
ONCE, only for arms passing the dev gate, walk-forward continuing
from the dev end state. Calibration = mean P(over 20.5) − actual
over-rate, SE reported.

## GATE LEGS (verbatim, frozen — identical across the program)

Dev gate — pooled dev LL at the primary line beats BOTH baselines (league base rate; naive trailing-10 / climatology), else arm dead, no virgin read. Virgin legs — (i) LL ≤ Gate Zero's and ≤ best baseline's; (ii) calibration |mean P(over) − actual| ≤ 1.0pp, SE reported, breach within 1 SE = PROVISIONAL PASS; (iii) dev per-season sign check for both-pass (variant dev LL ≤ Gate Zero's in at least half the dev seasons; Gate Zero exempt). Both-pass: both → lower pooled virgin LL ships; one → ships; none → FAIL. Ties → simpler arm (Gate Zero first). If Gate Zero fails its own dev gate, the variants are moot — verdict FAIL regardless of variant dev numbers, and the virgin window is not read.

(With the dev-gate reading above substituted for the pooled-dev
wording: gate pool = 2023 + 2024 + 2025; sign check over those three
seasons, at least half = 2 of 3. For this candidate "Gate Zero" in
leg (i) reads as arm A, the v1 reference pattern.)

## Forbidden
Halves modelling — **this market is FT-only** (no halves source
exists, F3; no halves ladders are produced); absence features;
snapshot features; any distribution family outside the shots family's
NB pattern.

## Outputs
- Engine: `league/NO-OBOSLigaen/engine/total_shots/`;
  `results_dev.json` (+ CSV), `results_virgin.json`,
  `fitted_params.json`.
- Virgin predictions: `league/NO-OBOSLigaen/predictions/t_no_obos_virgin_predictions.csv`
  (shipped arm; arm A labelled if nothing ships): match_id, date,
  teams, actual total shots, exp_shots_total, FT ladder P(over
  19.5/20.5/21.5). FT only — no halves ladders.
- Verdict: `league/NO-OBOSLigaen/reports/T_NO_OBOS_VERDICT.md`.
