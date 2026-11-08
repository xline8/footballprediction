# K-MX Verdict — Liga MX cards model

Date: 2026-11-09. Branch `build/mx-ligamx`. Prereg:
`league/MX-LigaMX/prereg/PREREG_K_MX.md` (commit 8512c8d, frozen
before any fitting). Target: event-derived unified yellows (the
stats-vs-events check in `EDA.md` F9 showed stats undercounting
in every dev tournament; the decision was frozen on dev-era
evidence before any virgin read). Engine:
`league/MX-LigaMX/engine/cards/`. Implementation by Codex
(gpt-5.6-luna) under the two-agent flow; the coordinator
independently re-ran the dev harness and reproduced every number
(see Verification notes). Predictions-only product: no Liga MX
card odds source exists in-system — expected, not a defect.

## Verdict: FAIL — no arm passes the dev gate; virgin NOT read

Gate Zero loses to **both** baselines pooled. The X8 referee arm
clearly improves on Gate Zero and beats the naive baseline, but
still loses to the plain league base rate. Under the frozen rule
the virgin window (2025/2026 - Clausura) is **deliberately NOT
read** — it stays virgin for one future read under a new prereg,
e.g. a referee model redesigned around this dev evidence.
Nothing ships.

## Dev results (per-match walk-forward, scored blocks = tournaments 2–9, n = 1,224; LL@4.5)

Pooled:

| Arm | LL@4.5 | vs base 0.6955 | vs naive 0.7015 |
|---|---|---|---|
| Gate Zero | 0.7041 | **FAIL** | **FAIL** |
| X8 (referee arm) | 0.6975 | **FAIL** (by 0.0020) | pass |
| League base rate | 0.6955 | — | — |
| Naive trailing-10 | 0.7015 | — | — |

Per-block LL@4.5:

| Block | GZ | X8 | Base | Naive |
|---|---|---|---|---|
| 2021/2022 - Clausura | 0.7271 | 0.7198 | 0.7112 | 0.7099 |
| 2022/2023 - Apertura | 0.7102 | 0.6833 | 0.7010 | 0.6993 |
| 2022/2023 - Clausura | 0.7050 | 0.6864 | 0.6897 | 0.7071 |
| 2023/2024 - Apertura | 0.7020 | 0.7030 | 0.6977 | 0.7100 |
| 2023/2024 - Clausura | 0.6976 | 0.6912 | 0.6941 | 0.6979 |
| 2024/2025 - Apertura | 0.6828 | 0.6674 | 0.6808 | 0.6905 |
| 2024/2025 - Clausura | 0.7006 | 0.7179 | 0.6836 | 0.7006 |
| 2025/2026 - Apertura | 0.7074 | 0.7110 | 0.7058 | 0.6964 |

Sign check (X8 dev LL ≤ GZ, of 8): 6/8 — X8 is the better model
in six blocks, often by a wide margin (2022/2023 - Apertura
0.6833 vs 0.7102; 2024/2025 - Apertura 0.6674 vs 0.6828). What
sinks it pooled is two blocks, above all 2024/2025 - Clausura
(0.7179 vs base 0.6836) and the final block (0.7110 vs naive
0.6964).

## Gate arithmetic

Dev gate (pooled LL@4.5 must beat BOTH baselines): Gate Zero
**FAIL** both legs; X8 beats naive (0.6975 < 0.7015) but **FAILS**
the base-rate leg (0.6975 > 0.6955). No arm passes → virgin legs
never arise → **K-MX is FAIL; nothing ships.**

Recorded plainly, in the J1-K spirit: the referee signal is real
in this league (EDA split-half reliability r = 0.331, and X8
improves Gate Zero pooled by 0.0066 and in 6 of 8 blocks — a
much stronger showing than the same arm managed in AR dev), but
the frozen AR form (HL = 270, K = 8, clamp [0.8, 1.25], venue-
mirrored attack/defence ratings underneath) does not clear the
base rate pooled, and the gate is the gate. The last two blocks
also carry the league's referee-coverage collapse (95–100%
through 2024/2025 - Clausura → 24.8% / 58.2% in the last dev
block and the virgin block): unnamed referees fall back to
factor 1.0, and in 2024/2025 - Clausura the arm was nonetheless
much worse than its own Gate Zero — the mechanism is not
established from dev data alone and is **not** investigated with
virgin data. A redesigned cards prereg (different referee
shrinkage, or a target/feature rethink) is future work under a
new registration; this verdict closes the frozen one.

## Verification notes (coordinator, independent of Codex)

- Coordinator re-run of the dev harness reproduces the results
  file **exactly** (byte-identical JSON), including the harness's
  own printed dev-gate flags (False for both arms).
- The X8 factor was verified genuinely active in the dev run
  (fitted dispersion identical across arms, r = 14.31 — the
  difference is the referee multiplier, not a second fit).
- Virgin isolation confirmed: no `results_virgin.json`, no fitted
  virgin params and no predictions file exist for this candidate;
  the coordinator did not invoke the virgin path. The AR-inherited
  AR halves constants found in the cards virgin helper during
  review were corrected to the MX constants (0.385/0.615) for the
  record, but that path was never run.
