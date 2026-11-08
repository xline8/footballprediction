# Verdict — G-SCO (Scotland Premiership goals) — **PROVISIONAL PASS** (Gate Zero ships)

Prereg: `prereg/PREREG_G_SCO.md` (frozen 2553ea4, before fitting).
Dev = walk-forward 2022/2023–2024/2025 (n=684); virgin = 2025/2026
(n=228), read once for dev-passing arms.

## Dev (pooled)
| Arm | 1X2 LL | RPS | OU2.5 LL | vs climatology (1.0567 / 0.2324 / 0.6983) |
|---|---|---|---|---|
| Gate Zero | 0.9406 | 0.1928 | 0.6859 | beats all three — dev gate PASS |
| SHRINK | 0.9406 | 0.1928 | 0.6859 | identical to GZ (n=0 case by construction) — PASS |
| X3 | 0.9598 | 0.1955 | 0.6926 | beats climatology — PASS |

## Virgin 2025/2026 (n=228)
| Arm | 1X2 LL | RPS | OU LL | HW cal | OU cal (SE) |
|---|---|---|---|---|---|
| Gate Zero | 0.9871 | 0.1975 | 0.6871 | +0.54pp | −1.25pp (3.30pp) |
| SHRINK | 0.9871 | 0.1975 | 0.6871 | +0.54pp | −1.25pp (3.30pp) |
| X3 | 1.0114 | 0.2021 | 0.6978 | +0.83pp | +0.20pp |
| Climatology | 1.0738 | 0.2258 | 0.6914 | — | — |

Gate arithmetic: leg (i) GZ/SHRINK 0.9871 ≤ GZ and ≤ climatology ✓;
X3 1.0114 > GZ → leg (i) FAIL. Leg (ii): HW clean; OU breach
1.25pp > 1pp but within 1 SE (3.30pp) → PROVISIONAL. Tie GZ/SHRINK
→ simpler arm ships.

**Ships: Gate Zero** (fitted params `engine/goals/fitted_params_virgin.json`;
predictions `predictions/g_sco_virgin_predictions.csv`, halves via
frozen 0.4405). The extreme Old Firm lambdas were left unclamped,
as designed, and the virgin read did not punish them.
