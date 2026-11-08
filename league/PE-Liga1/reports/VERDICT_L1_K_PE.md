# Verdict — L1-K-PE (Peru Liga 1 cards, Lane 1 re-entry) — **FAIL** (sealed leg (i); window read once, verdict final)

Date: 2026-11-11. Branch `build/lane1-kpe`. Lane 1 candidate under
`league/IMPROVEMENT_PROGRAM.md` (cohort A, variants-moot; cohort
report §1.2/§1.5). Prereg: `league/PE-Liga1/prereg/PREREG_L1_K_PE.md`,
committed as this branch's FIRST commit **4ce8a892e03834089daba1a55b9ce6a456ecedff**
("precedes any sealed access") before any sealed data was loaded.
Arm of record: **X8** (referee multiplier, K_REF = 8, clamp
[0.67, 1.50]). Gate Zero retained as baseline only — its dev veto
(the original prereg's "variants are moot" clause) is the
gate-architecture defect this entry corrects. Target: event-unified
yellows incl. second yellows, era 2023+. Primary line 4.5. Windows:
seed 2023 - Apertura (n = 165), dev 2023 - Clausura … 2024 -
Clausura (n = 475), virgin calendar 2025 (n = 323). All runs via
`league/gate_lib/` (mechanical prereg tokens, dev-pass assertion,
sealed loader) under the P2 design seal; runner:
`engine/cards/run_l1_k_pe.py`.

## Dev results — reproduction (pooled LL@4.5, n = 475)

| arm / baseline | documented | recomputed | abs diff |
|---|---|---|---|
| X8 (arm of record) | 0.687450 | 0.687450 (0.68744953) | 4.7e-07 |
| Gate Zero | 0.712602 | 0.712602 (0.71260154) | 4.6e-07 |
| league base rate | 0.707846 | 0.707846 (0.70784560) | 4.0e-07 |
| naive trailing-10 | 0.692826 | 0.692826 (0.69282579) | 2.1e-07 |

The documented dev pass reproduces within artefact rounding.
**Dev gate (X8): PASS** — 0.687450 beats BOTH baselines. Gate Zero
fails its own dev gate again (0.712602 > both baselines), as
documented; under this preregistration that no longer vetoes the
arm of record. Dev-pass token recorded in
`engine/cards/dev_pass_registry_l1.json` (candidate `L1-K-PE`,
2026-11-11T11:59:48Z) before the sealed load.

Per-block LL@4.5 (Gate Zero / X8): 2023-Cl 0.738593 / 0.725063;
2024-Ap 0.685894 / 0.646464; 2024-Cl 0.710599 / 0.686887 — X8 beats
Gate Zero in all 3 blocks.

## Sealed results — the single read (virgin 2025, n = 323 scored of 323 loaded)

| arm / baseline | LL@4.5 | calibration (predicted − actual) | SE |
|---|---|---|---|
| Gate Zero (reference) | **0.680517** | −2.654pp | 2.747pp |
| X8 (arm of record) | 0.690626 | −3.376pp | 2.771pp |
| league base rate | 0.695697 | — | — |
| naive trailing-10 | 0.693133 | — | — |

Actual over-4.5 rate 0.5077; X8 mean predicted 0.4740, Gate Zero
0.4812. Referee coverage in the window: 260/323 named (80.5%,
matching the original prereg's figure); X8 fell back to Gate Zero
behaviour on 125 fixtures (63 unknown identity, 62 thin history —
fewer than 8 priors).

## Gate arithmetic (mechanical, prereg legs — identical to PREREG_K_PE)

- **Leg (i) LL: FAIL.** X8 virgin LL@4.5 0.690626 ≤ base rate
  0.695697 ✓ and ≤ naive 0.693133 ✓, but **> Gate Zero's 0.680517
  ✗**. The referee multiplier that won every dev block lost to
  the unmodified pattern on the sealed season: in 2025 Gate Zero
  itself beat both baselines, and X8's adjustments subtracted
  value (era drift — the failure mode the cohort report flagged
  for this candidate).
- **Leg (ii) calibration: PROVISIONAL band, moot.** |−3.376pp| >
  1.0pp clean boundary but within 1 SE of it (1.0 + 2.771 =
  3.771pp). Would have recorded PROVISIONAL PASS had legs (i)
  and (iii) passed; it cannot rescue leg (i).
- **Leg (iii) sign check: PASS.** X8 dev LL ≤ Gate Zero dev LL in
  3 of 3 dev blocks (≥ 2 required).

**Verdict: FAIL.** One read, verdict final, no iteration against
the window. Nothing ships: no virgin predictions CSV, no fitted
params, no runner join prepared (join preparation is PASS-only
under the protocol; the referee operational gate is likewise not
run). The original K-PE FAIL stands unrevised — this Lane 1 entry
was a new candidate judged on its own preregistration, and it
failed on the window the original build never read.

## P6 worst-fold block (dev, information only — no gate change)

Source: `league/PE-Liga1/engine/cards/results_dev_l1.json` via
`league/worst_fold/` (worst block by the reference arm, Gate Zero,
at ll_4.5).

### P6 worst-fold block — PE-Liga1 cards (primary metric: ll_4.5)

Worst dev season (highest ll_4.5 for the reference arm): **2023 - Clausura**.

| Entity | Pooled ll_4.5 | Pooled source | Worst-season (2023 - Clausura) ll_4.5 | n (worst) | Δ vs pooled |
|---|---|---|---|---|---|
| gate_zero | 0.7126 | n-weighted, computed | 0.7386 | 169 | +0.0260 |
| gate_zero [base] | 0.7078 | n-weighted, computed | 0.7274 | 169 | +0.0195 |
| gate_zero [naive] | 0.6928 | n-weighted, computed | 0.7089 | 169 | +0.0161 |
| x8 | 0.6874 | n-weighted, computed | 0.7251 | 169 | +0.0376 |

Reading: even on the hardest dev fold X8 (0.7251) beat Gate Zero
(0.7386) and both baselines' worst-fold values — the dev evidence
was genuinely strong on every fold, which is exactly why the
sealed reversal is informative rather than a dev artefact: the
referee edge did not survive the 2025 era.

## Artefacts

- `engine/cards/run_l1_k_pe.py` — Lane 1 runner (gate_lib guards;
  refuses a second sealed read).
- `engine/cards/results_dev_l1.json` — dev evaluation +
  reproduction record.
- `engine/cards/results_virgin_l1.json` — the single sealed read.
- `engine/cards/dev_pass_registry_l1.json` — dev-pass token.
- Original `results_dev.json` / `results_virgin.json` and the
  original verdict are untouched.
