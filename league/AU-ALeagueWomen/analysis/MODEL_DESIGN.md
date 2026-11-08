# Model design (pre-fit)

Five candidates are buildable because all five targets are present in every development and 2025/2026 virgin regular row: G-AUW goals, S-AUW shots on target, C-AUW corners, K-AUW cards and T-AUW total shots. Every candidate uses the AU-ALeague sibling's Gate Zero reference pattern, adapted to regular-only AUW windows and the frozen constants above. No engine or fit is created in this phase.

| candidate | Gate Zero | pre-registered variant arms | primary line |
|---|---|---|---|
| G-AUW | goals-only Dixon-Coles | SHRINK for teams with <6 prior matches; no xG blend | OU 2.5 |
| S-AUW | SOT production v5 pattern | RS (BB prior 200 -> 20,000, the J1/AU sibling variant); no xG arms | O10.5 |
| C-AUW | corners_v3 pattern with X9 | X7 box-touch multiplier | O9.5 |
| K-AUW | cards production pattern, stats yellows | X8 referee strictness | O2.5 |
| T-AUW | total-shots reference pattern | arms A (v1 pattern), B (v2 + level layer), C (E9 trailing-r) as in the AU sibling prereg | O27.5 |

Development is season-blocked walk-forward: training seed 2021/2022, evaluation 2022/2023 (99), 2023/2024 (132), and 2024/2025 (138), pooled n=369. Virgin is 2025/2026 regular only (110), read once only for dev-passing arms. 2026/2027 is reserved and unread. Finals are excluded everywhere. Goals use no xG blend; the SHRINK arm is the sanctioned new/expansion-team protection.

## Frozen gate legs

Dev gate: the arm must beat both baselines mechanically—league base-rate/climatology and naive trailing-10 as appropriate to the market—on the candidate's primary scored log loss. Virgin legs are (i) LL <= Gate Zero and <= the best baseline, (ii) calibration `|mean predicted - actual| <= 1.0pp` clean PASS; a breach within one SE, `SE=sd(p_i-y_i)/sqrt(n)`, is PROVISIONAL PASS, otherwise FAIL, and (iii) variant arms must pass the dev per-season sign check. Both-pass ships the lower pooled virgin LL; ties go to the simpler arm. Gate Zero dev failure fails the candidate and virgin is not read. Halves on PASS are presentation only: FT plus 1H/2H using the frozen constants.
