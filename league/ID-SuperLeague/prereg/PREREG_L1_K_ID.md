# Pre-registration — L1-K-ID (ID-SuperLeague cards, Lane 1 re-entry)

**Lane 1 status.** This is a NEW candidate under the improvement
program charter (`league/IMPROVEMENT_PROGRAM.md`, Lane 1), entered
from `league/improvement_scratch/LANE1_WAVE1/cohort_report.md`
§1.2/§1.4/§1.5/§3 row 3 (K-ID, cohort A — variants-moot, AUDIT.md
§2 cause 4). The original candidate K-ID failed at the DEV gate
(`league/ID-SuperLeague/reports/K_ID_VERDICT.md`: FAIL, virgin
deliberately NOT read): Gate Zero scored pooled dev LL@4.5 0.7003
against the league base rate 0.6959 and naive trailing-10 0.6978 —
it beat neither — and the original prereg's frozen rule ("Gate
Zero failing dev ⇒ candidate FAILS, variant moot, virgin NOT
read") killed the candidate before its window was read. Its sealed
window was never read and remains genuinely sealed
(`engine/cards/results_virgin.json` records `virgin_read: false`).
This preregistration is the branch's FIRST commit, and its commit
message states that it precedes any sealed access. No sealed data
is loaded before that commit. One read, verdict final, no
iteration against the window after the read.

**Method difference, stated in advance (the sole difference).**
The arm that beat both baselines on dev — X5, the blend — becomes
the arm of record. Gate Zero is retained as a baseline/comparator
only: its dev numbers are recomputed and reported, and it is also
run on the sealed window solely as the leg-(i) reference, but its
dev pass is no longer a precondition for the arm of record's
sealed read. That precondition is the gate-architecture defect
this cohort exists to correct (cohort report §1.5). Gate Zero is
retained as baseline/comparator only, and its dev veto is removed
as the stated method difference. Nothing else changes: same
target, same machinery, same baselines, same thresholds as
`PREREG_K_ID.md`.

## Arm of record and comparators

- **Arm of record: X5** — mu = 0.5·model + 0.5·naive trailing-10,
  exactly as frozen in `PREREG_K_ID.md` and as implemented in
  `league/ID-SuperLeague/engine/cards/run_k_id.py` (the blended
  mean is scored through the NB over-probability with the model's
  r). X5 adopted in the original prereg; within-season split-half
  reliability 0.402 for / 0.338 against. Only X5 can ship under
  this preregistration.
- Gate Zero — the production cards pattern (decayed venue-split
  yellow ratings, half-life 270d, prior shrinkage K=8, pre-history
  fallbacks home 2.13 / away 2.33 = dev-era measured means; NB
  over-probability with r estimated on the seed season by the
  harness moment method) — is retained as a comparator/baseline
  only. The original prereg's clause "Gate Zero failing dev ⇒
  candidate FAILS, variant moot, virgin NOT read" does NOT apply
  to this Lane 1 candidate; that veto is the defect this re-entry
  exists to correct. X5's dev gate below is judged on X5's own
  numbers. Gate Zero cannot ship under this preregistration
  regardless of its numbers.
- Baselines (harness, not models), unchanged from
  `PREREG_K_ID.md`: league base rate (the model's running
  league-mean state; the "climatology" of the original virgin
  leg (i)) and naive trailing-10.

No referee arm exists: X8 referee strictness is dropped — referee
identity is absent (infoBox.Referee.text empty in 1,620/1,620
payloads); no referee arm exists. There is no referee operational
gate for this candidate, because X5 uses no referee data at all.

## Target and data

- Target: **event-unified yellows** = direct Yellow + YellowRed
  card events, home + away (`yellow_home + yellow_away` in the
  Phase A CSV). Target-source decision (frozen in the original
  prereg, before fitting): the stats feed carries no cards key at
  all in this league (the only stats keys with content are
  BallPossesion, total_shots, ShotsOnTarget, corners), so events
  are the target **by construction** (RU-1Division precedent,
  identical target definition). The substitute guard is feed
  completeness: the target is scored **only on events_complete
  matches** (event feed contains Substitution and Half events).
  Truncated-feed matches neither score nor update the online
  state (their true yellow counts are unknown).
- Source: `league/ID-SuperLeague/data/id_matches.csv`. Phase rule:
  `regular` rows only.
- Events_complete counts (regular): seed 2021/2022 267, dev
  2022/2023 306, 2023/2024 144, 2024/2025 281, virgin 2025/2026
  306. The 2023/2024 scored block is the Jul–Oct 2023
  complete-feed slice (actual over-4.5 rate 0.6181) — a recorded
  caveat of this candidate, not a design input.
