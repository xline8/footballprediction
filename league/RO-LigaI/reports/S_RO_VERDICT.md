# Verdict — S-RO (RO-LigaI shots on target)

**FAIL — virgin leg (i), by 0.0001 LL. Nothing ships.**

Dev (pooled, stats-target n = 924, LL@8.5):

| Arm | LL@8.5 | vs base 0.6889 | vs naive 0.6711 | Dev gate |
|---|---|---|---|---|
| Gate Zero | 0.6665 | ✓ | ✓ | PASS |
| RS | 0.6669 | ✓ | ✓ | PASS (but sign check 1/3) |

RS per-season LL@8.5 vs GZ: 0.6581>0.6579, 0.6621>0.6608,
0.6800<0.6802 → sign check 1 of 3 (< 2) → RS was NOT read on the
virgin window (harness `read_arms: ["GZ"]`).

Virgin (2025/2026, n = 315), Gate Zero only:

| | LL@8.5 | Calibration (pp) |
|---|---|---|
| Gate Zero | 0.693906 | −0.99 (SE 2.82) |
| League base rate | **0.693782** | −2.72 |
| Naive trailing-10 | 0.706696 | −0.69 |

Gate arithmetic (PREREG_S_RO): leg (ii) calibration passes clean
(|−0.99pp| ≤ 1.0pp). Leg (i) requires LL ≤ Gate Zero's AND ≤ the
best baseline's: 0.693906 > 0.693782 → **leg (i) FAILS by 0.000124**.
Verdict FAIL; no arm ships. (Headline numbers recomputed
independently from the per-match prediction CSV before its
deletion: LL 0.693906, calibration −0.99pp — exact match. The
harness writes a predictions file for its fallback arm even on
FAIL; that file was deleted — nothing ships on a FAIL.)
