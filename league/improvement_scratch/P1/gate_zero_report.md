# P1 Gate Zero — Forward-Stability Admission Leg: Replay Report

**VERDICT: P1 GATE ZERO FAILS — P1 DIES by its pre-registered kill rule.**

| Measure | Result | Threshold | Leg |
|---|---|---|---|
| A — sealed calibration failures the forward leg would have stopped | **18/68 = 26.5%** | ≥ 1/3 (33.3%) | **FAIL** |
| B — eventual passes the forward leg would have killed | **11/120 = 9.2%** | ≤ 10% | PASS |

Gate Zero passes only if A ≥ 1/3 AND B ≤ 10% (AUDIT.md §6, proposal P1).
A fails, so the workstream dies. No thresholds were altered and no
variant of the rule was tried.

Coverage (headline denominators are the measurable populations):
sealed calibration failures **68/70 measurable (97.1%)**; eventual
passes **120/122 measurable (98.4%)**; sealed other-failures 29/29
(reported for completeness; they enter neither measure). Both
coverages are far above the 50% floor in the test brief.

Robustness to the missing coverage: even if both unmeasurable
calibration failures (S-BO, S-PY) had been stopped, A would be
20/70 = 28.6% — still below 1/3. Under every arm-selection variant
tried (below), the maximum attainable A including all unmeasurable
candidates as stopped is 32.9% — still below 1/3. **The kill does not
depend on the unmeasurable candidates or on the arm-selection
convention.**

## Population and groups

Population = every candidate that passed the pooled dev gate =
122 PASS + 99 sealed FAIL = 221 (from
`league/audit_scratch/class_batch*.jsonl`). Groups:

