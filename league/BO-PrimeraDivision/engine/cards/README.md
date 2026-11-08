# K-BO cards engine

Reads `league/BO-PrimeraDivision/data/bo_matches.csv`. Target is
event-unified yellows (`event_yellow_unified_home + _away`); the stats-feed
yellow columns are NOT the target (they undercount 1,324 vs 1,495 in 2025).
Seed is 2025 rounds 1–10 (n=80); dev scores 2025 rounds 11–30 in four
expanding 5-round blocks (n=160); virgin is 2026 regular, transitional
(n=199 played). Gate Zero only (X8 dropped: referee named on 40/240 in
2025). Primary line 6.5 (secondary 5.5/7.5); frozen 1H share 0.3739.
NB dispersion r is estimated on the warm (seed) rows only; on the
underdispersed seed window (variance 5.11 < mean 6.39) the moment estimator
caps at r=500 for all three methods (effectively Poisson).

Run from this directory:

```text
python3 run_k_bo.py dev
python3 run_k_bo.py virgin
```

Dev result: Gate Zero FAILS the dev gate (pooled LL@6.5 0.662719 vs league
base rate 0.695092 — beats — but vs naive trailing-10 0.654949 — loses).
The virgin command refuses to read 2026 and writes a FAIL
`results_virgin.json`. Authority:
`league/BO-PrimeraDivision/prereg/PREREG_K_BO.md`.
