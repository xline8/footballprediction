# Verdict — L1-K-ID (Indonesia Super League cards, Lane 1 re-entry) — **CLEAN PASS** (window read once, verdict final)

Date: 2026-11-11. Branch `build/lane1-kid`. Lane 1 candidate under
`league/IMPROVEMENT_PROGRAM.md` (cohort A, variants-moot; cohort
report §1.2/§1.5). Prereg: `league/ID-SuperLeague/prereg/PREREG_L1_K_ID.md`,
committed as this branch's FIRST commit
**61bbb96c98d53cb5ac5d3d5ae0c22ed3775bfd4a** ("precedes any sealed
access") before any sealed data was loaded. Arm of record: **X5**
(mu = 0.5·model + 0.5·naive trailing-10, scored with the model's
NB r). Gate Zero retained as baseline only — its dev veto (the
original prereg's "variant moot" clause) is the gate-architecture
defect this entry corrects. Target: event-unified yellows (direct
Yellow + YellowRed events), scored only on events_complete
matches, `regular` rows only. Primary line 4.5. Windows: seed
2021/2022 (267 events_complete rows), dev 2022/2023–2024/2025
(n = 731), virgin 2025/2026 (n = 306). All runs via
`league/gate_lib/` (mechanical prereg tokens, dev-pass assertion,
sealed loader) under the P2 design seal; runner:
`engine/cards/run_l1_k_id.py`. The original harness's `count_gate`
writer was not used (its virgin legs are gated on a Gate Zero dev
pass). No referee arm exists and none is used: referee identity is
absent in 1,620/1,620 payloads, so there is no referee operational
gate for this candidate.

## Dev results — reproduction (pooled LL@4.5, n = 731)

| arm / baseline | documented | recomputed (gate_lib) | abs diff |
|---|---|---|---|
| X5 (arm of record) | 0.694041 | 0.694041 | 0.0 |
| Gate Zero | 0.700256 | 0.700256 | 0.0 |
| league base rate | 0.695916 | 0.695916 | 0.0 |
| naive trailing-10 | 0.697785 | 0.697785 | 0.0 |

The documented dev pass reproduces **exactly** (difference 0.0 on
every pooled leg, not merely within artefact rounding). **Dev gate
(X5): PASS** — 0.694041 beats BOTH baselines. Gate Zero fails its
own dev gate again (0.700256 > base rate 0.695916), as documented;
under this preregistration that no longer vetoes the arm of
record. Dev-pass token recorded in
`engine/cards/dev_pass_registry_l1.json` (candidate `L1-K-ID`,
2026-11-11T12:06:05Z) before the sealed load. Dev r (all methods,
seed-season moment estimate): 500.0 (the cap — seed yellows are
underdispersed, as the original verdict records).

Per-season LL@4.5 (Gate Zero / X5 / base / naive): 2022/2023
0.689869 / 0.684634 / 0.696090 / 0.688745; 2023/2024 0.721702 /
0.716386 / 0.711166 / 0.724959; 2024/2025 0.700577 / 0.692834 /
0.687911 / 0.693704 — X5 beats Gate Zero in all 3 dev seasons.

## Sealed results — the single read (virgin 2025/2026, n = 306)

| arm / baseline | LL@4.5 | calibration (predicted − actual) | SE |
|---|---|---|---|
| Gate Zero (reference) | 0.685854 | −1.253pp | 2.840pp |
| X5 (arm of record) | **0.684568** | **−0.914pp** | 2.838pp |
| league base rate | 0.692258 | −1.138pp | 2.860pp |
| naive trailing-10 | 0.693275 | −0.736pp | 2.862pp |

Actual over-4.5 rate 0.4673; X5 mean predicted 0.4582, Gate Zero
0.4548. Virgin r (re-estimated on all pre-virgin causal residuals,
per the frozen discipline): model 500.0, base 495.84, naive 500.0.

## Gate arithmetic (mechanical, prereg legs — identical to PREREG_K_ID)

- **Leg (i) LL: PASS.** X5 virgin LL@4.5 0.684568 ≤ Gate Zero's
  0.685854 ✓, ≤ league base rate 0.692258 ✓ and ≤ naive
  trailing-10 0.693275 ✓.
- **Leg (ii) calibration: PASS (clean).** |−0.914pp| ≤ the 1.0pp
  clean boundary (SE 2.838pp reported; no provisional band
  needed).
- **Leg (iii) sign check: PASS.** X5 dev LL ≤ Gate Zero dev LL in
  3 of 3 dev seasons (≥2 required).

**Verdict: CLEAN PASS.** One read, verdict final, no iteration
against the window. X5 ships as the arm of record (subject to the
runner-join preparation on this branch; no merge under this
preregistration). Virgin predictions written to
`predictions/k_id_lane1_virgin_predictions.csv` (306 rows, arm
`x5`) and `engine/cards/fitted_params_virgin_l1.json`. The
original K-ID FAIL stands unrevised — this Lane 1 entry was a new
candidate judged on its own preregistration, on the window the
original build never read.

## P6 worst-fold block (dev, information only — no gate change)

Source: `league/ID-SuperLeague/engine/cards/results_dev.json` via
`league/worst_fold/` (worst season by the reference arm, Gate
Zero, at the primary metric); the tool's output on the Lane 1 dev
artefact (`results_dev_l1.json`) is identical.

### P6 worst-fold block — ID-SuperLeague cards (primary metric: ll)

Worst dev season (highest ll for the reference arm): **2023/2024**.

| Entity | Pooled ll | Pooled source | Worst-season (2023/2024) ll | n (worst) | Δ vs pooled |
|---|---|---|---|---|---|
| gate_zero | 0.7003 | persisted | 0.7217 | 144 | +0.0214 |
| x5 | 0.6940 | persisted | 0.7164 | 144 | +0.0223 |
| baseline: __base | 0.6959 | persisted | 0.7112 | 144 | +0.0153 |
| baseline: __naive | 0.6978 | persisted | 0.7250 | 144 | +0.0272 |

Reading: the worst fold is the anomalous 144-match Jul–Oct 2023
complete-feed slice (actual over-rate 0.6181). On that fold X5
(0.7164) still beat Gate Zero (0.7217) and naive trailing-10
(0.7250), but lost to the base rate (0.7112): the pooled dev
margin was not uniform across folds. The sealed read nevertheless
cleared leg (i) outright and leg (ii) clean, so this stays
information, not a gate input.

## Artefacts

- `engine/cards/run_l1_k_id.py` — Lane 1 runner (gate_lib guards;
  refuses a second sealed read).
- `engine/cards/results_dev_l1.json` — dev evaluation +
  reproduction record (exact, diff 0.0).
- `engine/cards/results_virgin_l1.json` — the single sealed read.
- `engine/cards/dev_pass_registry_l1.json` — dev-pass token.
- `predictions/k_id_lane1_virgin_predictions.csv` +
  `engine/cards/fitted_params_virgin_l1.json` — virgin outputs for
  the shipped arm (X5), per the prereg's Outputs section.
- Original `results_dev.json` / `results_virgin.json` and the
  original verdict are untouched.