- Halves use frozen `yellow_cards_1h_share: 0.385` from event
  order on 2023/2024–2025/2026 complete-feed matches
  (presentation only).

## Frozen line and ladder

- **Primary line: 4.5** (dev mean 4.455, over-rate 0.452).
  Ladder: 3.5 / 4.5 / 5.5 (reported; the gate is judged at 4.5
  only, binary log-loss, natural log).

## NB size r — estimation discipline (frozen, unchanged)

Per method (model, base, naive), r is estimated by the harness
moment method on causal one-step-ahead residuals of earlier data
only, clipped to [2, 500]; denominator ≤ 0 → r = 500. Dev scoring:
r per method is estimated from the seed season 2021/2022 only,
then frozen for the scored dev seasons. Virgin scoring: r per
method is re-estimated from causal predictions over all
pre-virgin seasons (2021/2022–2024/2025) only, then frozen for
2025/2026. No virgin outcome enters any r. (On the seed season
the moment denominator is negative — seed yellows are
underdispersed — so all three dev r values sit at the 500 cap,
the Poisson limit, exactly as the original verdict records.)

## Dev protocol

- The dev evaluation runs through `league/gate_lib/`: the prereg
  tokens are parsed mechanically (`parse_prereg`), dev loading
  asserts no sealed rows (`assert_no_sealed_rows` against the
  sealed seasons 2025/2026 and 2026/2027), and all leg arithmetic
  (log loss, calibration, sign check, calibration band) uses the
  gate_lib implementations — gate_lib numbers are the verdict's.
  The original harness's `count_gate` writer is NOT used (its
  virgin legs are gated on a Gate Zero dev pass — the §5.6-class
  trap this protocol exists to avoid). P2 design seal applies to
  every artefact produced: EDA/design artefacts are computed on
  dev-era seasons only; this entry introduces NO new EDA and NO
  new design choice.
- Dev period: seed 2021/2022 (267 events_complete rows, warms
  state and tunes r, never scored); scored 2022/2023 (306),
  2023/2024 (144), 2024/2025 (281); pooled dev n = 731.
  Chronological online walk-forward as in the reference harness.
- Documented dev numbers to reproduce (from `K_ID_VERDICT.md`,
  `engine/cards/results_dev.json` and the cohort report §1.2):
  X5 pooled dev LL@4.5 **0.6940**, Gate Zero 0.7003, league base
  rate 0.6959, naive trailing-10 0.6978, dev n = 731. Per-season
  LL@4.5 — X5: 2022/2023 0.6846, 2023/2024 0.7164, 2024/2025
  0.6928; Gate Zero: 2022/2023 0.6899, 2023/2024 0.7217, 2024/2025
  0.7006 (sign check 3 of 3 for X5). The recomputation must
  reproduce X5 beating BOTH baselines within artefact rounding;
  if it does not, the candidate STOPS: no sealed read, verdict
  written as a STOPPED report explaining the discrepancy.
- If X5 passes the dev gate, the dev-pass token is recorded via
  gate_lib (`record_dev_pass`, candidate id `L1-K-ID`) BEFORE any
  sealed load. If X5 does not pass, the candidate dies at dev and
  the window stays unread.

## Virgin protocol

- Virgin window: 2025/2026 (n = 306, all events_complete) — the
  original virgin season named in the original prereg and in
  `league/ID-SuperLeague/config.yaml`. Mechanical token for
  gate_lib parsing: virgin_primary: 2025/2026 — read **ONCE**,
  only if X5 passes the dev gate, after the dev-pass token is
  recorded, loaded through the gate_lib sealed loader
  (`load_sealed_rows`). 2026/2027 is reserved and is NOT read
  anywhere in this build. The walk-forward continues from the
  dev run's end state; r per the discipline above.
- Calibration per arm at 4.5 via gate_lib: predicted − actual
  (mean predicted P(over 4.5) − actual over-4.5 rate), in
  percentage points, with SE = sd(p_i − y_i)/√n reported.
  Calibration: |breach| ≤ 1.0pp clean PASS; a breach within 1 SE
  of the boundary is PROVISIONAL PASS; beyond it FAIL. (The gate
  uses |breach|, so the legs are identical under the gate_lib
  sign convention, predicted - actual.)

## GATE LEGS (frozen — identical to PREREG_K_ID)

