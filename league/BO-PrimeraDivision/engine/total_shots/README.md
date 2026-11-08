# T-BO total-shots engine

Reads `league/BO-PrimeraDivision/data/bo_matches.csv`. Seed is 2025 rounds
1–10 (n=80); dev scores 2025 rounds 11–30 in four expanding 5-round blocks
(n=160); virgin is 2026 regular, transitional (n=199 played). Arms A (v1),
B (v2 level layer), C (E9 trailing-r). Primary line 29.5 (ladder
28.5/29.5/30.5/31.5); frozen 1H share 0.4633. Ridge lambda is tuned on the
2025 rows (selected 300.0, the top of the grid — noted in the verdict);
the level cell is tuned on the first dev block ([30.0, 0.5, 20.0]).
NB r_A = 87.84 (moment estimate on the tuned lambda).

Run from this directory:

```text
python3 run_t_bo.py dev
python3 run_t_bo.py virgin
```

Dev result: all three arms PASS (A 0.687881, B 0.685406, C 0.688186 pooled
LL@29.5, vs league base rate 0.698832 and naive trailing-10 0.692501).
Authority: `league/BO-PrimeraDivision/prereg/PREREG_T_BO.md`.
