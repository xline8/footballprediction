# G-AR Verdict — Liga Profesional goals model

Date: 2026-11-09. Branch `build/ar-liga`. Prereg:
`league/AR-LigaProfesional/prereg/PREREG_G_AR.md` (commit 7169cb5,
frozen before any fitting). Engine:
`league/AR-LigaProfesional/engine/goals/`. Implementation by Codex
(gpt-5.6-luna) under the two-agent flow; the dev run was reproduced
by the coordinator's own rerun with identical numbers (see
Verification notes). Predictions-only product: no Liga Profesional
odds source exists in-system — expected, not a defect.

## Verdict: FAIL — no arm passes the dev gate; virgin NOT read

All three arms lose the pooled dev gate to climatology on the 1X2
log-loss and RPS legs, and lose the OU2.5 leg to the base-rate
baseline. Under the frozen rule the virgin window (2026 - Clausura)
is **deliberately NOT read** — it stays virgin for one future read
under a new prereg. Nothing ships; no virgin predictions file
exists for this candidate.

## Dev results (expanding block-blocked walk-forward, scored blocks 2022 – 2026 - Apertura, n = 1,854)

Pooled:

| Arm | 1X2 LL | RPS | OU2.5 LL |
|---|---|---|---|
| Gate Zero | 1.0779 | 0.2167 | 0.6502 |
| X2 (newcomer priors −0.12/+0.18) | 1.0771 | 0.2165 | 0.6510 |
| X3 (X2 + set-play tilt) | 1.0834 | 0.2184 | 0.6548 |
| Climatology / base rate | **1.0739** | **0.2159** | **0.6456** |

Per-block 1X2 LL:

| Block | Gate Zero | X2 | X3 | Climatology |
|---|---|---|---|---|
| 2022 | 1.1172 | 1.1215 | 1.1215 | 1.0754 |
| 2023 | 1.0668 | 1.0666 | 1.0666 | 1.0665 |
| 2024 | 1.0685 | 1.0720 | 1.0903 | 1.0604 |
| 2025 - Apertura | 1.0623 | 1.0562 | 1.0723 | 1.0694 |
| 2025 - Clausura | 1.0975 | 1.0975 | 1.1084 | 1.0990 |
| 2026 - Apertura | 1.0440 | 1.0325 | 1.0255 | 1.0838 |

## Gate arithmetic

Dev gate (pooled 1X2 LL **and** RPS must beat climatology, and
OU2.5 LL must beat the base rate): Gate Zero **FAIL** (1.0779 >
1.0739; 0.2167 > 0.2159; 0.6502 > 0.6456). X2 **FAIL** (1.0771 >
1.0739; OU 0.6510 > 0.6456). X3 **FAIL** (worse than Gate Zero on
every leg). No arm survives → virgin legs never arise.

Reading of the failure, recorded plainly: the Dixon-Coles pattern
is dragged under climatology by the early scored blocks — 2022 is
fitted on 2021 alone (1.1172 vs 1.0754) and 2024 also loses —
while it **wins the last three scored blocks**, including a wide
win in 2026 - Apertura (X3 1.0255 vs 1.0838), as the xG era
(xG exists only from 2023) accumulates into the training window.
That trajectory is a diagnosis for a possible future prereg (e.g.
an xG-era-restricted design), **not** a rescue: the frozen pooled
gate is the gate, and it fails. Two port behaviours were verified
as correct, not bugs: X3 ≡ X2 exactly in 2022–2023 (the set-play
tilt needs ≥8 xG matches in the training window; the 2021–2022
training windows contain no xG, so the multiplier is 1.0 by the
preregistered rule), and X2's newcomer offsets use the AR
magnitudes (−0.12/+0.18), not another league's.

## Verification notes (coordinator, independent of Codex)

- Coordinator rerun of the dev harness reproduces every pooled
  and per-block number exactly.
- Virgin isolation confirmed: the dev results contain only the
  six scored blocks; no `results_virgin.json` and no predictions
  file were produced for this candidate, and the coordinator did
  not invoke the virgin path.
- X3≡X2 identity in 2022–2023 verified as the preregistered
  min-8-xG-matches inactivity (see above), not a key bug: X3
  diverges from X2 from 2024 onward, when the training window
  first contains xG-era matches.
