# Verdict — T-ES (ES-LaLiga2 total shots) — **PROVISIONAL PASS** (arm C / E9 ships)

Prereg: `prereg/PREREG_T_ES.md`. Primary line 23.5. Dev n=1,404,
virgin 2025/2026 n=468.

## Dev (pooled LL@23.5; baselines: league 0.6925, naive 0.6744)

| Arm | Dev LL | Per-season sign vs A | Dev outcome |
|---|---|---|---|
| A (v1 pattern) | 0.6678 | — | PASS |
| B (v2 level layer) | 0.6673 | 2/3 | PASS |
| C (E9 trailing-r) | 0.6679 | 2/3 | PASS |

## Virgin 2025/2026 (all three arms, per the frozen rule)

| Arm | LL@23.5 | Calibration (SE) | Legs |
|---|---|---|---|
| A | 0.6550 | −1.29pp (2.22pp) | (i) ✓ (ii) provisional |
| B | 0.6555 | −0.63pp (2.22pp) | **(i) ✗ — above reference arm A (0.6550)** |
| C | **0.6548** | −2.11pp (2.22pp) | (i) ✓ (ii) provisional |

Gate arithmetic: leg (i) requires LL ≤ the reference arm's and ≤
the best baseline's (naive 0.6682 / league 0.6797): A ✓, B fails
against A by 0.0005 despite the only clean calibration of the
three, C ✓ (0.6548 ≤ 0.6550). Leg (ii): A's excess over the 1.0pp
boundary is 0.29pp and C's is 1.11pp, both within 1 SE (2.22pp) →
PROVISIONAL for both. Leg (iii): B and C both 2/3 on dev. Passing
arms are A and C; the both-pass rule ships the lower pooled virgin
LL → **arm C (E9 trailing-r) ships, PROVISIONAL PASS**. The virgin
season ran hot on shots (actual over-23.5 rate 0.592 vs dev 0.481);
all three arms under-predicted it, C most of all — inside the
provisional band, recorded as such.

**Ships: arm C** (`engine/total_shots/fitted_params_virgin.json`;
`predictions/t_es_virgin_predictions.csv`; halves via 0.4522).
Independent checks: virgin LL@23.5 (0.654767) and calibration
(−2.113pp) recomputed by hand from the shipped predictions CSV.
