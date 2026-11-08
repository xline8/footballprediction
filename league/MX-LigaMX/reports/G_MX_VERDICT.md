# G-MX Verdict — Liga MX goals model

Date: 2026-11-09. Branch `build/mx-ligamx`. Prereg:
`league/MX-LigaMX/prereg/PREREG_G_MX.md` (commit 8512c8d, frozen
before any fitting). Engine: `league/MX-LigaMX/engine/goals/`.
Implementation by Codex (gpt-5.6-luna) under the two-agent flow;
the coordinator independently re-ran the dev harness and reproduced
every pooled and per-block number (see Verification notes).
Predictions-only product: no Liga MX odds source exists in-system —
expected, not a defect.

## Verdict: FAIL — no arm passes the dev gate; virgin NOT read

Both arms beat climatology clearly on 1X2 LL and RPS, and both lose
the OU2.5 leg to the same climatology baseline. Under the frozen
rule the virgin window (2025/2026 - Clausura) is **deliberately NOT
read** — it stays virgin for one future read under a new prereg.
Nothing ships; no virgin predictions file exists for this candidate.

## Dev results (expanding block-blocked walk-forward, scored blocks = tournaments 2–9, n = 1,224)

Pooled:

| Arm | 1X2 LL | RPS | OU2.5 LL |
|---|---|---|---|
| Gate Zero | 1.0118 | 0.2085 | 0.7045 |
| X3 (set-play tilt) | 1.0136 | 0.2088 | 0.7112 |
| Climatology / base rate | 1.0726 | 0.2288 | **0.6981** |

Per-block 1X2 LL / OU2.5 LL:

| Block | GZ LL | X3 LL | Clim LL | GZ OU | X3 OU | Clim OU |
|---|---|---|---|---|---|---|
| 2021/2022 - Clausura | 1.0733 | 1.0972 | 1.1121 | 0.7142 | 0.7303 | 0.7124 |
| 2022/2023 - Apertura | 1.0436 | 1.0408 | 1.0817 | 0.7308 | 0.7343 | 0.7078 |
| 2022/2023 - Clausura | 1.0138 | 1.0018 | 1.0850 | 0.6998 | 0.6946 | 0.7047 |
| 2023/2024 - Apertura | 1.0275 | 1.0419 | 1.0659 | 0.7118 | 0.7230 | 0.6957 |
| 2023/2024 - Clausura | 1.0030 | 1.0023 | 1.0673 | 0.6965 | 0.6998 | 0.6930 |
| 2024/2025 - Apertura | 1.0010 | 0.9998 | 1.0575 | 0.6976 | 0.7051 | 0.6930 |
| 2024/2025 - Clausura | 0.9658 | 0.9611 | 1.0524 | 0.6854 | 0.6979 | 0.6893 |
| 2025/2026 - Apertura | 0.9667 | 0.9639 | 1.0592 | 0.6999 | 0.7045 | 0.6893 |

## Gate arithmetic

Dev gate (pooled 1X2 LL **and** RPS must beat climatology, and
OU2.5 LL must beat the base rate): Gate Zero passes LL (1.0118 <
1.0726) and RPS (0.2085 < 0.2288) but **FAILS the OU leg**
(0.7045 > 0.6981). X3 **FAILS** the same leg (0.7112 > 0.6981) and
is also worse than Gate Zero pooled on all three metrics (its
per-block sign check, 6/8 blocks with LL ≤ GZ, never arises). No
arm survives → virgin legs never arise.

Reading of the failure, recorded plainly: the Dixon-Coles pattern
prices 1X2 well here (it beats climatology in every scored block,
by widening margins as the window grows), but its OU2.5
probabilities are systematically a touch worse than the pooled
pre-block over-rate — the same failure shape as G-AR. Liga MX's
over-rate drifted upward across the window (38.6% in the warm-up
block to a 50–58% band), and the DC totals track it more slowly
than climatology's direct rate. That is a diagnosis for a possible
future prereg, **not** a rescue: the frozen pooled gate is the
gate, and it fails. There is no X2 arm in this league by design
(no movers exist — EDA F4), so nothing about the failure is a
thin-team artefact.

## Verification notes (coordinator, independent of Codex)

- Coordinator re-run of the dev harness reproduces the results
  file **exactly** (byte-identical JSON).
- Virgin isolation confirmed: the dev results contain only the
  eight scored blocks plus pooled rows; no `results_virgin.json`,
  no fitted virgin params and no predictions file were produced
  for this candidate, and the coordinator did not invoke the
  virgin path. (The harness's AR-inherited `passed or [gate_zero]`
  fallback was never executed.)
- X3's tilt was verified active (it diverges from Gate Zero in
  every scored block), so the failure is the arm's, not a wiring
  artefact.
