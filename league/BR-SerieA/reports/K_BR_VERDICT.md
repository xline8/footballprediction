# K-BR verdict — FAIL at the dev gate (Gate Zero loses to the base rate)

Prereg: `prereg/PREREG_K_BR.md` (frozen 7056902, before fitting).
Primary line 4.5 on the **unified** yellows target. Dev pooled
n = 1,139 scored (one 2023 match has no cards in either feed).

## Dev results — pooled LL@4.5

| Arm / baseline | LL@4.5 | Per-season model LL (2022, 2023, 2024) |
|---|---|---|
| Gate Zero | 0.688573 | 0.680857 / 0.695462 / 0.689418 |
| X8 (referee) | 0.682996 | 0.674526 / 0.688720 / 0.685758 |
| League base rate | **0.686601** | — |
| Naive trailing-10 | 0.689992 | — |

## Gate arithmetic

- Dev gate: an arm must beat BOTH baselines. **Gate Zero loses to
  the league base rate (0.688573 > 0.686601)** — it beats only the
  naive (0.689992). Gate Zero is dead.
- Under the prereg's frozen mechanical reading ("if Gate Zero
  fails its dev gate, variants are moot, verdict FAIL, virgin NOT
  read"), that ends K-BR: **FAIL, nothing ships.**
- Recorded for completeness: X8 beat both baselines on dev
  (0.682996 < 0.686601 and < 0.689992 — the referee trait helps on
  dev here, as in K-J1/K-DK), and the harness mechanically
  computed X8's virgin metrics before the gate was applied by
  hand. Those figures are **not** a prereg virgin read and decide
  nothing; for the record they would have failed anyway: virgin
  LL@4.5 X8 0.697206 vs base rate 0.690470 and naive 0.692264 —
  leg (i) fails under any reading of the rules. X8's virgin
  calibration was +0.85pp (clean) with healthy referee coverage
  (342/380 = 90.0%; fallbacks 38 unknown-identity, 28 thin
  -history) — the arm died on LL, not on coverage, unlike K-J1.
- The pattern across the program is now consistent: the cards
  reference's team-ratings core adds nothing over a base rate in
  BR (and lost to naive in J2, to the virgin naive in J1) — the
  referee covariate is the only piece that ever helps, and never
  enough to carry the candidate through all legs.

**Ships: nothing.** K-BR is FAIL. The cards engine emits no
fitted-params artefact (same as the DK cards engine); on a FAIL
there is nothing to ship in any case.
