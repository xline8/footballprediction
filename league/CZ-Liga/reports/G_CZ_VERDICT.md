# Verdict — G-CZ (CZ-Liga goals, Dixon–Coles goals-only)

**FAIL — dev gate (OU2.5 leg). Virgin NOT read. Nothing ships.**

Dev (pooled, n = 810; walk-forward season-blocked, evaluation
2022/2023–2024/2025):

| Arm | 1X2 LL | RPS | OU2.5 LL | vs climatology (1.070348 / 0.231878 / 0.689911) |
|---|---|---|---|---|
| Gate Zero | 0.972997 | 0.198592 | **0.698004** | LL ✓, RPS ✓, OU ✗ |
| SHRINK | 0.972997 | 0.198592 | 0.698004 | identical to Gate Zero (see note) |
| X2 | 0.973323 | 0.198530 | 0.697444 | LL ✓, RPS ✓, OU ✗ |

Gate arithmetic (PREREG_G_CZ): the dev gate requires pooled 1X2 LL
and RPS to beat climatology AND OU2.5 LL to beat the base-rate
baseline. Gate Zero's OU2.5 LL 0.698004 > climatology 0.689911 →
**Gate Zero fails the dev gate**; per the frozen mechanical reading,
the variants are moot and the virgin window was NOT read
(`engine/goals/results_virgin.json`: `virgin_read: false`).

Per-season OU2.5 LL (model vs climatology): 2022/2023 0.725476 vs
0.681527 (the failure is concentrated here — the season after the
seed, when ratings are thinnest); 2023/2024 0.687245 vs 0.696497 ✓;
2024/2025 0.681291 vs 0.691711 ✓. The 1X2/RPS legs pass comfortably
in every season; the totals leg does not survive pooling.

Notes:
- SHRINK ≡ Gate Zero to all printed digits, by construction: under
  season-blocked fitting a team's prior in-league match count at
  prediction time is only ever 0 (new/promoted — where SHRINK's
  factor is 0, the same as Gate Zero's unseen rule) or ≥ 35. The
  arm had no match on which it could differ.
- X2 behaved as designed (≡ Gate Zero in 2022/2023 — no completed
  transition; small OU gains in 2023/2024–2024/2025, pooled 1X2 LL
  marginally worse) but is moot under the gate rule.
- Verification: the climatology baseline was recomputed
  independently from `data/cz_matches.csv` by the coordinator —
  1X2 LL 1.070348 and OU LL 0.689911, exact match with the harness.
  `dc.py` is byte-identical to the audited RO/J1-pattern engine.