- `pass` — 122 (PASS_CLEAN 28 + PASS_PROV 94).
- `sealed_cal_fail` — **70**: sealed FAILs whose `fail_legs` contain a
  calibration leg (any of CAL_LINE / CAL_OU / CAL_1X2). This
  reconciles exactly with AUDIT.md §2 ("calibration legs account for
  70 of the 99"): CAL_LINE 59, CAL_OU 9, CAL_1X2 2 (union 70).
- `sealed_other_fail` — 29 (sealed LL / sign-check failures only).

Candidate IDs are not unique across leagues: C-CH and T-CH each exist
in both CH-ChallengeLeague (sealed FAIL) and CH-SuperLeague (PASS).
All counting here is keyed by (league, candidate); the CSV carries
both columns.

## The rule as replayed

Forward leg (per arm): the arm must beat BOTH baselines on the LAST
dev season alone, at the candidate's frozen gate metric, in addition
to the pooled dev legs it already passed. "Beats" = strictly lower
log-loss.

- Counting markets (S/C/K/T): LL at the prereg primary line vs the
  league base rate and the naive trailing-10, last dev season only.
  Gate line taken from the prereg first, then the dev file's
  protocol/root `primary_line`, then the verdict (source recorded
  per candidate in the CSV).
- Goals (G): the dev gate has three legs against climatology
  (1X2 LL, RPS, OU2.5 LL — the OU "base-rate baseline" is
  climatology's own OU number in every goals prereg/verdict checked),
  so the forward leg requires all three to beat climatology on the
  last dev season.
- Last dev season: the last scored dev fold as persisted — a season
  for most leagues, the league's own tournament/round blocks where
  that is the dev unit (e.g. AR, MX, VE, BO, PY, K-MXE). Tuning /
  warm-up seasons are excluded (for total shots, the protocol
  `gate_pool` defines the scored seasons where present).
- Single-season / single-window dev (5 cal + 2 pass candidates:
  K-CR, C-CH, T-CH, T-MA, C-SAFD; S-LV, S-SAFD): the forward slice is
  the whole dev set, so the leg is identical to the pooled leg by
  construction; these candidates are counted, and flagged in the CSV
  (`single_window_flat` / `n_dev_seasons` = 1).

Arm selection (the admission leg is per-arm in the frozen gates):

- Measure B: the arm that actually shipped (from
  `results_virgin.json` shipped/export/ship field in 70 cases, from
  the verdict text in 50, from a manual verdict read in 2 — C-EG and
  G-KZ, both "Gate Zero ships" after an exact tie with the variant).
  Killed = shipped arm fails the forward leg.
- Measure A: a candidate is STOPPED only if **every** arm that both
  passed the pooled dev gate and was actually read on the sealed
  window fails the forward leg — if any such arm survives, it would
  have been read and the candidate would not have been stopped at
  admission. (Arms read despite failing dev, e.g. G-J1's X2/X3, are
  excluded: they were already dead at the pooled leg.)

Sensitivities (same data, different arm conventions — all kill P1):

| Definition | A | B |
|---|---|---|
| Headline (above) | 18/68 = 26.5% | 11/120 = 9.2% |
| Reference arm only (Gate Zero / arm A) | 21/68 = 30.9% | — |
| Any evaluated arm fails (upper bound for A) | 20/68 = 29.4% | — |
| All dev-passing arms fail (strongest kill for B) | — | 11/120 = 9.2% |

Measure A by market (headline): S 5/12, C 4/17, K 2/8, T 5/20,
G 2/11. Measure B by market: C 5/40, K 3/12, S 1/31, T 1/33, G 1/4.
For reference, 9/29 sealed other-failures would also have been
stopped — the leg does catch some era drift, just not enough of the
calibration kind: most calibration failures come from arms whose
last-dev-season LL still beat both baselines (their ranking held;
their level did not), which is exactly the failure shape a
log-loss-only forward leg cannot see.

Stopped calibration failures (18): S-AR, C-AT2, S-AT, K-CH
(CH-SuperLeague), G-IE, G-MXE, T-MX, S-NO-OBOS, T-NO-OBOS, T-PL,
T-PY, S-RU1, T-RU1, C-SCOCH, K-SCOCH, C-SE2, S-USLL1, C-VE.
Killed passes (11): C-AR (X7), C-AU, K-AUW (X8), G-BA, C-CZ, K-FI,
S-IN, C-MX, K-NO, C-PE (X7), T-TH (arm B).

Margin fragility (exact persisted values, not estimates — listed so
the coordinator can see where the rule, not the arithmetic, is
knife-edge): B sits 1 kill below its boundary (12/120 = 10.0% would
still pass; a 13th kill would fail it). Closest B cases: T-TH arm B
fails by 0.0003 LL; S-BE's shipped RS survives by 0.0002 LL. Closest
A cases: K-AR's Gate Zero forward margin is +0.0006/−0.0015 (already
counted as stopped); S-AE survives by 0.0025 LL, G-J1's OU leg by
0.0010, G-VE's RPS leg by 0.0004 (full-precision JSON values).

## Unmeasurable candidates (4)

- S-BO (cal): dev is 4 round-blocks inside one season; per-block
  baseline LLs were never persisted (pooled only) and the engine has
  no per-match dev predictions file.
- S-PY (cal): per-block baseline LLs not persisted (pooled only;
  verdict prints pooled baselines only); no per-match dev
  predictions file.
- S-COA, S-PE (both pass): per-season baseline LLs not persisted
  (pooled only); no per-match dev predictions file. (S-COA's baseline
  definition deviation is also recorded in AUDIT.md §5.12.)

No sealed window was read for this test; sealed outcomes enter only
as group labels from the audit classification. No harness was
re-run; every number comes from persisted dev artefacts.

## Method and validation

- Numbers extracted per candidate from
  `league/<L>/engine/<market>/results_dev.json` (11 persisted schema
  variants across the five market families — row lists, arms/seasons
  dicts, total-shots metrics dicts, cards model/base/naive cells,
  per-block tables, and pooled-only flat files), plus
  `results_virgin.json` for shipped/scored arms. Source schema per
  candidate is recorded in the CSV.
- Cross-checks performed: (i) pooled dev-pass recomputed from the
  persisted numbers for every arm of all 221 candidates — it agrees
  with the verdicts everywhere except two candidates, and in both
  the verdict text itself confirms the recomputation (K-PT: Gate
  Zero dev-dead, only the referee arm X8 was read; T-DE2: only arm C
  dev-passed and was read). (ii) Hand-verification of raw JSON for
  S-AR, C-AR, S-AE, S-BE, G-VE, T-ZA, C-MA/T-MA and S-LV/T-LV against
  verdict dev tables — all match exactly, including the fragile
  margins above. (iii) Flat single-window candidates verified
  against their protocols/verdicts (LV and MA dev windows, CH
  2024/2025 single dev season, SA warm-up + scored inside 2025/2026).
- Known artefact quirks encountered (none change the verdict):
  HU results_dev flags omit the per-season leg (AUDIT.md §5.12) —
  numbers, not flags, were used; G-MXE per-block LLs are rounded to
  4 decimals in the persisted file (its forward margins exceed
  0.004, so rounding cannot flip it); K-PT's virgin "naive" is
  Gate-Zero-derived (AUDIT-noted) — irrelevant here, only dev
  numbers were used.

## Deliverables

- `per_candidate.csv` — one row per population candidate (221):
  league, market, candidate, group, measurable (y/n),
  forward_leg_pass (y/n; for passes = shipped arm survives, for
  fails = candidate not stopped), reference-arm outcome, evaluated /
  shipped arms, last dev season, gate line + source, last-season LLs
  for the basis arm and both baselines, artefact source, and the
  unmeasurable reason where applicable. Measures A and B reproduce
  by counting this CSV: A = cal rows with forward_leg_pass = n over
  measurable cal rows (18/68); B = pass rows with
  forward_leg_pass = n over measurable pass rows (11/120).
- Working files (extraction + computation scripts and intermediate
  JSON) in `work/` under this directory.
