# Pre-registration — L1-T-AUW (AU-ALeagueWomen total shots, Lane 1 re-entry)

**Lane 1 status.** This is a NEW candidate under the improvement
program charter (`league/IMPROVEMENT_PROGRAM.md`, Lane 1), entered
from the wave-1 cohort report
(`league/improvement_scratch/LANE1_WAVE1/cohort_report.md`
§2.2/§2.5, cohort B, AUDIT.md §5.9). The original candidate T-AUW
failed at the DEV gate (`reports/T_AUW_VERDICT.md`: FAIL, virgin
NOT read). Its sealed window was never read and remains genuinely
sealed. This preregistration is committed BEFORE any sealed access;
one read, verdict final, no iteration against the window after
the read.

**Method difference, stated in advance (the sole difference).**
AUDIT.md §5.9: the shipped T-AUW engine ran arms B/C with
`M_BAR = 24.9` in `engine/total_shots/model.py` — J1's dev mean,
copied with the template — while this league's own dev mean is
≥27.5 (the primary line 27.5 itself sits at the dev level; the
audit's all-rows carrier example for this league family is 28.1).
The copied constant biased the level prior DOWN against a
higher-scoring league, on exactly the arms that read it; the
binding corrected margins in the original scoring were 0.0015
(arm C) – 0.0020 (arm B) LL against the naive baseline. The
corrected method derives M_BAR from this league's own dev data
(below) and wires it into the model's LevelLayer/TrailingR.
Nothing else changes: same arms, same machinery, same baselines,
same gate legs as `PREREG_T_AUW.md`.

## Derived constant (P5, gate_lib)

- Constant: `M_BAR` (level prior for arm B's level layer and arm
  C's trailing-r estimator).
- Derivation: `league/gate_lib/constants.py` `derive_level_prior`
  — the pooled mean of total shots per match
  (`home_total_shots + away_total_shots`) over ALL loaded dev-era
  rows: warm-up season 2021/2022 plus scored dev seasons
  2022/2023–2024/2025, regular phase only, rows with both shot
  columns present (the shipped harness's loaded set, n = 439).
  Derivation computed on dev-era rows only, before this commit;
  the sealed seasons were not touched.
- **Derived value: M_BAR = 27.678815489749432** (27.6788).
- The copied value 24.9 is FORBIDDEN in this candidate. Any other
  template constant is used exactly as the original prereg froze
  it (regression lambda 30, NB r_A = 40, level cell
  (60, 1.0, 50), trailing-r window k = 200).

## Arm of record and comparators

- **Arms of record: arm B** (v2 pattern: A + level layer) **and
  arm C** (E9: NB r from a trailing window), both with the
  corrected M_BAR = 27.678815489749432, as designated for this
  candidate in the cohort report §2.5. Only arms B and C can ship
  under this preregistration.
- The original prereg designated arm A (v1 pattern) as this
  candidate's Gate Zero / primary reference arm. Arm A never
  touches M_BAR, so its dev FAIL reproduces exactly under
  corrected code; per cohort report §2.5 point (3) it is retained
  as the Gate Zero comparator/baseline only, and the original
  Gate-Zero-veto reading does NOT apply to this Lane 1 candidate.
  Arm A cannot ship under this preregistration.
- Baselines (harness, not models), unchanged from
  `PREREG_T_AUW.md`: league base rate / climatology and naive
  trailing-10, computed exactly as the shipped harness computes
  them (decayed base-rate tracker; naive trailing-10 team tracker;
  both scored through NB r = 40). Neither baseline reads M_BAR;
  the recorded shipped baseline numbers stand.

## Target and data

- Target: stats-feed total shots per match =
  `home_total_shots + away_total_shots`.
- Scope: regular phase only; finals excluded; sorted by
  (day, match_id). One chronological walk-forward pass; every
  state updates only AFTER the match is predicted (the shipped
  harness's update rule, including its level-layer prediction
  input, is reproduced verbatim). Warm-up: 2021/2022 updates
  state but is never scored; scored dev seasons 2022/2023,
  2023/2024, 2024/2025 (n = 369).
- No xG, shotmap or xGOT arm is eligible (none has a dev window),
  as in the original prereg.

## Frozen line and ladder

- **Primary line: 27.5** (O27.5)
- Ladder (reported): 26.5 / 27.5 / 28.5.
- All gate legs judged at 27.5 only (binary log-loss, natural log).

## Dev protocol

- Scored dev: seasons 2022/2023–2024/2025 (n = 369). The dev
  harness must not read 2025/2026 or 2026/2027 rows at all
  (enforced via `league/gate_lib/`'s sealed guard: dev loading
  asserts no sealed rows; P2 design seal applies to every
  artefact produced).
- Metric: mean binary log-loss at line 27.5, per season and
  pooled, per arm and per baseline, computed via
  `league/gate_lib/` metrics.
- The corrected dev evaluation reports the corrected arm B/C
  numbers beside the shipped (copied-constant) numbers.
- Each arm of record is judged on its own numbers: if NEITHER
  corrected arm passes the dev gate, the candidate dies at dev:
  verdict FAIL (dev), the sealed window is NOT read. An arm that
  fails the dev gate is dead and is not read on the window.

## Virgin protocol

- Virgin window: virgin_primary: 2025/2026, regular only,
  **n = 110** — the original candidate's virgin window per
  `config.yaml` and `PREREG_T_AUW.md` — read **ONCE**, only for
  dev-passing arms of record, after the dev-pass token is
  recorded via `league/gate_lib/` (`record_dev_pass`) and the
  window is loaded through the gate_lib sealed loader
  (`load_sealed_rows`). The walk-forward continues from the dev
  run's end state under the shipped harness's update rule.
  2026/2027 is reserved/unread and is never loaded.
- Virgin metrics per arm: LL@27.5; calibration via gate_lib =
  predicted - actual (mean P(over 27.5) − actual over-27.5 rate),
  in percentage points, SE = sd(p_i − y_i)/√n reported.

## GATE LEGS (verbatim, frozen — identical to PREREG_T_AUW)

Dev gate beats BOTH league base-rate/climatology and naive trailing-10 baselines. Virgin (i) LL <= Gate Zero and <= best baseline; (ii) `|mean predicted − actual| <= 1.0pp` clean, within one `SE=sd(p_i−y_i)/sqrt(n)` provisional, otherwise fail; (iii) variant per-season sign check. Both-pass ships lower pooled virgin LL; ties go simpler. Gate Zero dev failure means FAIL and virgin NOT read. Halves on PASS use total-shots 0.467/0.533.

Mechanical reading (adapted only where the Lane 1 arm-of-record
designation requires it, mirroring the sibling PREREG_T_AU
reading): "Gate Zero" in leg (i) is arm A; leg (iii) = the
variant arm's dev LL@27.5 ≤ arm A's in at least half the dev
seasons (≥ 2 of 3); "Gate Zero dev failure means FAIL" applies
to each arm of record's own dev gate (an arm of record that does
not beat BOTH baselines on dev is dead, no virgin read for it);
ties go simpler in the order A before B before C. An arm of
record passes iff it survives the dev gate AND passes virgin
(i)–(ii) (PROVISIONAL counts on leg (ii), recorded as such) AND
leg (iii). Verdict labels: all legs clean → CLEAN PASS; leg (ii)
provisional with (i) and (iii) passed → PROVISIONAL PASS;
otherwise FAIL. If both arms of record pass, the lower pooled
virgin LL ships; if one passes, it ships. Shipping is subject to
the runner-join preparation on this branch; no merge under this
preregistration.

## Reporting requirements

- P6 worst-fold: the verdict reports the worst dev season's legs
  (worst by the reference arm, arm A, at the primary line) beside
  the pooled legs — information only, no gate change.
- P2 seal: all artefacts produced under this preregistration are
  computed on dev-era seasons only until the single sealed read;
  the verdict states the prereg commit hash and the dev-pass
  token record.
- Verdict: `reports/VERDICT_L1_T_AUW.md`, with shipped vs
  corrected dev numbers and, if read, every sealed leg.

## Forbidden

The copied constant 24.9 anywhere in this candidate's runs; any
arm beyond A/B/C; any constant search on this corpus; any second
sealed read; any reading of 2026/2027.

Production code and data are untouched. No push. No merge.
