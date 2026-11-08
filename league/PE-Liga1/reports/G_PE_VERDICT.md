# Verdict — G-PE (Peru Liga 1 goals) — **FAIL** (dev gate; virgin NOT read)

Date: 2026-11-10. Branch `build/pe-liga1`. Prereg:
`league/PE-Liga1/prereg/PREREG_G_PE.md` (frozen in commit 2ca0c6f
before any fitting). Arms: Gate Zero, X2 (entrant prior: attack
replaced by −0.0645, defence by +0.1024 in a club's entry year).
Dev: block-blocked expanding walk-forward, seed 2021 - Fase 1 +
Fase 2 (n = 234), evaluation 2022 - Apertura … 2024 - Clausura
(pooled n = 982).

## Dev results (coordinator-verified; see Verification)

Pooled dev (n = 982):

| arm | 1X2 LL | RPS | OU2.5 LL |
|---|---|---|---|
| Gate Zero | 0.9571 | 0.19243 | 0.7092 |
| X2 | **0.9557** | **0.19199** | 0.7059 |
| climatology / base rate | 1.0416 | 0.22092 | **0.6934** |
| naive trailing-10 (reporting only) | 1.0891 | 0.20891 | 0.8044 |

Per-block model 1X2 LL (Gate Zero / X2):

| block | Gate Zero | X2 |
|---|---|---|
| 2022 - Apertura | 1.0270 | 1.0223 |
| 2022 - Clausura | 0.9312 | 0.9253 |
| 2023 - Apertura | 0.9663 | 0.9715 |
| 2023 - Clausura | 0.9804 | 0.9756 |
| 2024 - Apertura | 0.9164 | 0.9162 |
| 2024 - Clausura | 0.9132 | 0.9157 |

## Gate arithmetic (mechanical, prereg legs)

Dev gate — an arm must beat climatology on pooled 1X2 LL **and**
RPS, and beat the base rate on OU2.5 LL:

- **Gate Zero: LL 0.9571 < 1.0416 ✓; RPS 0.19243 < 0.22092 ✓;
  OU 0.7092 > 0.6934 ✗ — fails the OU leg.**
- X2: LL ✓ (0.9557), RPS ✓ (0.19199), OU 0.7059 > 0.6934 ✗ —
  fails the same leg independently.

Gate Zero failing its own dev gate makes the variant moot:
**verdict FAIL, virgin NOT read** (X2 also fails independently, so
no reading of the rule changes the outcome).

## Root cause, measured

The 1X2 side is strong — both arms beat climatology on LL and RPS
by wide margins. The totals side is not: the DC totals level loses
to the plain base rate on OU2.5, the same totals-calibration
failure family as G-COA, G-GE and G-BG2. X2 helps slightly where
it bites (2022 blocks, the entrant-heavy year) but an entrant
prior cannot repair a league-wide totals level.

## Verification performed

- Coordinator re-ran `run_g_pe.py dev` from the committed code:
  `results_dev.json` bit-identical to the Codex-produced file.
- Climatology pooled dev (LL 1.041613, RPS 0.220916, OU 0.693388)
  recomputed from the raw CSV through an independent script —
  exact match to 6 dp.
- `dc.py` is byte-identical to the proven CO-PrimeraA reference;
  `arms.py` inspected: X2 replaces an entrant's ratings with
  exactly −0.0645 / +0.1024, nothing else. The harness corpus
  filter (regular phase, non-awarded) and the dev loader's
  no-2025/2026 assertion were diff-verified against the prereg.
- The virgin entry point short-circuits on the dev gate:
  `engine/goals/results_virgin.json` records
  `{"virgin_read": false, "verdict": "FAIL"}` and no 2025 row was
  loaded by the virgin path.

## Virgin

**Deliberately NOT read.** Calendar 2025 (n = 323) remains
untouched as a virgin window for a future, separately
pre-registered design (a totals-level arm would be the natural
next attempt — NOT authorised here).

## What ships

Nothing. No predictions CSV, no fitted params, no pipeline join.
G-PE verdict: **FAIL**.
