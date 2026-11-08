# G-NLE Verdict — Eerste Divisie goals model

Date: 2026-11-09. Branch `build/nl-eerste`. Prereg:
`league/NL-EersteDivisie/prereg/PREREG_G_NLE.md` (commit f267312,
frozen before any fitting). Engine:
`league/NL-EersteDivisie/engine/goals/`. Implementation by Codex
(gpt-5.6-luna) under the two-agent flow; every number below was
recomputed independently by the coordinator from the engine's
per-match dev predictions CSV and the league CSV (1X2 LL, RPS, OU
LL and the climatology baseline all reproduced exactly).
Calibration is stated as actual − predicted throughout this build.

## Verdict: FAIL — every arm dies at the dev gate (OU2.5 leg); virgin NOT read

All three arms beat climatology on 1X2 LL and RPS, and all three
lose the OU2.5 leg to the base-rate baseline on pooled dev — the
same shape as G-NL (Eredivisie) and most of the program. Under the
frozen legs no arm passes dev, so the virgin window was **not
read** (the ported harness's fallback virgin path was removed by
brief; no 2025/2026 outcome was evaluated for this candidate) and
**nothing ships**.

## Dev results (expanding season-blocked walk-forward, scored 2022/2023–2024/2025, n = 1140)

| Season | GZ LL / OU | SHRINK LL / OU | X2 LL / OU | Climatology LL / OU |
|---|---|---|---|---|
| 2022/2023 | 1.0835 / 0.7303 | 1.0835 / 0.7303 | 1.0531 / 0.7196 | 1.0508 / 0.6751 |
| 2023/2024 | 1.0538 / 0.6938 | 1.0538 / 0.6938 | 1.0700 / 0.6789 | 1.0702 / 0.6720 |
| 2024/2025 | 1.0230 / 0.6891 | 1.0230 / 0.6891 | 1.0259 / 0.6892 | 1.0602 / 0.6741 |
| **Pooled** | **1.0534 / 0.7044** | **1.0534 / 0.7044** | **1.0497 / 0.6959** | 1.0604 / **0.6737** |

Pooled RPS: GZ 0.2287, SHRINK 0.2287, X2 0.2271, climatology
0.2321.

Dev gate (pooled 1X2 LL **and** RPS beat climatology **and** OU2.5
LL beats the base-rate baseline): Gate Zero **FAIL** (OU 0.7044 >
0.6737). SHRINK **FAIL** (identical numbers — see below). X2
**FAIL** (OU 0.6959 > 0.6737; its 1X2 LL 1.0497 and RPS 0.2271 are
the best of the three arms, so the relegated-club prior carries
real result signal, but it does not fix the totals distribution).

Two plain findings:

- **SHRINK is vacuous in this harness.** Under season-blocked
  fitting every non-mover team has ≥ 38 training matches (shrink
  factor 1.0) and every mover has 0 (rating 0 × 0 = 0, the league
  mean it starts from anyway). The arm can never bind; its
  byte-identical results are correct, not a bug. A shrink arm only
  has content under per-match refits.
- The DC ratings again carry genuine 1X2 signal (LL ~1.05 vs
  1.06 climatology, RPS clearly better) while the total-goals
  distribution loses to the league's own over-rate in a league
  whose OU2.5 over-rate sits near 60% every season. The gate is
  doing its job.

## Virgin window — NOT read

No arm passed dev. No virgin metrics, no fitted params, no
predictions file for G-NLE. 2026/2027 was never touched.
