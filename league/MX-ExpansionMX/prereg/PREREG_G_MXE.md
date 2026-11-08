# Pre-registration — G-MXE (Mexico Liga de Expansión MX goals model)

Frozen: 2026-11-10, before any fitting. Branch `build/mx-expansion`.
Design authority: `league/MX-ExpansionMX/analysis/MODEL_DESIGN.md`
(G-MXE); features per `analysis/FEATURES.md` (X1 DROPPED — no xG
exists in the modelling corpus, so the observation is goals-only;
X2 DROPPED — no promotion/relegation flow with Liga MX exists,
measured overlap 0 in all 10 blocks; altitude R7 REJECTED on this
league's measurement). Reference: production Dixon-Coles in
`model_v2.py` (class `DC`), hl = 270; sibling analogue:
`league/CL-LigaDeAscenso/prereg/PREREG_G_CLA.md` (same goals-only
pattern).
Phase rule (frozen, MODEL_DESIGN): liguilla play-off ties are
**excluded** from every fit and every score. Population rule
(frozen): only `finished = 1 AND phase = regular` rows, tournament
blocks per the frozen date rule (Apertura = 15 Jun – 31 Dec of the
first calendar year; Clausura = 1 Jan – 14 Jun of the second). The
virgin is scored on the 105 finished regular rows of
2025/2026 - Clausura. Calibration is defined as **actual −
predicted** everywhere in this build.

## Reference architecture (all arms share unless an arm says otherwise)

- Dixon-Coles fit, copied pattern from production `model_v2.py`:
  iterative multiplicative updates, 14 sweeps, damping 0.7, +0.25
  smoothing, home advantage fitted (init 0.28), attack/defence per
  team (init 0), score matrix MAXG = 10, production `tau` correction.
- Rho per fit from grid (0.0, −0.05, −0.10, −0.15) by weighted
  log-likelihood on goals only, as production.
- Observation: goals only. (No blend pair can exist here —
  expected_goals is absent from every one of the 1,208
  modelling-corpus payloads.)
- Time decay w = 0.5 ** ((cutoff − match_date).days / 270) — frozen,
  no search.
- Fit scope for target block B: all modelling-population matches
  dated strictly before the first match date of B (expanding,
  tournament-blocked).
- Teams unseen in training start at the league mean (a = d = 0).

## Arms

1. **Gate Zero** — the unmodified reference above.
2. **Arm SHRINK** (sanctioned G-J2-lesson arm) — Gate Zero plus
   exactly one change at prediction time: for a team with fewer
   than 6 prior in-league matches in the training window, its
   fitted attack and defence ratings are shrunk toward the league
   mean: `a *= n/6`, `d *= n/6` where n = its prior in-league match
   count (n = 0 ⇒ a = d = 0, identical to Gate Zero's unseen rule;
   the arm bites exactly for teams with 1–5 prior matches — the
   season-opener failure mode; under tournament-blocked fitting
   that band may not occur, which is itself a recorded finding if
   so). Nothing else changes.

## Dev protocol

- Training seed = 2021/2022 - Apertura (finished regular, n = 136);
  evaluation blocks 2021/2022 - Clausura … 2025/2026 - Apertura
  (pooled scored n = 967) under the tournament-blocked
  walk-forward.
- Metrics per arm per block and pooled: mean 1X2 LL, mean RPS
  (H, D, A), mean OU2.5 LL. Baselines: climatology — for target
  block B, pooled outcome rates + OU2.5 over-rate of all blocks
  strictly before B (modelling population only). Dev OU2.5
  over-rate 0.4933 (primary line 2.5 is the median line).
- The dev harness must not read 2025/2026 - Clausura or
  2026/2027 rows at all.

## Virgin protocol

- Virgin = 2025/2026 - Clausura (n = 105, last complete block),
  read ONCE, only for arms passing the dev gate, after dev results
  are frozen. Fit = all modelling-population matches before the
  first virgin-block match date. Climatology = pooled rates of
  blocks 1–9. Calibration: actual − mean predicted for home-win
  rate and OU2.5 over-rate, SE = sd(y_i − p_i)/√n.
- 2026/2027 - Apertura (in progress) is the reserved confirmatory
  window — never read in this build.

## GATE LEGS (verbatim, frozen)

Dev gate — pooled dev 1X2 LL and RPS must beat climatology, and OU2.5 LL must beat the base-rate baseline, else the arm is dead. Virgin legs — (i) LL leg: arm's virgin 1X2 LL ≤ Gate Zero's AND ≤ climatology's; (ii) calibration leg: |actual − mean predicted| ≤ 1.0pp pooled for home-win rate and for OU2.5 over-rate, SEs reported; a breach within 1 SE of the boundary is recorded PROVISIONAL PASS, beyond it FAIL; (iii) per-block sign check on dev (arm LL ≤ Gate Zero LL in at least half the dev blocks) for the both-pass rule. Both-pass rule: if Gate Zero and a variant both pass all legs, the lower pooled virgin 1X2 LL ships; if only one passes, it ships; if none passes, G-MXE verdict is FAIL and nothing ships.

Mechanical reading: an arm passes iff it survives the dev gate AND
passes virgin legs (i)–(ii) (PROVISIONAL counts, recorded as such)
AND, for variant arms, leg (iii); Gate Zero is exempt from (iii).
Ties go to the simpler arm (Gate Zero before SHRINK). If Gate Zero
fails its own dev gate, variants are moot, verdict FAIL, virgin
NOT read.

## Outputs

Engine `league/MX-ExpansionMX/engine/goals/`; dev results
`results_dev.json` (+ CSV); virgin `results_virgin.json`; fitted
params `fitted_params_virgin.json`; on PASS, virgin predictions
`league/MX-ExpansionMX/predictions/g_mxe_virgin_predictions.csv`
(shipped arm; 1H/2H presentation via frozen goals constant 0.448).
Verdict: `league/MX-ExpansionMX/reports/G_MXE_VERDICT.md`.
Production code untouched. No push. No merge.
