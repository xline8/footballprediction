# Pre-registration — T-NLE (Eerste Divisie total shots model)

**Provenance, stated plainly.** This candidate's design family
(total shots) is under a frozen prospective trial on the top-5: the
v2 design and the E9 challenger are frozen there, verdict due at
n ≥ 1,200 scored top-5 matches or the end of the 2026/27 season —
NOT reached. T-NLE is built now, ahead of that verdict, under the
user's standing order for this program (J.League design §6
override, applied program-wide by the conveyor mandate), on the
Eerste Divisie corpus only. The top-5 prospective trial is not
touched; different corpus, different virgin window, no shared
fitting.

Frozen: 2026-11-09, before any fitting. Branch `build/nl-eerste`.
Design authority: `league/NL-EersteDivisie/analysis/MODEL_DESIGN.md`;
levels per `EDA.md` (dev total shots mean 26.019; shots-for
split-half r = 0.879). Reference implementation: the shots family
as ported in `league/NL-Eredivisie/engine/total_shots/` (arms A/B/C
frozen there from `experiments/shots_model/` v1, the v2 level
layer, and the E9 trailing-r mechanism).

## Target and data

- Target: total shots per match = `total_shots_home +
  total_shots_away` (stats feed), present for all matches.
- Scope: every regular-season row, sorted by (date, match_id).
  One chronological walk-forward pass; every state (regression,
  naive tracker, base-rate tracker, level layer, trailing-r
  window) updates only AFTER the match is predicted. Warm-up:
  season 2021/2022 updates state but is never scored; scored dev
  seasons 2022/2023, 2023/2024, 2024/2025 (n = 1140).

## Frozen line and ladder

Dev distribution (seasons 2021/2022–2024/2025, n = 1520, measured
pre-freeze): mean 26.019, median 26. Over-rates: 24.5 → ~57%,
25.5 → 50.79%, 26.5 → 43.68%.

- **Primary line: 25.5** — the ladder line whose dev over-rate is
  closest to 50%.
- Ladder (reported, all arms and baselines): 24.5 / 25.5 / 26.5.
- All gate legs are judged at the primary line 25.5 only (binary
  log-loss, natural log, on P(over 25.5)).

## Arms (all share the reference port's machinery, constants frozen there)

1. **Arm A (v1 pattern)** — joint ridge Poisson team ratings
   (lambda grid and solver exactly as
   `league/NL-Eredivisie/engine/total_shots/model.py`), NB size
   from the method-of-moments residual estimate on the fit window,
   final probability = 0.5 · NB_over(model total) +
   0.5 · NB_over(naive trailing-10 total). Arm A is this
   candidate's Gate-Zero-equivalent reference arm.
2. **Arm B (v2 pattern)** — Arm A plus the v2 level layer (the
   port's frozen level-layer mechanism, fitted on pre-match data
   only).
3. **Arm C (E9 mechanism)** — Arm A with the NB size replaced by
   the E9 trailing-r estimate (league-level trailing window over
   the most recent 200 scored matches' residuals, single-league
   analogue exactly as T-J1/T-NL froze it).

No constant is re-searched for this league; the port's frozen
values are used throughout.

## Baselines (harness, not models)

- **League base rate**: for target season S, P(over 25.5) = the
  over-25.5 rate of all matches in seasons strictly before S
  (constant within S).
- **Naive trailing-10**: the naive total alone, scored through the
  same NB machinery as Arm A's naive term.

## Dev protocol

- Scored dev matches: seasons 2022/2023, 2023/2024, 2024/2025
  (n = 1140), walk-forward as above. The dev harness must not read
  season "2025/2026" or "2026/2027" rows at all.
- Metric: mean binary log-loss at line 25.5, per season and pooled,
  per arm and per baseline.

## Virgin protocol

- Virgin window: season "2025/2026" (n = 380), read **ONCE**, only
  for arms that pass the dev gate, after dev results are frozen.
  The walk-forward continues from the dev run's end state.
- Virgin metrics per arm: LL@25.5; calibration = **actual over-25.5
  rate − mean P(over 25.5)**, SE = sd(y_i − p_i)/√n reported.

## GATE LEGS (verbatim, frozen)

Dev gate — pooled dev LL@25.5 beats BOTH baselines (league base rate; naive trailing-10), else arm dead, no virgin read. Virgin legs — (i) LL@25.5 ≤ Arm A's and ≤ best baseline's; (ii) calibration |actual − predicted| ≤ 1.0pp, SE reported, breach within 1 SE = PROVISIONAL PASS; (iii) dev per-season sign check vs Arm A for both-pass. Both-pass: passing arms → lowest pooled virgin LL ships; one → ships; none → FAIL.

Reading of the legs, fixed here so the verdict is mechanical:

- The "best baseline" in virgin leg (i) is the lower-LL of the two
  baselines scored on the virgin window.
- Leg (iii): for arms B and C, dev LL@25.5 ≤ Arm A's dev LL@25.5
  in at least half of the dev seasons (≥ 2 of 3). Arm A is exempt.
- An arm *passes* iff it survives the dev gate AND passes virgin
  legs (i)–(ii) (PROVISIONAL PASS counts, recorded as such) AND,
  for arms B/C, leg (iii).
- Both-pass rule across all passing arms: the lowest pooled virgin
  LL@25.5 ships; ties go to the simpler arm (A before B before C).
  If no arm passes, T-NLE verdict is FAIL and nothing ships.
- Design NOT-built clause: if Arm A fails its own dev gate, arms
  B/C are moot — verdict FAIL regardless of their dev numbers, and
  the virgin window is not read.

## Forbidden

Half-share modelling (halves via the frozen constant 0.451 in
presentation only); post-match snapshots; any constant search on
this corpus.

## Outputs

- Engine: `league/NL-EersteDivisie/engine/total_shots/`.
- Dev results: `engine/total_shots/results_dev.json` (+ CSV).
- Virgin results: `engine/total_shots/results_virgin.json`.
- Fitted parameters: `engine/total_shots/fitted_params.json`.
- Virgin predictions (shipped arm only, on PASS):
  `league/NL-EersteDivisie/predictions/t_nle_virgin_predictions.csv`
  — one row per 2025/2026 match with actual total shots, expected
  total, FT ladder P(over 24.5/25.5/26.5), and 1H/2H ladders
  derived presentation-only via the frozen total-shots constant
  0.451 (1H lines 11.5/12.5/13.5, 2H lines 12.5/13.5/14.5). Halves
  are never fitted.
- Verdict: `league/NL-EersteDivisie/reports/T_NLE_VERDICT.md`.

Production code and data are untouched. No push. No merge.
