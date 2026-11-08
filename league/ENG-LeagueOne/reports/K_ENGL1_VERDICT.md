# Verdict — K-ENGL1 (ENG-LeagueOne cards)

**FAIL at the dev gate. Virgin 2025/2026 deliberately NOT read.
Nothing ships.**

Primary line 3.5. Single arm by design (X8 referee arm dropped in
FEATURES: reliability r=0.305; team yellows trait weak, r=0.309).

## Dev gate (walk-forward 2022/2023–2024/2025, pooled n=1,671)

| Arm | LL@3.5 | vs league base 0.6938 | vs naive 0.6979 |
|---|---|---|---|
| Gate Zero | 0.6982 | ✗ (+0.0045) | ✗ (+0.0004) |

Gate (frozen): pooled dev LL@3.5 must beat BOTH baselines. Gate
Zero loses to the base rate clearly and to naive trailing-10 by
four ten-thousandths — a loss is a loss under the frozen gate.
The cards level shift in 2023/2024 (yellows 3.64 → 4.07 per match,
EDA F1) is part of the context: the model's per-season fits chase
a moving level while the dumb baselines sit on it.

Virgin NOT read; no `results_virgin.json` exists for this engine
(the ENG-Championship convention for a dev-gate FAIL). 2025/2026
remains available only under a new prereg; 2026/2027 confirmatory
untouched.
