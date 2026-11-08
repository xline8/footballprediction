# Pre-registration — L1-K-CO (CO-PrimeraA cards, Lane 1 re-entry)

**Lane 1 status.** This is a NEW candidate under the improvement
program charter (`league/IMPROVEMENT_PROGRAM.md`, Lane 1), entered
from `league/IMPROVEMENT_LANE1_INVENTORY.md` and the wave-1 cohort
report (`league/improvement_scratch/LANE1_WAVE1/cohort_report.md`
§1.2/§1.5, cohort A — variants-moot, AUDIT.md §2 cause 4). The
original candidate K-COA failed at the DEV gate
(`reports/K_COA_VERDICT.md`: FAIL, virgin NOT read): Gate Zero
scored pooled dev LL@5.5 0.7001 against the league base rate
0.6956 and naive trailing-10 0.7080, and the original prereg's
mechanical reading ("if Gate Zero fails its own dev gate, variants
are moot, verdict FAIL, virgin NOT read") killed the candidate
before its window was read. Its sealed window was never read and
remains genuinely sealed. This preregistration is committed BEFORE
any sealed access; one read, verdict final, no iteration against
the window after the read.

**Method difference, stated in advance (the sole difference).**
The arm that beat both baselines on dev — X8, the referee
multiplier — becomes the arm of record. Gate Zero is retained as a
baseline only: its dev numbers are recomputed and reported, and it
is also run on the sealed window solely as the leg-(i) reference,
but its dev pass is no longer a precondition for the arm of
record's sealed read. That precondition is the gate-architecture
defect this cohort exists to correct (cohort report §1.5). Gate
Zero is retained as baseline/comparator only, and its dev veto is
removed as the stated method difference. Nothing else changes:
same target, same machinery, same baselines, same gate legs as
`PREREG_K_COA.md`.

## Arm of record and comparators

- **Arm of record: X8** — Gate Zero plus the referee multiplier,
  exactly as frozen in `PREREG_K_COA.md` and as implemented in
  `league/CO-PrimeraA/engine/cards/` (the J1 cards mechanics):
  for the appointed referee, trailing mean of event-unified
  yellows within this league (matches strictly before kickoff),
  shrunk toward the running league mean with K_REF = 8;
  multiplier = clamp(rate / league_mean, 0.67, 1.50) applied to
  both teams' expectations. Referees with <8 prior era matches,
  or no named referee, fall back to Gate Zero for that fixture
  (multiplier 1.0, fallback recorded — no imputation). Only X8
  can ship under this preregistration.
- Gate Zero — the unmodified production cards pattern (decayed
  team attack/defence state + NB total; r estimated on the seed
  block per method, as in the reference harness) — is retained as
  a comparator/baseline only. The original prereg's clause "If
  Gate Zero fails its own dev gate, variants are moot, verdict
  FAIL, virgin NOT read" does NOT apply to this Lane 1 candidate;
  that veto is the defect this re-entry exists to correct. X8's
  dev gate below is judged on X8's own numbers. Gate Zero cannot
  ship under this preregistration regardless of its numbers.
- Baselines (harness, not models), unchanged from
  `PREREG_K_COA.md`: league base rate at 5.5 (the model's running
  league-mean state — the reference harness's `base` method) and
  naive trailing-10 (reference-harness definition).

## Target and data

- Target — event-unified yellows (frozen in the original prereg
  BEFORE fitting): `y = ev_yellow_inc2nd_home +
  ev_yellow_inc2nd_away` (each Yellow = 1, each YellowRed = 1
  additional yellow), from the CSV's event-derived columns. The
  stats-feed `yellow_cards` columns are NOT the target (feed
  level break inside 2022; card events absent 2021–2022). The
  harness must not load earlier rows than the cards era for this
  candidate.
- Source: `league/CO-PrimeraA/data/co_primeraa_matches.csv`, era
  2023 - Apertura onward only. Dev-era (2024–2025 blocks)
  event-unified mean 5.60.
- Seed (training only): 2023 - Apertura (n = 226).
- Dev eval blocks: 2023 - Clausura … 2025 - Clausura (5
  tournaments, n = 1,110), chronological online walk-forward as
  in the reference harness (decayed state, HL = 270,
  K_PRIOR = 8).

## Frozen line and ladder

- **Primary line: 5.5**
- Ladder (reported): 3.5 / 4.5 / 5.5 / 6.5.
- All gate legs judged at 5.5 only (binary log-loss, natural log).

## Dev protocol

- The dev evaluation runs through `league/gate_lib/`: the prereg
  tokens are parsed mechanically (`parse_prereg`), dev loading
  asserts no sealed rows (`assert_no_sealed_rows` against the
  sealed seasons 2026 - Apertura / 2026 - Clausura), and
  metrics/calibration use the gate_lib implementations. P2
  design seal applies to every artefact produced: EDA/design
  artefacts are computed on dev-era seasons only.
- Documented dev numbers to reproduce (from `K_COA_VERDICT.md`
  and the cohort report §1.2): X8 pooled dev LL@5.5 **0.6918**,
  Gate Zero 0.7001, league base rate 0.6956, naive trailing-10
  0.7080, dev n = 1,110 (dev rows loaded 1,336 including the
  seed block). The recomputation must reproduce X8 beating BOTH
  baselines within artefact rounding; if it does not, the
  candidate STOPS: no sealed read, verdict written as a STOPPED
  report explaining the discrepancy.
- If X8 passes the dev gate, the dev-pass token is recorded via
  gate_lib (`record_dev_pass`, candidate id `L1-K-CO`) BEFORE any
  sealed load. If X8 does not pass, the candidate dies at dev and
  the window stays unread.

## Virgin protocol

- Virgin window: 2026 - Apertura (n = 204, complete) — the
  original candidate's virgin season per `config.yaml` (the
  `virgin` field) and `PREREG_K_COA.md` — read **ONCE**, only if
  X8 passes the dev gate, after the dev-pass token is recorded,
  loaded through the gate_lib sealed loader
  (`load_sealed_rows`). Mechanical token for gate_lib parsing:
  virgin_primary: 2026 - Apertura. 2026 - Clausura (in progress)
  is NOT read anywhere in this build. The walk-forward continues
  from the dev run's end state (r estimated on the full dev fit,
  as in the reference harness).
