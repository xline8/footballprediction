# K-DK verdict — FAIL

Prereg: `prereg/PREREG_K_DK.md` (frozen 6a0240b, before fitting).
Primary line 3.5. Dev pooled n = 579; virgin 2025/2026 n = 193,
read once for both dev-passing arms. Referee coverage in DK is
100% in every season — the X8 arm was fully testable here, unlike
K-J1 (virgin coverage 0.5%) and K-J2 (0%).

## Dev results — pooled LL@3.5

| Arm / baseline | LL@3.5 |
|---|---|
| Gate Zero | 0.6889 |
| X8 (referee) | 0.6868 |
| League base rate | 0.6918 |
| Naive trailing-10 | 0.7053 |

Both arms beat both baselines → both pass the dev gate. X8 helps
on dev, as it did in J1 (pooled −0.0021), driven by 2024/2025
(0.6673 vs 0.6845).

## Virgin results (2025/2026, n = 193)

| Arm / baseline | LL@3.5 | Calibration |
|---|---|---|
| Gate Zero | 0.6640 | +1.98pp (SE 3.50pp) |
| X8 | 0.6742 | +1.01pp (SE 3.54pp) |
| League base rate | 0.6757 | — |
| Naive trailing-10 | **0.6540** | — |

## Gate arithmetic

- Leg (i): virgin LL must be ≤ Gate Zero's **and** ≤ the best
  baseline's. The naive trailing-10 (0.6540) beats Gate Zero
  (0.6640) and X8 (0.6742) → **both arms FAIL leg (i)**. X8 also
  fails leg (i)'s Gate Zero clause directly (0.6742 > 0.6640).
- Leg (ii) would have been PROVISIONAL PASS for both (breaches of
  0.98pp / 0.01pp beyond the 1.0pp boundary, each within 1 SE) —
  recorded for completeness; it does not rescue leg (i).
- Leg (iii): X8's dev sign check vs Gate Zero is 1/3 seasons
  (worse in 2022/2023 and 2023/2024, better only in 2024/2025) —
  X8 would have failed this leg too.

**Verdict: FAIL. Nothing ships.** The diagnosis mirrors K-J2: DK
yellows stepped down across the window (3.69 → 3.24 per match) and
kept falling in the virgin season (over-3.5 rate 0.399 vs dev
0.474); the trailing-10 baseline adapts to a level shift in weeks
while HL-270 ratings carry the old regime for months. The referee
trait is real here (r = 0.561) and helped on dev, but reversed on
the virgin — with full referee coverage this time, that reversal
is a genuine market result, not a coverage artefact. Note: the
harness's NB size estimate hit its 500 cap for the model/base
methods on the virgin fit (near-Poisson yellows, dispersion 1.02);
the gate outcome does not turn on it (the naive winner used
r = 159.1).
