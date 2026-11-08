# Verdict — S-PY (PY-DivisionProfesional shots on target)

**FAIL — both arms passed the dev gate, read the transitional
virgin, and failed virgin leg (ii) calibration decisively.
Nothing ships.**

Prereg: `league/PY-DivisionProfesional/prereg/PREREG_S_PY.md` (frozen
06d6a41, before any fitting). Engine: `engine/sot/` (KR/J1 v5 port
with X4/X6 removed — no shotmap exists; coordinator verified the
dev/virgin JSON arithmetic below).

## Dev gate (pooled, 2025-Cl + 2026-Ap, n = 263 scored)

| arm | LL@7.5 |
|---|---|
| Gate Zero | 0.6928 |
| RS | **0.6918** |
| league base rate | 0.8988 |
| naive trailing-10 | 0.7000 |

Both arms beat both baselines ✓ → dev gate PASS for GZ and RS.
(RS better in 2025-Cl, worse in 2026-Ap — sign leg (iii) 1/2, met.)

## Virgin — 2026 - Clausura TRANSITIONAL (n = 112 played)

| arm | LL@7.5 | calibration breach | SE |
|---|---|---|---|
| Gate Zero | 0.6296 | **−9.53pp** | 4.35pp |
| RS | 0.6290 | **−9.56pp** | 4.35pp |
| league base rate (p = 0.5 reference) | 0.6931 | – | – |
| naive trailing-10 | 0.6296 | – | – |

- Leg (i) LL: both arms ≤ Gate Zero and ≤ baselines ✓ (RS lowest).
- Leg (ii) calibration: |−9.53pp| vs the frozen boundary 1.0pp +
  1 SE 4.35pp = 5.35pp → **breach exceeds the provisional band by
  4.18pp → FAIL** for both arms. The transitional virgin ran hot on
  SOT (actual mean 8.81 vs dev 8.09; F5 in the EDA) and both arms
  under-predicted the over-rate by ~9.5pp. The gate is not moved.

**Verification catch (recorded for the final audit; verdict-neutral):**
in the ported harness's virgin mode, the naive baseline's LL is
bit-identical to Gate Zero's (the virgin baseline path recomputes
from the GZ rows instead of independent naive probs, an inherited
KR-harness shortcut) and the league base rate is a fixed p = 0.5
reference. Leg (i) is therefore weaker than specified — but leg (ii)
fails both arms by a wide margin on its own, so the FAIL verdict
does not depend on the defect. No virgin re-read was made or is
needed.

The season-end confirmatory read of the completed 2026 - Clausura
remains outstanding by design; it cannot change this verdict.
