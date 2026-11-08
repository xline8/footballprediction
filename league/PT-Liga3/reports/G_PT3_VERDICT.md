# Verdict — G-PT3 (Portugal Liga 3 goals model) — **FAIL**

Prereg: `prereg/PREREG_G_PT3.md`, frozen 2026-11-10 before fitting. Dev is expanding, season-blocked evaluation for 2022/2023–2024/2025, pooled n=929, with 2021/2022 as the seed. Both preregistered arms failed the pooled dev gate. The virgin was deliberately **not read**. No arm ships.

## Dev results

| Season | Arm | 1X2 LL | RPS | OU2.5 LL | Climatology LL / RPS / OU LL |
|---|---|---:|---:|---:|---|
| 2022/2023 (n=337) | Gate Zero | 1.059670 | 0.224986 | 0.710861 | 1.075837 / 0.232121 / 0.688374 |
| 2023/2024 (n=296) | Gate Zero | 1.083818 | 0.232629 | 0.695933 | 1.075081 / 0.229908 / 0.684837 |
| 2024/2025 (n=296) | Gate Zero | 1.104911 | 0.231637 | 0.703447 | 1.082429 / 0.223719 / 0.685845 |
| **Pooled (n=929)** | **Gate Zero** | **1.081779** | **0.229541** | **0.703742** | **1.077696 / 0.228739 / 0.686441** |
| 2022/2023 (n=337) | SHRINK | 1.059670 | 0.224986 | 0.710861 | 1.075837 / 0.232121 / 0.688374 |
| 2023/2024 (n=296) | SHRINK | 1.083818 | 0.232629 | 0.695933 | 1.075081 / 0.229908 / 0.684837 |
| 2024/2025 (n=296) | SHRINK | 1.104911 | 0.231637 | 0.703447 | 1.082429 / 0.223719 / 0.685845 |
| **Pooled (n=929)** | **SHRINK** | **1.081779** | **0.229541** | **0.703742** | **1.077696 / 0.228739 / 0.686441** |

SHRINK is numerically identical to Gate Zero in these season-blocked fits; no target-season team had a prior in-league count below six in a way that changed the predictions.

## Dev gate arithmetic

The frozen gate requires all three pooled strict inequalities: 1X2 LL < climatology, RPS < climatology, and OU2.5 LL < the base-rate baseline.

- Gate Zero, 1X2 LL: **1.0817787102783878 vs 1.077696351125059 — FAIL**.
- Gate Zero, RPS: **0.22954054007503003 vs 0.22873915473136938 — FAIL**.
- Gate Zero, OU2.5 LL: **0.7037420729434581 vs 0.686441375932824 — FAIL**.
- SHRINK has exactly the same three comparisons and therefore also **FAILS**.

Because no arm passed dev, the virgin was not read. Virgin legs (i) 1X2 LL, (ii) home-win and OU2.5 calibration, and (iii) the SHRINK per-season sign check are **not assessed**; all virgin arithmetic is N/A. The both-pass/tie rule is not reached. **Final verdict: FAIL; nothing ships.**

## Virgin results

Not read, as required. `engine/goals/results_virgin.json` records:

```json
{"virgin_read": false, "reason": "No arm passed pooled dev gate"}
```

No `fitted_params_virgin.json` or `predictions/g_pt3_virgin_predictions.csv` was written.

## Verification notes

- PT2 replay used the available sibling-worktree copy `../wt-pt-liga2/league/PT-LigaPortugal2/data/pt2_matches.csv`; the specified main-checkout path did not contain that gitignored file. The CSV was read through a small `home_team`/`away_team` adapter and was not copied into PT3. Every published PT2 dev metric for both arms, all three seasons plus pooled and climatology rows, reproduced exactly (maximum absolute difference 0.0; requirement was <=1e-9).
- An independent naive score-matrix reconstruction from the fitted Gate Zero parameters reproduced the PT3 pooled dev metrics for all 929 matches exactly: 1X2 LL 1.0817787102783878, RPS 0.22954054007503003, OU2.5 LL 0.7037420729434581. Twenty sampled matches also had maximum probability/score difference 0.0.
- Leakage checks printed maximum training dates of 2022-05-14, 2023-05-20, and 2024-05-19 for the three dev blocks, each before its target season's first kickoff. Dev fits contained no 2025/2026 or 2026/2027 rows; the virgin command stopped at the dev gate.
- `run_g_pt3.py virgin` reran the dev gate and wrote the not-read marker without loading the virgin season. The loader assertion rejects an unfiltered reserved 2026/2027 load.
- The engine uses the preregistered constants and the exact SHRINK n/6 prediction-time rule. `config.yaml` was not changed.