Dev gate — pooled dev LL and primary-line LL of an arm must beat
climatology/base-rate and naive trailing-10, else the arm is
dead. Virgin legs — (i) LL leg: arm's virgin LL ≤ Gate Zero's AND
≤ climatology's; (ii) calibration leg: |breach| ≤ 1.0pp clean
PASS, ≤ 1 SE beyond the boundary PROVISIONAL, otherwise FAIL
(breach = mean predicted over-rate − actual over-rate, pp);
(iii) variant must beat Gate Zero in at least half of dev seasons
(sign check). Both-pass rule: if Gate Zero and the variant both
pass all legs, the lower pooled virgin LL ships; if only one
passes, it ships; ties go to the simpler arm (Gate Zero). If none
passes, K-ID FAIL and nothing ships. Virgin is read once.

Lane 1 reading (adapted only where the arm-of-record designation
requires it): the dev gate is judged on the arm of record, X5 —
pooled dev LL@4.5 of X5 must beat BOTH baselines, else X5 is dead
and there is no sealed read. Leg (i) is read exactly as frozen:
X5's virgin LL ≤ Gate Zero's AND ≤ both baselines' (the frozen
text names climatology; the second baseline, naive trailing-10,
is reported beside it and the stricter reading — ≤ the lower of
the two baselines — is the one applied, matching the program's
mechanical reading in the other Lane 1 cards entries). Leg (iii)
= X5's dev LL@4.5 ≤ Gate Zero's in at least half the dev seasons
(≥2 of 3). The both-pass rule is retained verbatim: Gate Zero's
dev failure is a reproduced fact under this preregistration's own
dev evaluation, so the both-pass branch cannot trigger unless the
dev recomputation contradicts the documented numbers — in which
case the candidate STOPS under the dev protocol above and no
sealed read occurs. X5 passes iff it survives the dev gate AND
passes virgin legs (i) and (ii) (PROVISIONAL counts on leg (ii),
recorded as such) AND leg (iii). Verdict labels: all legs clean →
CLEAN PASS; leg (ii) provisional with (i) and (iii) passed →
PROVISIONAL PASS; otherwise FAIL. If X5 passes, it ships (subject
to the runner-join preparation on this branch; no merge under
this preregistration).

## Design seal (P2)

All EDA/design artefacts for this entry are under the P2 design
seal: EDA and reliability artefacts may only be computed on
dev-era seasons. This entry takes no new design decision from any
artefact: the design is inherited verbatim from the original
prereg (frozen 2026-11-10) and from cohort report §1.5. No
sealed-season aggregate was computed or consulted in writing this
preregistration. (The virgin events_complete count, 306, quoted
in the original prereg and the cohort report is a completeness
count published before this program; it is not used as a design
input here.)

## Worst-fold reporting (P6)

The verdict includes the P6 worst-fold block: the worst dev
season — defined by the reference arm (Gate Zero) at the primary
metric — with every arm's and baseline's legs on that fold
reported beside the pooled legs, produced via
`league/worst_fold/`. Information only, no gate change.

## Reporting requirements

- P6 worst-fold: as above, in the verdict.
- P2 seal: all artefacts produced under this preregistration are
  computed on dev-era seasons only until the single sealed read;
  the verdict states the prereg commit hash and the dev-pass
  token record.
- Verdict: `league/ID-SuperLeague/reports/VERDICT_L1_K_ID.md`,
  with the documented vs recomputed dev numbers and, if read,
  every sealed leg.

## Outputs

- Engine: `league/ID-SuperLeague/engine/cards/` (existing; Lane 1
  runner `run_l1_k_id.py` added).
- Dev results: `league/ID-SuperLeague/engine/cards/results_dev_l1.json`.
- Virgin results: `league/ID-SuperLeague/engine/cards/results_virgin_l1.json`
  (or a `{"virgin_read": false, ...}` marker when virgin is not
  read).
- Dev-pass registry:
  `league/ID-SuperLeague/engine/cards/dev_pass_registry_l1.json`.
- On PASS only: virgin predictions
  `league/ID-SuperLeague/predictions/k_id_lane1_virgin_predictions.csv`
  (the shipped arm's — X5's — predictions, one row per 2025/2026
  match, FT + halves via the frozen cards constant 0.385,
  presentation only) and
  `league/ID-SuperLeague/engine/cards/fitted_params_virgin_l1.json`.

## Forbidden

Any gate move after results are seen; any second sealed read; any
arm beyond Gate Zero/X5; any constant search on this corpus; any
use of 2026/2027 rows. Production top-5 untouched. No push. No
merge.
