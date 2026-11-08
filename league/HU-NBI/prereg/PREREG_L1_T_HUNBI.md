# Pre-registration — L1-T-HU-NBI (HU-NBI total shots, Lane 1 re-entry)

**Lane 1 status.** This is a NEW candidate under the improvement
program charter (`league/IMPROVEMENT_PROGRAM.md`, Lane 1), entered
from the wave-1 cohort report
(`league/improvement_scratch/LANE1_WAVE1/cohort_report.md`
§2.2/§2.5, Cohort B). The original candidate T-HU-NBI failed at
the DEV gate (`reports/T_HU_VERDICT.md`: FAIL (dev), virgin
deliberately NOT read). Its sealed window was never read and
remains genuinely sealed. This preregistration is committed
BEFORE any sealed access; one read, verdict final, no iteration
against the window after the read.

**Method differences, stated in advance (the ONLY differences).**
Two corrections, fixed together in the same corrected run, as the
cohort report requires:

- (a) **M_BAR correction (AUDIT.md §5.9).** The shipped engine ran
  arms B/C with `M_BAR = 24.9` in `engine/total_shots/model.py` —
  J1's dev mean, copied with the template — while the original
  prereg (`prereg/PREREG.md`, coordinator correction) documents
  this league's own level at 19.0425. The distortion is +5.86
  shots, 31% above the league's true level, the largest M_BAR
  distortion in the audit. The corrected method derives M_BAR
  from this league's own dev data (below) and wires it into the
  model's LevelLayer / TrailingR. The copied 24.9 is FORBIDDEN.
- (b) **Naive-baseline correction (AUDIT.md §5.12).** The shipped
  `run_t_hu.py` scored the naive trailing-10 baseline from arm
  B's blended probabilities, so B's self-comparison was vacuous
  (B pooled LL ≡ shipped "naive" LL to full printed precision,
  0.7057836266832629) and A/C faced a stronger-than-frozen
  comparator. The corrected evaluation uses the TRUE naive
  trailing-10 baseline: the trailing-10 total alone through the
  same NB machinery as arm A (NB size r = 40.0, the shipped arm-A
  size) — i.e. `nb_over(naive_total, 40.0, 19.5)`, where
  `naive_total` is the NaiveTracker total (each team's plain
  trailing-10 mean shots for/against, combined
  (for + opponent-against)/2 per side, league-mean fallback).
  It is NOT any arm's blended probability.

Nothing else changes: same arms, same machinery, same league
base rate, same gate legs as `prereg/PREREG.md`.

## Derived constant (P5, gate_lib)

