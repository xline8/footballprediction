# S-BO shots-on-target engine

Reads `league/BO-PrimeraDivision/data/bo_matches.csv` (`ShotsOnTarget_*`
fields). Seed is 2025 rounds 1–10 (n=80); dev scores 2025 rounds 11–30 in
four expanding 5-round blocks (n=160); virgin is 2026 regular, transitional
(n=199 played). Arms are GZ (production v5, ratio prior 200) and RS (ratio
prior 20,000). No xG inputs exist in this league. Primary line 11.5
(secondary 10.5/12.5/13.5); frozen 1H share 0.4555.

Run from this directory:

```text
python3 run_s_bo.py dev
python3 run_s_bo.py virgin
```

Dev result: both arms PASS (GZ pooled LL@11.5 0.685669, RS 0.686559, vs
league base rate 0.691716 and naive trailing-10 0.701864). The league
base-rate baseline is the expanding pooled over-rate over all prior 2025
rows (seed included) — the PY harness computed it over scored rows only,
which gives q=0 for the first block; that defect is fixed here.
Authority: `league/BO-PrimeraDivision/prereg/PREREG_S_BO.md`.
