# Verdict — G-J3 (J3 goals model)

Date: 2026-11-09. Branch `build/g-j3`. Pre-registration:
`league/J3/prereg/PREREG_G_J3.md` (commit aeb720a, frozen before any
fitting). Engine: `league/J3/engine/goals/g_j3.py` (implemented by
Codex per brief, verified independently by the coordinator — see §5).
**FULL-TIME ONLY**, as pre-registered; no halves output exists.

## 1. Dev results (walk-forward expanding, season-blocked; n=1,066)

Evaluated seasons 2022–2024 (2021 is the training origin). One fit
per target season on all earlier J3 seasons.

| Arm | Season | n | 1X2 LL | RPS | OU2.5 LL |
|---|---|---:|---:|---:|---:|
| Gate Zero | 2022 | 306 | 1.05569 | 0.23636 | 0.71393 |
| Gate Zero | 2023 | 380 | 1.11060 | 0.23856 | 0.69000 |
| Gate Zero | 2024 | 380 | 1.08248 | 0.22528 | 0.71014 |
| **Gate Zero** | **pooled** | **1066** | **1.08482** | **0.23319** | **0.70405** |
| X2 | 2022 | 306 | 1.07162 | 0.24126 | 0.71601 |
| X2 | 2023 | 380 | 1.11511 | 0.24022 | 0.68845 |
| X2 | 2024 | 380 | 1.08238 | 0.22523 | 0.70742 |
| **X2** | **pooled** | **1066** | **1.09096** | **0.23518** | **0.70312** |
| Climatology / base rate | 2022 | 306 | 1.05192 | 0.23817 | 0.69562 |
| Climatology / base rate | 2023 | 380 | 1.10371 | 0.23594 | 0.69444 |
| Climatology / base rate | 2024 | 380 | 1.09386 | 0.22793 | 0.69147 |
| **Climatology / base rate** | **pooled** | **1066** | **1.08533** | **0.23373** | **0.69372** |

Dev gate (pooled LL and RPS beat climatology, and OU2.5 LL beats
base rate; all three required):

- **Gate Zero: FAIL.** LL beats climatology by 0.00052 and RPS by
  0.00053, but OU2.5 LL 0.70405 loses to the base rate 0.69372 by
  0.01033. Arm dead.
- **X2: FAIL.** Loses all three pooled comparisons (LL +0.00563 vs
  climatology, RPS +0.00145, OU LL +0.00940 vs base rate). Arm dead.

Per-season sign check: both arms beat climatology on 1X2 LL in only
1 of 3 dev seasons (2024 only; both lose 2022 and 2023). The frozen
≥2-of-3 requirement is not met by either arm, so neither arm was
eligible for the both-pass comparison in any case.

## 2. Virgin results (season 2025, n=383, read once after dev froze)

| Arm | 1X2 LL | RPS | OU2.5 LL |
|---|---:|---:|---:|
| Gate Zero | 1.05958 | 0.23130 | 0.69289 |
| X2 | 1.05866 | 0.23088 | 0.69389 |
| Climatology | 1.06014 | — | — |

Virgin legs:

- **(i) LL leg: PASS for both arms.** Gate Zero 1.05958 ≤ its own
  value (equality clause) and ≤ climatology 1.06014. X2 1.05866 ≤
  Gate Zero 1.05958 and ≤ climatology.
- **(ii) Calibration leg: FAIL for both arms.**
  - Home-win rate (actual 47.00%): Gate Zero mean predicted 39.32%,
    diff **−7.68pp**, SE 2.54pp — breach beyond the 1.0pp limit is
    6.68pp, far beyond 1 SE. X2: mean predicted 39.27%, diff
    **−7.72pp**, SE 2.53pp — same failure.
  - OU2.5 over-rate (actual 46.21%): Gate Zero mean predicted
    42.86%, diff −3.35pp, SE 2.55pp — the 2.35pp breach is within
    1 SE, so this sub-item alone would be a provisional pass. X2:
    mean predicted 42.51%, diff −3.70pp, SE 2.55pp — breach 2.70pp
    is beyond 1 SE, FAIL.
  - The leg requires both quantities; the home-win failure alone
    kills it for both arms.
- **(iii) Sign check:** failed on dev (see §1).

The virgin home-win miss is a level shift, not a ratings failure in
disguise: J3's actual home-win rate jumped to 47.0% in 2025 against
a 2021–2024 training level the model centred near 39–41%, and the
same shift is visible in dev season 2022 in reverse (actual 47.4%
vs predicted ~37%). J3's home edge is materially less stable across
seasons than the pooled EDA level suggested.

## 3. Per-arm verdict

| Arm | Dev gate | Virgin LL leg | Virgin calibration leg | Sign check | Verdict |
|---|---|---|---|---|---|
| Gate Zero | FAIL (OU leg) | PASS | FAIL (home-win) | FAIL (1/3) | **FAIL — dead** |
| X2 | FAIL (all three) | PASS | FAIL (home-win, OU) | FAIL (1/3) | **FAIL — dead** |

## 4. Shipped arm

**None. FAIL — nothing ships**, exactly as the pre-registered
both-pass rule prescribes for the none-pass case. X2's lower pooled
virgin LL (1.05866 vs 1.05958) does not rescue it: it failed the dev
gate on every pooled comparison, and the both-pass rule only chooses
between arms that pass. The cross-tier prior itself behaved as
designed (§5) — it simply did not buy accuracy in J3, where only
2–3 relegated clubs arrive per season and the dominant error is the
league's unstable home-win level, which no mover prior addresses.

The virgin predictions file
(`league/J3/predictions/g_j3_virgin_predictions.csv`) records both
arms for the record, per prereg §8; it is not a shipped product.

## 5. Independent verification (coordinator)

- Full harness re-run by the coordinator produced byte-identical
  `dev_results.json` and `virgin_results.json` to the implementer's
  run.
- Dev isolation: the dev path is hard-coded to target seasons
  2022–2024 with training seasons strictly earlier and an assertion
  against season 2025 in training; season 2025 is touched only by
  the virgin block, and 2026/2027 rows are never read as targets or
  training.
- 5 virgin predictions (rows 0, 100, 200, 300, 382; both arms)
  recomputed from scratch from `fitted_params_virgin.json` with an
  independent score-matrix implementation: exact match (max diff
  0.0) on all probabilities and lambdas. Virgin LL recomputed from
  the predictions CSV alone reproduces 1.05958 / 1.05866.
- X2 priors hand-checked: the two relegated clubs with no prior J3
  history (Thespakusatsu Gunma, Tochigi SC) carry fitted ratings
  exactly equal to the pre-registered translation of their 2024 J2
  rates (Gunma a=−0.120/d=+0.006; Tochigi SC a=+0.070/d=−0.103);
  the third relegated club (Kagoshima United) had older J3 history
  and was initialised then updated. The two JFL entrants with no
  J.League history (Tochigi City FC, Kochi United SC) sit at the
  league mean (a=d=0) in both arms, as pre-registered.
- tau/pois copies match `football_etl.py`; the DC fit matches
  production `model_v2.py` (14 sweeps, step 0.7, +0.25 smoothing,
  half-life 270, rho grid, rho condition `yh<=1 or ya<=1`).
