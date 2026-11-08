# Pre-registration — L1-K-PE (PE-Liga1 cards, Lane 1 re-entry)

**Lane 1 status.** This is a NEW candidate under the improvement
program charter (`league/IMPROVEMENT_PROGRAM.md`, Lane 1), entered
from `league/IMPROVEMENT_LANE1_INVENTORY.md` and the wave-1 cohort
report (`league/improvement_scratch/LANE1_WAVE1/cohort_report.md`
§1.2/§1.5, cohort A — variants-moot). The original candidate K-PE
failed at the DEV gate (`reports/K_PE_VERDICT.md`: FAIL, virgin NOT
read): Gate Zero scored pooled dev LL@4.5 0.712602 against the
league base rate 0.707846 and naive trailing-10 0.692826, and the
original prereg's mechanical reading ("if Gate Zero fails its own
dev gate, variants are moot") killed the candidate before its
window was read. Its sealed window was never read and remains
genuinely sealed. This preregistration is committed BEFORE any
sealed access; one read, verdict final, no iteration against the
window after the read.

**Method difference, stated in advance (the sole difference).**
The arm that beat both baselines on dev — X8, the referee
multiplier — becomes the arm of record. Gate Zero is retained as a
baseline only: its dev numbers are recomputed and reported, and it
is also run on the sealed window solely as the leg-(i) reference,
but its dev pass is no longer a precondition for the arm of
record's sealed read. That precondition is the gate-architecture
defect this cohort exists to correct (cohort report §1.5). Nothing
else changes: same target, same machinery, same baselines, same
gate legs as `PREREG_K_PE.md`.

## Arm of record and comparators

- **Arm of record: X8** — Gate Zero plus the referee multiplier,
  exactly as frozen in `PREREG_K_PE.md` and as implemented in
  `league/PE-Liga1/engine/cards/` (the J1/CO-A cards mechanics):
  for the appointed referee, trailing mean of event-unified
  yellows within this league (matches strictly before kickoff),
  shrunk toward the running league mean with K_REF = 8;
  multiplier = clamp(rate / league_mean, 0.67, 1.50); referees
  with no prior in-league matches — and matches with no named
  referee — get factor 1.0. Only X8 can ship under this
  preregistration.
- Gate Zero — the unmodified production cards pattern (decayed
  team attack/defence state + NB total; r estimated on the seed
  block per method, as in the reference harness) — is retained as
  a comparator/baseline only. The original prereg's clause "if
  Gate Zero fails its own dev gate, variants are moot, verdict
  FAIL, virgin NOT read" does NOT apply to this Lane 1 candidate;
  that veto is the defect this re-entry exists to correct. X8's
  dev gate below is judged on X8's own numbers. Gate Zero cannot
  ship under this preregistration regardless of its numbers.
- Baselines (harness, not models), unchanged from
  `PREREG_K_PE.md`: league base rate at 4.5 (pooled rate strictly
  prior to the scored block) and naive trailing-10
  (reference-harness definition).

## Target and data

- Target — event-unified yellows, era 2023+ (frozen in the
  original prereg BEFORE fitting): `y = ev_yellow_inc2nd_home +
  ev_yellow_inc2nd_away` (each Yellow = 1, each YellowRed = 1
  additional yellow), from the CSV's event-derived columns. The
  harness must not load earlier rows for this candidate.
- Source: `league/PE-Liga1/data/pe_liga1_matches.csv`, modelling
  corpus (regular, non-awarded), era 2023 onward only. Cards-era
  dev mean (2023–2024) 4.909.
- Seed (training only): 2023 - Apertura (n = 165).
- Dev eval blocks: 2023 - Clausura … 2024 - Clausura (3 blocks,
  n = 475), chronological online walk-forward as in the reference
  harness (decayed state, HL = 270, K_PRIOR = 8).

## Frozen line and ladder

- **Primary line: 4.5**
- Ladder (reported): 3.5 / 4.5 / 5.5 / 6.5.
- All gate legs judged at 4.5 only (binary log-loss, natural log).

## Dev protocol

- The dev evaluation runs through `league/gate_lib/`: the prereg
  tokens are parsed mechanically (`parse_prereg`), dev loading
  asserts no sealed rows (`assert_no_sealed_rows` against the
  sealed seasons 2025/2026), and metrics/calibration use the
  gate_lib implementations. P2 design seal applies to every
  artefact produced: EDA/design artefacts are computed on
  dev-era seasons only.
