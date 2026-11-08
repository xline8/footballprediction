# C-BO corners engine

Reads `league/BO-PrimeraDivision/data/bo_matches.csv`. Seed is 2025 rounds
1–10 (n=80); dev scores 2025 rounds 11–30 in four expanding 5-round blocks
(n=160); virgin is 2026 regular, transitional (n=199 played). Arms are
`gate_zero` (production corners_v3, X9 possession + big-chance covariates)
and `x7` (opp-box-touch territorial multiplier). Primary line 9.5
(secondary 8.5/10.5); frozen 1H share 0.4866. The league base rate is the
expanding rate as of each scored block's first date.

Run from this directory:

```text
python3 run_c_bo.py dev
python3 run_c_bo.py virgin
```

Dev result: both arms FAIL the dev gate (Gate Zero pooled LL@9.5 0.742273,
X7 0.756243, vs league base rate 0.717569 and naive trailing-10 0.727916).
The virgin command refuses to read 2026 and writes a FAIL
`results_virgin.json`. Authority:
`league/BO-PrimeraDivision/prereg/PREREG_C_BO.md`.
