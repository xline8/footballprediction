# Verdict — L1-K-CO (Colombia Primera A cards, Lane 1 re-entry) — **PROVISIONAL PASS** (sealed leg (ii) provisional; window read once, verdict final)

Date: 2026-11-11. Branch `build/lane1-kco`. Lane 1 candidate under
`league/IMPROVEMENT_PROGRAM.md` (cohort A, variants-moot; cohort
report §1.2/§1.5). Prereg: `league/CO-PrimeraA/prereg/PREREG_L1_K_CO.md`,
committed as this branch's FIRST commit **6557938e5d4c9d650f45c72668107713cf34f261**
("precedes any sealed access") before any sealed data was loaded.
Arm of record: **X8** (referee multiplier, K_REF = 8, clamp
[0.67, 1.50]). Gate Zero retained as baseline only — its dev veto
(the original prereg's "variants are moot" clause) is the
gate-architecture defect this entry corrects. Target: event-unified
yellows incl. second yellows, era 2023 - Apertura onward. Primary
line 5.5. Windows: seed 2023 - Apertura (n = 226), dev 2023 -
Clausura … 2025 - Clausura (n = 1,110), virgin 2026 - Apertura
(n = 204). All runs via `league/gate_lib/` (mechanical prereg
tokens, dev-pass assertion, sealed loader) under the P2 design
seal; runner: `engine/cards/run_l1_k_co.py`.

## Dev results — reproduction (pooled LL@5.5, n = 1,110)

| arm / baseline | documented | recomputed | abs diff |
|---|---|---|---|
| X8 (arm of record) | 0.6918 | 0.691751 (0.69175095) | 4.9e-05 |
| Gate Zero | 0.7001 | 0.700084 (0.70008415) | 1.6e-05 |
| league base rate | 0.6956 | 0.695579 (0.69557895) | 2.1e-05 |
| naive trailing-10 | 0.7080 | 0.707987 (0.70798710) | 1.3e-05 |

The documented dev pass reproduces within artefact rounding
(documented values are rounded to 4 decimal places; tolerance
5e-5). **Dev gate (X8): PASS** — 0.691751 beats BOTH baselines.
Gate Zero fails its own dev gate again (0.700084 > base rate
0.695579), as documented; under this preregistration that no
longer vetoes the arm of record. Dev-pass token recorded in
`engine/cards/dev_pass_registry_l1.json` (candidate `L1-K-CO`,
2026-11-11T12:01:51Z) before the sealed load.

Per-block LL@5.5 (Gate Zero / X8): 2023-Cl 0.694969 / 0.681371;
2024-Ap 0.701483 / 0.676639; 2024-Cl 0.714295 / 0.714026;
2025-Ap 0.700622 / 0.698707; 2025-Cl 0.689741 / 0.688329 — X8
beats Gate Zero in all 5 blocks.

## Sealed results — the single read (virgin 2026 - Apertura, n = 204 scored of 204 loaded)

| arm / baseline | LL@5.5 | calibration (predicted − actual) | SE |
|---|---|---|---|
| Gate Zero (reference) | 0.680909 | −2.600pp | 3.461pp |
| X8 (arm of record) | **0.665796** | −1.574pp | 3.413pp |
| league base rate | 0.694059 | — | — |
| naive trailing-10 | 0.684646 | — | — |

Actual over-5.5 rate 0.5196; X8 mean predicted 0.5039, Gate Zero
0.4936. Referee coverage in the window: 172/204 named (84.3%);
X8 fell back to Gate Zero behaviour on 56 fixtures (32 unknown
identity, 24 thin history — fewer than 8 priors).

## Gate arithmetic (mechanical, prereg legs — identical to PREREG_K_COA)

- **Leg (i) LL: PASS.** X8 virgin LL@5.5 0.665796 ≤ Gate Zero's
  0.680909 ✓, ≤ base rate 0.694059 ✓ and ≤ naive 0.684646 ✓.
  The referee multiplier beat the unmodified pattern and both
  baselines on the sealed season.
- **Leg (ii) calibration: PROVISIONAL.** |−1.574pp| > the 1.0pp
  clean boundary but within 1 SE of it (1.0 + 3.413 = 4.413pp)
  → PROVISIONAL PASS on this leg.
- **Leg (iii) sign check: PASS.** X8 dev LL ≤ Gate Zero dev LL
  in 5 of 5 dev blocks (≥ 3 required).

**Verdict: PROVISIONAL PASS.** One read, verdict final, no
iteration against the window. X8 ships as the arm of record
(subject to the runner-join preparation on this branch and the
operational condition below; no merge under this
preregistration). Virgin predictions written to
`predictions/k_coa_virgin_predictions.csv` (204 rows, arm `x8`)
and `engine/cards/fitted_params_virgin.json` (r_model = 66.87).
The original K-COA FAIL stands unrevised — this Lane 1 entry was
a new candidate judged on its own preregistration, on the window
the original build never read.

## P6 worst-fold block (dev, information only — no gate change)

Source: `league/CO-PrimeraA/engine/cards/results_dev_l1.json` via
`league/worst_fold/` (worst block by the reference arm, Gate Zero,
at ll_5.5).

### P6 worst-fold block — CO-PrimeraA cards (primary metric: ll_5.5)

Worst dev season (highest ll_5.5 for the reference arm): **2024 - Clausura**.

| Entity | Pooled ll_5.5 | Pooled source | Worst-season (2024 - Clausura) ll_5.5 | n (worst) | Δ vs pooled |
|---|---|---|---|---|---|
| gate_zero | 0.7001 | n-weighted, computed | 0.7143 | 216 | +0.0142 |
| gate_zero [base] | 0.6956 | n-weighted, computed | 0.7027 | 216 | +0.0072 |
| gate_zero [naive] | 0.7080 | n-weighted, computed | 0.7203 | 216 | +0.0124 |
| x8 | 0.6918 | n-weighted, computed | 0.7140 | 216 | +0.0223 |

Reading: on the hardest dev fold X8 (0.7140) still edged Gate
Zero (0.7143) — by only 0.0003 — but lost to the base rate's
worst-fold value (0.7027): the pooled dev margin was not uniform
across folds, and 2024 - Clausura is the fold where the referee
arm's edge nearly vanished. The sealed read nevertheless cleared
leg (i) outright, so this stays information, not a gate input.

## Operational condition and referee gate (shipping)

Operational condition (carried over from the original prereg):
referees with <8 prior era matches, or no named referee, fall
back to Gate Zero for that fixture (multiplier 1.0, fallback
recorded — no imputation); a PASS ships with this condition
attached.

Referee operational gate, run 2026-11-11 after the PASS: the 10
upcoming CO-PrimeraA fixtures in the daily runner's 2026-11-11
output (match ids 1000014227–1000014236, dated 2026-11-12 …
2026-11-14) were probed through the runner's own referee path
(`run_daily._cards_referees`, FotMob matchDetails
`infoBox.Referee`). **Named referees: 0/10.** FotMob is not
publishing CO-PrimeraA appointments pre-match for this matchday,
so if this join were merged today every live fixture would fall
back to Gate Zero behaviour (multiplier 1.0) and the shipped X8
arm would be inert in practice. **The verdict stands, but
shipping is blocked on this gate** — the runner-join preparation
on this branch is therefore prepared-but-blocked, and the merge
decision should wait until a matchday probe shows appointments
actually published pre-match (or the user accepts a Gate-Zero-
fallback-only live behaviour in the meantime).

## Artefacts

- `engine/cards/run_l1_k_co.py` — Lane 1 runner (gate_lib guards;
  refuses a second sealed read).
- `engine/cards/results_dev_l1.json` — dev evaluation +
  reproduction record.
- `engine/cards/results_virgin_l1.json` — the single sealed read.
- `engine/cards/dev_pass_registry_l1.json` — dev-pass token.
- `predictions/k_coa_virgin_predictions.csv` +
  `engine/cards/fitted_params_virgin.json` — virgin outputs for
  the shipped arm (X8), per the prereg's Outputs section.
- Original `results_dev.json` / `results_virgin.json` and the
  original verdict are untouched.