- Constant: `M_BAR` (level prior for arm B's level layer and arm
  C's trailing-r estimator).
- Derivation: `league/gate_lib/constants.py` `derive_level_prior`
  — the pooled mean of total shots per match
  (`total_shots_h + total_shots_a`) over the SCORED dev seasons
  2022/2023, 2023/2024 and 2024/2025, rows with both total-shots
  fields present (n = 588, sum = 11197.0). This is exactly the
  definition behind the original prereg's documented dev mean:
  "dev means … total shots 19.0425" (recomputed pre-fitting from
  the committed `hu_nbi.csv`; the warm-up season 2021/2022 is
  loaded for walk-forward state but is not part of this mean,
  as in the original prereg's dev-mean statement).
- **Derived value: M_BAR = 19.0425** (full precision
  19.042517006802722).
- The copied value 24.9 is FORBIDDEN in this candidate. Any other
  template constant is used exactly as the shipped engine froze
  it (ridge lambda 100.0, arm-A/C NB base size r_a = 40.0,
  trailing-r window k = 200 and clip [20, 400], level-layer cell
  CELLS[0] = (30.0, 0.5, 20.0), BASE_HL 365, refit 7 days).

## Arms of record and comparators

- **Arms of record: arm C (E9 trailing-r) and corrected arm B
  (v2 level layer), both reported** — per cohort report §2.5 for
  this candidate. Both read M_BAR; either may ship under this
  preregistration (both-pass rule below).
- Arm A (v1 pattern, the original Gate Zero) never touches
  M_BAR, so its numbers reproduce the shipped run exactly; it is
  retained as a comparator only and cannot ship under this
  preregistration. The original prereg's tie rule "Gate Zero
  ships" and any variant-mootness on arm A's failure do NOT
  apply to this Lane 1 candidate — that is the gate-architecture
  feature this re-entry exists to correct (cohort §2.5 point 3).
  Arms B/C are judged on their own numbers.
- Baselines (harness, not models):
  - league base rate: for target season S, P(over 19.5) = the
    over-19.5 rate of all matches in seasons strictly before S
    (the shipped, uncorrupted definition; pooled shipped LL
    0.6956 stands as the comparator figure).
  - naive trailing-10: the TRUE naive defined in correction (b)
    above. The shipped "naive" figure 0.7058 (= arm B) is
    corrupted and does NOT stand.

## Target and data

- Target: total shots per match = `total_shots_h + total_shots_a`
  (the feed's own `total_shots` key; HU levels are low vs other
  leagues — the key evidently counts a narrower shot definition;
  it is consistent across all seasons).
- Scope: every row with both total-shots fields present, sorted
  by (date, match_id). One chronological walk-forward pass;
  every state updates only AFTER the match is predicted.
  Warm-up: season 2021/2022 updates state but is never scored;
  scored dev seasons 2022/2023, 2023/2024, 2024/2025 (n = 588:
  198 / 193 / 197).

## Frozen line and ladder

- **Primary line: 19.5**
- All gate legs judged at 19.5 only (binary log-loss, natural
  log).

## Dev protocol

- Scored dev: seasons 2022/2023–2024/2025 (n = 588). The dev
  harness must not read 2025/2026 or 2026/2027 rows at all
  (enforced via `league/gate_lib/`'s sealed guard: dev loading
  asserts no sealed rows; P2 design seal applies to every
  artefact produced).
- Metric: mean binary log-loss at line 19.5, per season and
  pooled, per arm and per baseline, computed via
  `league/gate_lib/` metrics.
- The corrected dev evaluation reports shipped vs corrected
  numbers side by side, including the corrected naive baseline.
  The full frozen legs are applied via gate_lib — NOT the
  shipped `results_dev.json` gate flags, which omit the
  per-season leg (AUDIT.md §5.12).
- If NEITHER arm of record passes the dev gate, the candidate
  dies at dev: verdict FAIL (dev), the sealed window is NOT
  read. If at least one passes, only the passing arm(s) of
  record proceed to the sealed read.

## Virgin protocol

- Virgin window: virgin_primary: 2025/2026 (n = 198) — the
  original candidate's virgin season per `config.yaml` and
  `prereg/PREREG.md` — read **ONCE**, only if at least one arm
  of record passes the dev gate, after the dev-pass token is
  recorded via `league/gate_lib/` (`record_dev_pass`) and the
  window is loaded through the gate_lib sealed loader
  (`load_sealed_rows`). The walk-forward continues from the dev
  run's end state (all dev-era rows as prior state).
- Virgin metrics per arm: LL@19.5; calibration via gate_lib =
  predicted − actual (mean P(over 19.5) − actual over-19.5
  rate), in percentage points, SE = sd(p_i − y_i)/√n reported.
  (The original prereg stated actual − predicted; gate_lib's
  single convention predicted − actual is used here, so the
  reported sign is the reverse of the original's — the absolute
  breach, which is what leg (ii) judges, is unchanged.)

## GATE LEGS (identical to PREREG.md, frozen)

Dev gate — pooled dev LL@19.5 beats BOTH baselines (league base rate; naive trailing-10), plus the per-season sign check: LL improvement over EACH baseline must be positive in EVERY scored development season (2022/2023, 2023/2024, 2024/2025), else arm dead, no virgin read. Virgin legs — (i) LL@19.5 beats the best baseline (strictly lower than the lowest virgin baseline LL@19.5); (ii) calibration |mean P(over 19.5) − actual| ≤ 1.0 pp is clean PASS, breach beyond 1.0 pp within 1 SE = PROVISIONAL PASS, otherwise FAIL; sign check as stated in the dev gate (it is a dev leg, applied at the dev gate). Both-pass: among passing arms of record, lower pooled virgin LL ships; tie goes to the simpler arm (B before C); one passing → ships; none → FAIL.

Reading: an arm of record passes iff it survives the full dev
gate (pooled + per-season sign check, both baselines, every
season) AND passes virgin legs (i)–(ii) (PROVISIONAL counts on
leg (ii), recorded as such). Verdict labels: all legs clean →
CLEAN PASS; leg (ii) provisional with (i) passed → PROVISIONAL
PASS; otherwise FAIL. If an arm passes, it ships (subject to
runner-join preparation on this branch; no merge under this
preregistration). Arm A cannot ship under this preregistration
regardless of its numbers.

## Reporting requirements

- P6 worst-fold: the verdict reports the worst dev season's legs
  (worst by the reference arm A at the primary line) beside the
  pooled legs — information only, no gate change.
- P2 seal: all artefacts produced under this preregistration are
  computed on dev-era seasons only until the single sealed read;
  the verdict states the prereg commit hash and the dev-pass
  token record.
- Verdict: `reports/VERDICT_L1_T_HUNBI.md`, with shipped vs
  corrected dev numbers (including the corrected naive) and, if
  read, every sealed leg.

## Forbidden

The copied constant 24.9 anywhere in this candidate's runs; the
shipped corrupted naive (= arm B) anywhere as a baseline; any
arm beyond A/B/C; any constant search on this corpus; any
second sealed read; half-share shot modelling (total shots are
FT-only; halves share is null in this league).

Production code and data are untouched. No push. No merge.
