# Verdict — L1-K-US (US-MLS cards, Lane 1 re-entry) — **FAIL** (sealed leg (ii); window read once, verdict final)

Date: 2026-11-11. Branch `build/lane1-kus`. Lane 1 candidate under
`league/IMPROVEMENT_PROGRAM.md` (cohort A, variants-moot; cohort
report §1.2/§1.5). Prereg: `league/US-MLS/prereg/PREREG_L1_K_US.md`,
committed as this branch's FIRST commit
**bdb4d3aa83fa2b8112892db19712fb6875c756a3** ("precedes any sealed
access") before any sealed data was loaded. Dev evaluation commit
18990221 (dev-pass token recorded there, before the sealed read).
Arm of record: **X8** (referee covariate, K_REF = 8, clamp
[0.67, 1.50]). Gate Zero retained as baseline only — its dev veto
(the original prereg's "variants are moot" clause) is the
gate-architecture defect this entry corrects. Target: total
unified yellows = `yellow_home + yellow_away` (stats feed).
Primary line 4.5. Windows: warm-up 2021, dev 2022–2024
(n = 1529 scored), virgin 2025 (n = 540). All leg arithmetic via
`league/gate_lib/` (pooled LL, per-match log-loss, calibration,
calibration band, sign check); runner:
`engine/cards/run_l1_k_us.py`. Original candidate:
`league/US-MLS/reports/K_US_VERDICT.md` (FAIL at the dev gate,
sealed window never read).

## Verdict: FAIL — at sealed leg (ii). Nothing ships.

X8 reproduced its documented dev pass exactly and was read once
on the sealed window 2025 (n=540). On that window it **passes leg
(i)** — its LL@4.5 (0.674312) beats Gate Zero's (0.676249) and
both baselines — and **passes leg (iii)** (sign check 2/3), but
**fails leg (ii) outright**: calibration is −4.22pp
(predicted − actual), SE 2.11pp, beyond the 1.0pp tolerance and
beyond the 1 SE provisional boundary (3.11pp). Both arms
under-predicted the sealed season's card level (actual over-4.5
rate 0.4204 against a dev pooled actual of 0.4029 and an X8 mean
prediction of 0.3782). Legs are conjunctive: FAIL, verdict final,
no iteration against the window.

No runner-join change is prepared (join preparation is PASS-only
under the protocol), and the referee operational gate is not run
(it gates shipping, and nothing ships).

## Dev results — reproduction (pooled LL@4.5, n = 1529)

| arm / baseline | documented | recomputed | abs diff |
|---|---|---|---|
| X8 (arm of record) | 0.670898 | 0.670898 (0.67089840) | 4.0e-07 |
| Gate Zero | 0.678407 | 0.678407 (0.67840706) | 5.8e-08 |
| league base rate | 0.677134 | 0.677134 (0.67713350) | 5.0e-07 |
| naive trailing-10 | 0.682714 | 0.682714 (0.68271413) | 1.3e-07 |

The documented dev pass reproduces within artefact rounding.
**Dev gate (X8): PASS** — 0.670898 beats BOTH baselines. Gate Zero
fails its own dev gate again (0.678407 > base rate 0.677134), as
documented; under this preregistration that no longer vetoes the
arm of record. Dev-pass token recorded in
`engine/cards/dev_pass_registry_l1.json` (candidate `L1-K-US`,
2026-11-11T12:03:18Z) before the sealed load.

Per-season LL@4.5 (Gate Zero / X8): 2022 0.706163 / 0.714217;
2023 0.676576 / 0.666706; 2024 0.654393 / 0.634751 — X8 beats
Gate Zero in 2 of 3 dev seasons.

## Sealed results — the single read (virgin 2025, n = 540 scored of 540 loaded)

Loaded once through gate_lib's fail-closed `load_sealed_rows`
(which asserted the recorded dev-pass token first), online
walk-forward continuing from the dev end state. Full numbers in
`engine/cards/results_virgin_l1.json`; arm-of-record predictions
in `predictions/k_us_virgin_predictions.csv` (evidence of the
read, not a shipped product; the file is gitignored under the
tree's `*.csv` rule and lives in this worktree only).

| arm / baseline | LL@4.5 | calibration (predicted − actual) | SE |
|---|---|---|---|
| **X8 (arm of record)** | **0.674312** (0.67431152) | −4.220pp | 2.105pp |
| Gate Zero (reference) | 0.676249 (0.67624913) | −4.067pp | 2.109pp |
| league base rate | 0.684326 | — | — |
| naive trailing-10 | 0.695332 | — | — |

Actual over-4.5 rate 0.4204; X8 mean predicted 0.3782, Gate Zero
0.3797. Referee coverage in the window: 519/540 named (96.1%,
matching the original prereg's published figure); X8 fell back
to Gate Zero behaviour on 56 fixtures (21 unknown identity, 35
thin history — fewer than 8 priors).

## Gate arithmetic (mechanical, prereg legs — identical to PREREG_K_US)

- **Leg (i) LL: PASS.** X8 virgin LL@4.5 0.674312 ≤ Gate Zero
  0.676249 ✓, ≤ base rate 0.684326 ✓ and ≤ naive 0.695332 ✓.
  The referee covariate won the discrimination leg on the sealed
  season.
- **Leg (ii) calibration: FAIL.** |−4.220pp| > 1.0pp clean
  boundary and beyond 1 SE of it (1.0 + 2.105 = 3.105pp);
  gate_lib `calibration_band`: FAIL. Gate Zero itself is
  −4.067pp (SE 2.109pp) — also FAIL band: the level miss is in
  the shared pattern, not in the referee adjustment.
- **Leg (iii) sign check: PASS.** X8 dev LL ≤ Gate Zero dev LL
  in 2 of 3 dev seasons (≥ 2 required).

**Verdict: FAIL.** One read, verdict final, no iteration against
the window. Nothing ships: no runner join prepared, no fitted
params written for shipping, and the referee operational gate
is not run (PASS-only). The original K-US FAIL stands unrevised
— this Lane 1 entry was a new candidate judged on its own
preregistration, and it failed on the window the original build
never read.

## P6 worst-fold block (dev, information only — no gate change)

Source: `league/US-MLS/engine/cards/results_dev.json` via
`league/worst_fold/` (worst season by the reference arm, Gate
Zero, at ll_4.5).

### P6 worst-fold block — US-MLS cards (primary metric: ll_4.5)

Worst dev season (highest ll_4.5 for the reference arm): **2022**.

| Entity | Pooled ll_4.5 | Pooled source | Worst-season (2022) ll_4.5 | n (worst) | Δ vs pooled |
|---|---|---|---|---|---|
| gate_zero | 0.6784 | n-weighted, computed | 0.7062 | 486 | +0.0278 |
| gate_zero [base] | 0.6771 | n-weighted, computed | 0.6849 | 486 | +0.0077 |
| gate_zero [naive] | 0.6827 | n-weighted, computed | 0.6840 | 486 | +0.0013 |
| x8 | 0.6709 | n-weighted, computed | 0.7142 | 486 | +0.0433 |

Reading: on the hardest dev fold X8 (0.7142) was worse than Gate
Zero (0.7062) and both baselines — 2022 is the season X8 loses in
the sign check, and the pooled dev margin rests on 2023–2024.
That weakness was visible in dev and is not what decided the
verdict: on the sealed window X8 won the LL leg anyway, and the
candidate fell on calibration, a level miss shared with Gate
Zero.

## Verification notes

- Dev reproduction: all four pooled numbers within 5e-07 of the
  documented values; the original `results_dev.json` /
  `results_dev.csv` artefacts are untouched (the runner snapshots
  and restores them; the Lane 1 record is `results_dev_l1.json`).
- Sealed cross-check: the sealed walk-forward was recomputed
  with the league's original harness (`virgin_metrics()`, run in
  a /tmp copy) — X8 LL@4.5 0.6743115232927259, base 0.6843259294,
  naive 0.6953318699, calibration −0.04220356 (SE 0.02105336),
  coverage 519/540, fallbacks 21/35: identical to this run's
  gate_lib numbers to every printed digit.
- The original harness's own virgin verdict writer cannot be
  used: it crashes with `KeyError: 'gate_zero'` whenever Gate
  Zero is not itself a dev-passing arm (reproduced in the /tmp
  cross-check, after `results_virgin.json` was written) — the
  §5.6-class virgin-verdict-writer trap named in the tasking.
  All leg arithmetic here is gate_lib's. The crash changes
  nothing: under the harness's own calibration token
  (|diff| ≤ 0.01 or ≤ SE), 0.0422 > 0.0211 also fails, and
  leg (ii) fails independently under either reading.
- The engine's NB r estimates sit at the capped 500.0 for all
  methods in both windows, exactly as in the original documented
  run — the reproduction target — and are unchanged by this entry.

## Artefacts

- `engine/cards/run_l1_k_us.py` — Lane 1 runner (gate_lib guards;
  refuses a second sealed read).
- `engine/cards/results_dev_l1.json` — dev evaluation +
  reproduction record.
- `engine/cards/results_virgin_l1.json` — the single sealed read.
- `engine/cards/dev_pass_registry_l1.json` — dev-pass token.
- `predictions/k_us_virgin_predictions.csv` — X8 sealed
  predictions, evidence of the read (worktree-local, gitignored).
- Original `results_dev.json` / `results_virgin.json` (absent, as
  before) and the original verdict are untouched.
