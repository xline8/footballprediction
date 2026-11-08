# G-IRPG Verdict — Persian Gulf Pro League goals model

Date: 2026-11-10. Branch `build/ir-persian-gulf`. Prereg:
`league/IR-PersianGulf/prereg/PREREG_G_IRPG.md` (commit b8ef70bf,
frozen before any fitting). Engine:
`league/IR-PersianGulf/engine/goals/`. Implementation: Codex
(gpt-5.6-luna) copied `dc.py` byte-identical from the Azadegan
engine and adapted `arms.py` (added X2) + `harness.py` + the CLI
runner; the coordinator ran the dev harness and the
`virgin-metrics` sentinel path. Every number below was verified
independently by the coordinator: the climatology baseline was
recomputed from the CSV with fresh code and matches the engine
exactly to 6 decimals on all three metrics (pooled and per season);
`dc.py` is byte-identical to the Azadegan copy (`cmp` clean);
the SHRINK lambda-change count (0) and the X2 lambda-change count
(174) were measured by re-running the arm comparison over all 720
scored dev matches; two hand spot-checks recomputed X2 lambdas
from the fitted ratings and matched exactly (Paykan vs Malavan,
2022-08-12: 1.086395 / 0.776910; Shams Azar vs Havadar,
2023-08-16: 1.099364 / 0.853287); the dev run was repeated and
reproduced identical numbers (identical md5 6faad54b2025c1b9965c09bae6d62dfb
across four runs). Calibration is stated as actual − predicted
throughout this build.

## Verdict: FAIL — every arm dies at the dev gate (OU2.5 leg); virgin NOT read

All three arms beat climatology on pooled 1X2 LL and RPS, and all
three lose the OU2.5 leg to the base-rate baseline on pooled dev —
the same shape as G-IRAZ, G-NLTD, G-NLE, and G-ESPF, mirrored the
same way: this league is low-scoring (scored-dev over-2.5 rate
32.5%) and the under-rate baseline is strong. Under the frozen
legs no arm passes dev, so the virgin window was **not read** (the
runner wrote `results_virgin.json`:
`{"virgin_read": false, "reason": "no arm passed the dev gate"}`;
no 2025/2026 outcome was evaluated, no predictions file exists, no
fitted params exist) and **nothing ships**.

## Dev results (expanding season-blocked walk-forward, scored 2022/2023–2024/2025, n = 720)

| Season | GZ LL / RPS / OU | SHRINK LL / RPS / OU | X2 LL / RPS / OU | Climatology LL / RPS / OU |
|---|---|---|---|---|
| 2022/2023 | 0.9834 / 0.1836 / 0.6151 | 0.9834 / 0.1836 / 0.6151 | 0.9690 / 0.1795 / 0.6149 | 1.0921 / 0.2163 / 0.6258 |
| 2023/2024 | 1.0193 / 0.1997 / 0.6726 | 1.0193 / 0.1997 / 0.6726 | 1.0193 / 0.1995 / 0.6710 | 1.1004 / 0.2246 / 0.6523 |
| 2024/2025 | 1.0642 / 0.2083 / 0.6424 | 1.0642 / 0.2083 / 0.6424 | 1.0628 / 0.2081 / 0.6408 | 1.0926 / 0.2189 / 0.6180 |
| **Pooled** | **1.0223 / 0.1972 / 0.6434** | **1.0223 / 0.1972 / 0.6434** | **1.0170 / 0.1957 / 0.6422** | **1.0950 / 0.2199 / 0.6320** |

Dev gate (pooled 1X2 LL **and** RPS beat climatology **and** OU2.5
LL beats the base-rate baseline): Gate Zero **FAIL** (OU 0.6434 >
0.6320, loses by 0.0113). SHRINK **FAIL** (identical numbers — see
below). X2 **FAIL** (OU 0.6422 > 0.6320, loses by 0.0102 — the
closest arm, still short).

Three plain findings:

- **The ratings carry genuine 1X2 signal, and the totals
  distribution does not.** Pooled LL 1.0223 vs 1.0950 and RPS
  0.1972 vs 0.2199 are real wins, and the model beats climatology
  on LL and RPS in **all three** scored seasons individually.
  But the model loses the OU2.5 leg in **two of three** seasons
  (2023/2024 by 0.0203, 2024/2025 by 0.0243; it wins 2022/2023
  by 0.0107): its predicted totals are systematically too high
  for a league whose over-2.5 rate sits at 31–35%. This is the
  Azadegan failure with a smaller margin — the sibling lost the
  pooled OU leg by 0.0258; here it is 0.0113 (GZ) / 0.0102 (X2).
- **X2 helps on every metric in every season — just not enough.**
  The frozen entrant offset improves LL, RPS, and OU2.5 LL vs Gate
  Zero in all three scored seasons (pooled LL −0.0053, RPS
  −0.0015, OU −0.0012), on 174/720 matches involving an unseen
  team. The EDA F4 direction was real: entrants really do arrive
  below the league mean, and pricing that in helps. But the OU
  improvement is an order of magnitude smaller than the gap to
  the baseline, so the arm dies on the same leg. The X2
  experiment is a *validated direction with an insufficient
  magnitude*, not a failed idea — and no rescue is permitted: the
  prereg is frozen, and a larger offset fitted after seeing dev
  would be post-hoc.
- **SHRINK is vacuous in this harness, as pre-recorded.** Under
  season-blocked fitting every non-entrant team has ≥ 30 training
  matches (shrink factor 1.0) and every entrant has 0 (rating 0 ×
  0 = 0, the league mean it starts from anyway). The arm changed
  0 of 720 scored lambdas; its byte-identical results are
  correct, not a bug. A shrink arm only has content under
  per-match refits.

## Virgin window — NOT read

The virgin window (2025/2026, partial, rounds 1–23, n = 178) was
not evaluated for any arm. Its descriptive levels (1.82
goals/match, 28.7% over-2.5) are lower-scoring than scored dev
(2.05, 32.5%), so the virgin regime would likely have been harder
still — but the gate decided first, and no claim is made about it.
The 2026/2027 confirmatory window (18-team expansion, in
progress) remains reserved; a future re-read of either window
would need a fresh prereg, not a reopening of this one.

## What ships

Nothing. No fitted params, no predictions file, no market joins
the daily runner. The league is complete as a build (its only
buildable candidate ran its full gate), with 0 passing markets —
the same terminal state as the Azadegan sibling. The durable
assets are the verified data build (1,243 league matches), the
EDA record (notably the F4 entrant gaps and the F6 card feed
break), and the X2 evidence: a pre-registered entrant prior that
improves every dev metric, for a future build to reuse — with a
fresh prereg — if the program ever revisits a totals model for a
low-scoring league.
