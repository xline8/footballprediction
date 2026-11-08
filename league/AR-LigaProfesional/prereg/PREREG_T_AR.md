# Pre-registration — T-AR (Liga Profesional total shots model)

**Provenance, stated plainly.** This candidate's design family
(total shots) is under a frozen prospective trial on the top-5: the
v2 design and the E9 challenger are frozen there, verdict due at
n ≥ 1,200 scored top-5 matches or the end of the 2026/27 season —
NOT reached. T-AR is built now, ahead of that verdict, under the
user's standing order for this program (J.League design §6 override,
applied program-wide by the conveyor mandate), on the Liga Profesional
corpus only. The top-5 prospective trial is not touched; different
corpus, different virgin window, no shared fitting.

Frozen: 2026-11-09, before any fitting. Branch `build/ar-liga`.
Design authority: `league/AR-LigaProfesional/analysis/MODEL_DESIGN.md` §5;
levels per `EDA.md` (total shots mean ≈ 24.4 pooled, dispersion
1.35; shots-for split-half r = 0.747). Reference implementation:
the shots family as ported in `league/J1/engine/total_shots/`
(arms A/B/C frozen there from `experiments/shots_model/` v1, the
v2 level layer, and the E9 trailing-r mechanism).

## Target and data

- Target: total shots per match = `total_shots_home +
  total_shots_away` (stats feed), present for all matches.
- Scope: every regular-season row, sorted by (date, match_id).
  One chronological walk-forward pass; every state (regression,
  naive tracker, base-rate tracker, level layer, trailing-r
  window) updates only AFTER the match is predicted. Warm-up:
  block 2021 updates state but is never scored; scored dev
  blocks 2022, 2023, 2024, 2025 - Apertura, 2025 - Clausura,
  2026 - Apertura (n = 1,854).

## Frozen line and ladder

Dev distribution (blocks 2021 – 2026 - Apertura, n = 2,179,
measured pre-freeze): mean 24.15, median 24.0. Over-rates:
22.5 → 58.3%, 23.5 → 51.8%, 24.5 → 44.7%.

- **Primary line: 23.5** — the ladder line whose dev over-rate is
  closest to 50%.
- Ladder (reported, all arms and baselines): 22.5 / 23.5 / 24.5.
- All gate legs are judged at the primary line 23.5 only (binary
  log-loss, natural log, on P(over 23.5)).

## Arms (all share the J1 port's machinery, constants frozen there)

1. **Arm A (v1 pattern)** — joint ridge Poisson team ratings
   (lambda grid and solver exactly as `league/J1/engine/total_shots/model.py`),
   NB size from the method-of-moments residual estimate on the fit
   window, final probability = 0.5 · NB_over(model total) +
   0.5 · NB_over(naive trailing-10 total). Arm A is this
   candidate's Gate-Zero-equivalent reference arm.
2. **Arm B (v2 pattern)** — Arm A plus the v2 level layer (the
   port's frozen level-layer mechanism, fitted on pre-match data
   only).
3. **Arm C (E9 mechanism)** — Arm A with the NB size replaced by
   the E9 trailing-r estimate (league-level trailing window over
   the most recent 200 scored matches' residuals, single-league
   analogue exactly as T-J1 froze it).

No constant is re-searched for this league; the port's frozen
values (ridge grid, HL = 365, refit cadence 7 days, M_BAR as the
port defines it for its corpus — replaced here by this league's
dev mean 24.15 only where the port takes the corpus mean as an
input constant, which is a data input, not a tuned parameter) are
used as-is.

## Baselines (harness, not models)

- **League base rate**: for target block S, P(over 23.5) = the
  over-23.5 rate of all matches in blocks strictly before S.
- **Naive trailing-10**: the trailing-10 total alone through the
  same NB machinery (arm A's MoM r).

## Dev protocol

- Scored dev: blocks 2022 – 2026 - Apertura (n = 1,854). The dev
  harness must not read block "2026 - Clausura" rows at all.
- Metric: mean binary log-loss at line 23.5, per block and pooled,
  per arm and per baseline.

## Virgin protocol

- Virgin window: block "2026 - Clausura" (n = 240), read **ONCE**, only
  for arms that pass the dev gate, after dev results are frozen.
  The walk-forward continues from the dev run's end state.
- Virgin metrics per arm: LL@23.5; calibration = mean P(over 23.5)
  − actual over-23.5 rate, SE = sd(p_i − y_i)/√n reported.

## GATE LEGS (verbatim, frozen)

Dev gate — pooled dev LL@23.5 beats BOTH baselines (league base rate; naive trailing-10), else arm dead, no virgin read. Virgin legs — (i) LL@23.5 ≤ Arm A's and ≤ best baseline's; (ii) calibration |mean P(over 23.5) − actual| ≤ 1.0pp, SE reported, breach within 1 SE = PROVISIONAL PASS; (iii) dev per-block sign check for both-pass. Both-pass: both → lower pooled virgin LL ships; one → ships; none → FAIL.

Reading: leg (iii) = variant's (B/C) dev LL@23.5 ≤ Arm A's in at
least half the dev blocks (≥ 3 of 6); Arm A exempt. An arm passes
iff it survives the dev gate AND passes virgin (i)–(ii)
(PROVISIONAL counts, recorded as such) AND, for variants, (iii).
Across passing arms: lowest pooled virgin LL@23.5 ships; ties go to
the simpler arm (A before B before C). If no arm passes, T-AR
verdict is FAIL, nothing ships.

## Forbidden

Half-share shot modelling (F3 — halves via the frozen constant
0.462 in presentation only); any arm beyond A/B/C; any constant
search on this corpus.

## Outputs

- Engine: `league/AR-LigaProfesional/engine/total_shots/`.
- Dev results: `league/AR-LigaProfesional/engine/total_shots/results_dev.json` (+ CSV).
- Virgin results: `league/AR-LigaProfesional/engine/total_shots/results_virgin.json`.
- Fitted parameters: `league/AR-LigaProfesional/engine/total_shots/fitted_params.json`.
- Virgin predictions:
  `league/AR-LigaProfesional/predictions/t_ar_virgin_predictions.csv` —
  the shipped arm's predictions (Arm A's if nothing ships,
  labelled in the verdict): match_id, date, teams, actual total
  shots, exp_shots_total, FT ladder P(over 22.5/23.5/24.5), and
  1H/2H ladders derived presentation-only via the frozen shots
  constant 0.462 from the same expected total and NB machinery.
- Verdict: `league/AR-LigaProfesional/reports/T_AR_VERDICT.md`.

Production code and data are untouched. No push. No merge.