- Documented dev numbers to reproduce (from `K_PE_VERDICT.md` and
  the cohort report §1.2): X8 pooled dev LL@4.5 **0.687450**,
  Gate Zero 0.712602, league base rate 0.707846, naive
  trailing-10 0.692826, dev n = 475. The recomputation must
  reproduce X8 beating BOTH baselines within artefact rounding;
  if it does not, the candidate STOPS: no sealed read, verdict
  written as a STOPPED report explaining the discrepancy.
- If X8 passes the dev gate, the dev-pass token is recorded via
  gate_lib (`record_dev_pass`, candidate id `L1-K-PE`) BEFORE any
  sealed load. If X8 does not pass, the candidate dies at dev and
  the window stays unread.

## Virgin protocol

- Virgin window: calendar 2025 (n = 323) — the original
  candidate's virgin season per `config.yaml`
  (`virgin_primary: 2025`) and `PREREG_K_PE.md` — read **ONCE**,
  only if X8 passes the dev gate, after the dev-pass token is
  recorded, loaded through the gate_lib sealed loader
  (`load_sealed_rows`). 2026 is NOT read anywhere in this build.
  The walk-forward continues from the dev run's end state (r
  estimated on the full dev fit, as in the reference harness).
- Virgin metrics per arm: LL@4.5; calibration via gate_lib =
  predicted − actual (mean P(over 4.5) − actual over-4.5 rate),
  in percentage points, SE = sd(p_i − y_i)/√n reported. (The
  original prereg reported calibration as actual − predicted;
  the gate uses |breach|, so the legs are identical under the
  gate_lib sign convention.)

## GATE LEGS (verbatim, frozen — identical to PREREG_K_PE)

Dev gate — pooled dev LL@4.5 of an arm must beat BOTH baselines, else the arm is dead. Virgin legs — (i) LL leg: arm's virgin LL@4.5 ≤ Gate Zero's AND ≤ both baselines'; (ii) calibration leg: |mean predicted P(over 4.5) − actual over-rate| ≤ 1.0pp clean PASS; a breach within 1 SE of the boundary is recorded PROVISIONAL PASS, beyond it FAIL (SE = sd(p_i − y_i)/√n); (iii) per-season sign check on dev (arm LL ≤ Gate Zero LL in at least half the dev seasons) for the both-pass rule. Both-pass rule: if Gate Zero and a variant both pass all legs, the lower virgin LL ships; if only one passes, it ships; if none passes, K-PE verdict is FAIL and nothing ships.

Variant arms require leg (iii); Gate Zero is exempt. Ties go to the
simpler arm (Gate Zero before X8). Calibration is reported as
predicted − actual under the gate_lib convention; the gate uses
|breach|.

Lane 1 reading (adapted only where the arm-of-record designation
requires it): the dev gate is judged on the arm of record, X8 —
pooled dev LL@4.5 of X8 must beat BOTH baselines, else X8 is dead
and there is no sealed read. Leg (iii) = X8's dev LL@4.5 ≤ Gate
Zero's in at least half the dev blocks (≥ 2 of 3). The both-pass
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

Operational condition: if the appointment is not published
pre-match in the live pipeline, the fixture falls back to Gate
Zero. No referee identity is imputed. A PASS ships with this
condition attached (the K-BNAC precedent). Historical referee
coverage (original prereg): 97.9% (2023) / 84.6% (2024) / 80.5%
(virgin 2025); strictness split-half r = 0.769 on 2023–2024 —
the strongest measured in the programme.

## Reporting requirements

- P6 worst-fold: the verdict reports the worst dev block's legs
  (worst by the reference arm, Gate Zero, at the primary line)
  beside the pooled legs — information only, no gate change.
- P2 seal: all artefacts produced under this preregistration are
  computed on dev-era seasons only until the single sealed read;
  the verdict states the prereg commit hash and the dev-pass
  token record.
- Verdict: `league/PE-Liga1/reports/VERDICT_L1_K_PE.md`, with the
  documented vs recomputed dev numbers and, if read, every
  sealed leg.

## Outputs

Engine `league/PE-Liga1/engine/cards/` (existing; Lane 1 runner
`run_l1_k_pe.py` added); `results_dev_l1.json`,
`results_virgin_l1.json`; on PASS, virgin predictions
`league/PE-Liga1/predictions/k_pe_virgin_predictions.csv`
(FT + halves via the frozen cards constant 0.3818, presentation
only) and `fitted_params_virgin.json`, as in the original prereg.

## Forbidden

Any gate move after results are seen; any second sealed read;
any arm beyond Gate Zero/X8; any constant search on this corpus;
any use of 2026 rows. Production code untouched. No push.
No merge.
