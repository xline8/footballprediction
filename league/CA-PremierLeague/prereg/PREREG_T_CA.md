# Pre-registration — T-CA (CA-PremierLeague total shots model)

**Provenance, stated plainly.** This candidate's design family
(total shots) is under a frozen prospective trial on the top-5:
the v2 design and the E9 challenger are frozen there, verdict due
at n ≥ 1,200 scored top-5 matches or the end of the 2026/27
season — NOT reached. T-CA is built now, ahead of that verdict,
under the user's standing order for this program (J.League design
§6 override, applied program-wide by the conveyor mandate), on
the CA-PremierLeague corpus only. The top-5 prospective trial is
not touched; different corpus, different virgin window, no shared
fitting.

Frozen: 2026-11-10, before any fitting. Branch `build/ca-premier`.
Design authority: `analysis/MODEL_DESIGN.md` (T-CA); levels per
`EDA.md` (total shots mean ≈ 22.9 pooled dev; shots-for split-half
r ≈ 0.24–0.63 by season pair). Reference implementation: the
shots family as ported in `league/J1/engine/total_shots/` (arms
A/B/C frozen there from `experiments/shots_model/` v1, the v2
level layer, and the E9 trailing-r mechanism); AR analogue
`PREREG_T_AR.md`.

## Target and data

- Target: total shots per match = `total_shots_home +
  total_shots_away` (stats feed), present for all matches, with
  no level break across the dev→virgin boundary (dev means
  23.27/21.45/23.16/23.46; virgin 23.68 — EDA).
- Scope: every included regular-season row, sorted by
  (date, match_id). One chronological walk-forward pass; every
  state updates only AFTER the match is predicted. Warm-up:
  season 2021 updates state but is never scored; scored dev
  seasons 2022, 2023, 2024 (n = 336).

## Frozen line and ladder

Dev distribution (seasons 2021–2024 pooled for line choice,
n = 448, measured pre-freeze): over-rates 21.5 → 0.575893,
22.5 → 0.506696, 23.5 → 0.439732.

- **Primary line: 22.5** — closest to 50%.
- Ladder (reported): 21.5 / 22.5 / 23.5.
- All gate legs judged at 22.5 only (binary log-loss, natural log).

## Arms (all share the J1 port's machinery, constants frozen there)

1. **Arm A (v1 pattern)** — joint ridge Poisson team ratings
   (lambda grid and solver exactly as
   `league/J1/engine/total_shots/model.py`), NB size from the
   method-of-moments residual estimate on the fit window, final
   probability = 0.5 · NB_over(model total) + 0.5 · NB_over(naive
   trailing-10 total). Arm A is this candidate's
   Gate-Zero-equivalent reference arm.
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
dev mean only where the port takes the corpus mean as an input
constant, which is a data input, not a tuned parameter) are used
as-is.

## Baselines (harness, not models)

- **League base rate**: for target season S, P(over 22.5) = the
  over-22.5 rate of all matches in seasons strictly before S.
- **Naive trailing-10**: the trailing-10 total alone through the
  same NB machinery (arm A's MoM r).

## Dev protocol

- Scored dev: seasons 2022–2024 (n = 336). The dev harness must
  not read 2025 or 2026 rows at all.
- Metric: mean binary log-loss at line 22.5, per season and
  pooled, per arm and per baseline.

## Virgin protocol

- Virgin window: season 2025 (n = 112), read **ONCE**, only for
  arms that pass the dev gate, after dev results are frozen. The
  walk-forward continues from the dev run's end state.
- Virgin metrics per arm: LL@22.5; calibration = mean P(over 22.5)
  − actual over-22.5 rate, SE = sd(p_i − y_i)/√n reported.

## GATE LEGS (verbatim, frozen)

Dev gate — pooled dev LL@22.5 beats BOTH baselines (league base rate; naive trailing-10), else arm dead, no virgin read. Virgin legs — (i) LL@22.5 ≤ Arm A's and ≤ best baseline's; (ii) calibration |mean P(over 22.5) − actual| ≤ 1.0pp, SE reported, breach within 1 SE = PROVISIONAL PASS; (iii) dev per-season sign check for both-pass. Both-pass: both → lower pooled virgin LL ships; one → ships; none → FAIL.

Reading: leg (iii) = variant's (B/C) dev LL@22.5 ≤ Arm A's in at
least half the dev seasons (≥ 2 of 3); Arm A exempt. An arm passes
iff it survives the dev gate AND passes virgin (i)–(ii)
(PROVISIONAL counts, recorded as such) AND, for variants, (iii).
Across passing arms: lowest pooled virgin LL@22.5 ships; ties go
to the simpler arm (A before B before C). If Arm A fails its own
dev gate, variants are moot, verdict FAIL, virgin NOT read. If no
arm passes, T-CA verdict is FAIL, nothing ships.

## Forbidden

Half-share shot modelling (halves via the frozen constant
0.447807 in presentation only); any arm beyond A/B/C; any constant
search on this corpus.

## Outputs

- Engine: `league/CA-PremierLeague/engine/total_shots/`.
- Dev results: `results_dev.json` (+ CSV); virgin:
  `results_virgin.json`; fitted params: `fitted_params.json`.
- On PASS, virgin predictions:
  `predictions/t_ca_virgin_predictions.csv` — the shipped arm's
  predictions: match_id, date, teams, actual total shots,
  exp_shots_total, FT ladder P(over 21.5/22.5/23.5), and 1H/2H
  ladders derived presentation-only via the frozen shots constant
  0.447807 from the same expected total and NB machinery.
- Verdict: `reports/T_CA_VERDICT.md`.

Production code and data are untouched. No push. No merge.
