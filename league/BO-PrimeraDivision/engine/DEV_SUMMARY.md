# BO-PrimeraDivision — dev summary (frozen prereg, 2026-11-10)

Pooled dev log-loss at the primary line vs both baselines. The dev gate is:
pooled dev LL beats BOTH the league base rate and the naive trailing-10
(goals: pooled 1X2 LL + RPS beat climatology AND OU2.5 LL beats the
climatology base rate). Arms failing dev do not read the virgin.

| candidate | arm | pooled dev LL | base rate | naive | dev gate |
|---|---|---|---|---|---|
| G-BO (OU2.5) | Gate Zero | 0.698485 | 0.693243 | — (climatology) | **FAIL** (OU leg; 1X2 0.993593 vs 1.022474 and RPS 0.205238 vs 0.213618 pass) |
| G-BO (OU2.5) | SHRINK | 0.698485 | 0.693243 | — | **FAIL** (identical to Gate Zero: no team has 1–5 prior matches at any block start) |
| S-BO (11.5) | GZ | 0.685669 | 0.691716 | 0.701864 | **PASS** |
| S-BO (11.5) | RS | 0.686559 | 0.691716 | 0.701864 | **PASS** |
| C-BO (9.5) | Gate Zero | 0.742273 | 0.717569 | 0.727916 | **FAIL** |
| C-BO (9.5) | X7 | 0.756243 | 0.717569 | 0.727916 | **FAIL** |
| K-BO (6.5) | Gate Zero | 0.662719 | 0.695092 | 0.654949 | **FAIL** (beats base, loses to naive) |
| T-BO (29.5) | A (v1) | 0.687881 | 0.698832 | 0.692501 | **PASS** |
| T-BO (29.5) | B (v2) | 0.685406 | 0.698832 | 0.692501 | **PASS** |
| T-BO (29.5) | C (E9) | 0.688186 | 0.698832 | 0.692501 | **PASS** |

Virgin reads: S-BO (both arms) and T-BO (all three arms) ONLY. G-BO, C-BO
and K-BO virgins are NOT read; their virgin commands write FAIL artifacts
without loading the virgin window. Defects fixed during this build (all
before any virgin read): the SOT league-base-rate baseline excluded seed
rows (inflated to 1.0335; corrected to 0.691716); the cards virgin leg (i)
in the PY harness compared against the base rate only (BO compares against
both baselines, per prereg); the SOT virgin naive baseline used model probs
in PY (BO uses naive_probs); the builder wrote the literal string "null"
for missing referees (fixed; CSVs regenerated identically).