- Virgin metrics per arm: LL@5.5; calibration via gate_lib =
  predicted − actual (mean P(over 5.5) − actual over-5.5 rate),
  in percentage points, SE = sd(p_i − y_i)/√n reported. (The
  original prereg reported calibration as actual − predicted;
  the gate uses |breach|, so the legs are identical under the
  gate_lib sign convention, predicted - actual.)

## GATE LEGS (verbatim, frozen — identical to PREREG_K_COA)

Dev gate — pooled dev LL@5.5 of an arm must beat BOTH baselines, else the arm is dead. Virgin legs — (i) LL leg: arm's virgin LL@5.5 ≤ Gate Zero's AND ≤ both baselines'; (ii) calibration leg: |mean predicted P(over 5.5) − actual over-rate| ≤ 1.0pp clean PASS; a breach within 1 SE of the boundary is recorded PROVISIONAL PASS, beyond it FAIL (SE = sd(p_i − y_i)/√n); (iii) per-season sign check on dev (arm LL ≤ Gate Zero LL in at least half the dev seasons) for the both-pass rule. Both-pass rule: if Gate Zero and a variant both pass all legs, the lower virgin LL ships; if only one passes, it ships; if none passes, K-COA verdict is FAIL and nothing ships.

Variant arms require leg (iii); Gate Zero is exempt. Ties go to the
simpler arm (Gate Zero before X8). Calibration is reported as
predicted − actual under the gate_lib convention; the gate uses
|breach|.

Lane 1 reading (adapted only where the arm-of-record designation
requires it): the dev gate is judged on the arm of record, X8 —
pooled dev LL@5.5 of X8 must beat BOTH baselines, else X8 is dead
and there is no sealed read. Leg (iii) = X8's dev LL@5.5 ≤ Gate
Zero's in at least half the dev blocks (≥ 3 of 5). The both-pass
rule is retained verbatim: Gate Zero's dev failure is a reproduced
fact under this preregistration's own dev evaluation, so the
both-pass branch cannot trigger unless the dev recomputation
contradicts the documented numbers — in which case the candidate
STOPS under the dev protocol above and no sealed read occurs. X8
passes iff it survives the dev gate AND passes virgin legs (i)
and (ii) (PROVISIONAL counts on leg (ii), recorded as such) AND
leg (iii). Verdict labels: all legs clean → CLEAN PASS; leg (ii)
provisional with (i) and (iii) passed → PROVISIONAL PASS;
otherwise FAIL. If X8 passes, it ships (subject to the
runner-join preparation on this branch and the operational
condition below; no merge under this preregistration).

## Operational condition (carried over verbatim)

Referees with <8 prior era matches, or no named referee, fall
back to Gate Zero for that fixture (multiplier 1.0, fallback
recorded — no imputation). An unpublished appointment therefore
falls back to Gate Zero for that fixture, with no imputation,
and a PASS ships with that condition attached (the K-BNAC
precedent). Historical referee coverage in the dev era:
1,275/1,336 = 95.4% (per tournament 91.2–98.7%); strictness
split-half r = 0.487 on 36 referees (EDA F5).

## Reporting requirements

- P6 worst-fold: the verdict reports the worst dev block's legs
  (worst by the reference arm, Gate Zero, at the primary line)
  beside the pooled legs — information only, no gate change.
- P2 seal: all artefacts produced under this preregistration are
  computed on dev-era seasons only until the single sealed read;
  the verdict states the prereg commit hash and the dev-pass
  token record.
- Verdict: `league/CO-PrimeraA/reports/VERDICT_L1_K_CO.md`, with
  the documented vs recomputed dev numbers and, if read, every
  sealed leg.

## Outputs

Engine `league/CO-PrimeraA/engine/cards/` (existing; Lane 1 runner
`run_l1_k_co.py` added); `results_dev_l1.json`,
`results_virgin_l1.json`; on PASS, virgin predictions
`league/CO-PrimeraA/predictions/k_coa_virgin_predictions.csv`
(FT + halves via the frozen cards constant 0.3543, presentation
only) and `fitted_params_virgin.json`, as in the original prereg.

## Forbidden

Any gate move after results are seen; any second sealed read;
any arm beyond Gate Zero/X8; any constant search on this corpus;
any use of 2026 - Clausura rows. Production code untouched.
No push. No merge.
