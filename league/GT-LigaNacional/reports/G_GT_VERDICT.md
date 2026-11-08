# Verdict — G-GT (Guatemala Liga Nacional goals model) — **FAIL**

Prereg: `prereg/PREREG_G_GT.md`, frozen before fitting at commit `5df200e2`.
Development is expanding and season-blocked: 2021/2022 seed, 2022/2023–2024/2025 dev, pooled n=746. The complete 2025/2026 virgin and reserved 2026/2027 confirmatory rows were not read by the dev run. Both preregistered arms failed the pooled dev gate. No arm ships.

## Dev results

| Season | Arm | n | 1X2 LL | RPS | OU2.5 LL | Climatology LL / RPS / OU LL |
|---|---|---:|---:|---:|---:|---|
| 2022/2023 | Gate Zero | 292 | 1.034425705 | 0.207596381 | 0.725733132 | 1.014425723 / 0.201263136 / 0.697312292 |
| 2023/2024 | Gate Zero | 220 | 0.982955534 | 0.200975429 | 0.702810950 | 0.990628134 / 0.201805888 / 0.695939127 |
| 2024/2025 | Gate Zero | 234 | 0.980133264 | 0.189990176 | 0.696405735 | 1.008199435 / 0.198524575 / 0.684925322 |
| **Pooled** | **Gate Zero** | **746** | **1.002216766** | **0.200121231** | **0.709774029** | **1.005454649 / 0.200564184 / 0.693021880** |
| 2022/2023 | SHRINK | 292 | 1.034425705 | 0.207596381 | 0.725733132 | 1.014425723 / 0.201263136 / 0.697312292 |
| 2023/2024 | SHRINK | 220 | 0.982955534 | 0.200975429 | 0.702810950 | 0.990628134 / 0.201805888 / 0.695939127 |
| 2024/2025 | SHRINK | 234 | 0.980133264 | 0.189990176 | 0.696405735 | 1.008199435 / 0.198524575 / 0.684925322 |
| **Pooled** | **SHRINK** | **746** | **1.002216766** | **0.200121231** | **0.709774029** | **1.005454649 / 0.200564184 / 0.693021880** |

## Dev gate arithmetic

The frozen gate requires strict improvement on pooled 1X2 LL and RPS versus climatology, and pooled OU2.5 LL versus the base-rate baseline. The pooled comparisons are:

- Gate Zero 1X2 LL: **1.002216765536508 vs 1.0054546492878784 — PASS**.
- Gate Zero RPS: **0.2001212317098 vs 0.20056418441886548 — PASS**.
- Gate Zero OU2.5 LL: **0.709774028984336 vs 0.6930218799267513 — FAIL**.
- SHRINK has exactly the same three comparisons: **PASS, PASS, FAIL**.

No arm passed all three legs. Per the preregistered stop rule, the virgin was deliberately not read. `results_virgin.json` records `{"virgin_read": false, "reason": "No arm passed pooled dev gate"}`. Virgin 1X2 LL, calibration, and variant sign legs are not assessed; the both-pass/tie rule is not reached. Final verdict: **FAIL; nothing ships**.

## SHRINK identity check

SHRINK changed **0 of 746 dev predictions**, with maximum absolute delta **0.0** across expected goals, 1X2, OU2.5, and BTTS probabilities. This is not dead code. For each dev target season, the all-target-team minimum prior count was 0 because newly promoted/unseen teams use the explicit n=0 default; the minimum among seen target teams was 46 (2022/2023), 46 (2023/2024), and 36 (2024/2025), all above six. Thus every fitted rating subject to scaling was unscaled, while unseen teams correctly remained at the same league-mean default.

The per-season maximum training dates were 2022-05-30, 2023-05-28, and 2024-05-19, each before its target season's first kickoff. The loader rejects reserved 2026/2027 rows, and dev is restricted to the seed plus dev seasons.

An independent from-scratch Poisson/DC score-matrix reconstruction for four seed-fitted target matches matched the engine's expected goals and probabilities with maximum absolute delta 0.0.

## Reproducibility

Two clean runs from deleted generated result files produced identical SHA-256 hashes for all three generated result artifacts:

- `results_dev.json`: `e1bfe03da9f99839604726a0469ff6dccad23617300471f7adf513072710213a`
- `results_dev.csv`: `ee5bc725ebb509ac289e3dcf138f680ab91c7c741286fbf40b5e6a56de954b62`
- `results_virgin.json`: `ee913fa6387485a059d116c6138055c05f6e845e1996d18ba2b4578b42c1488a`

## Files produced

- `engine/goals/dc.py`
- `engine/goals/arms.py`
- `engine/goals/harness.py`
- `engine/goals/run_g_gt.py`
- `engine/goals/README.md`
- `engine/goals/results_dev.json`
- `engine/goals/results_dev.csv`
- `engine/goals/results_virgin.json`
- `reports/G_GT_VERDICT.md`

No `fitted_params_virgin.json` or virgin predictions CSV was produced because the virgin was not read.
