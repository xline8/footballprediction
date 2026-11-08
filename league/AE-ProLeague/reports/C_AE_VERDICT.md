# Verdict — C-AE (AE-ProLeague corners)

**FAIL at virgin leg (i): the plain league base rate beat both arms.**
Nothing ships. Virgin read once, for both dev-passing arms.

Dev LL@10.5 (n=545, recomputed exactly): Gate Zero 0.683055, X7
0.690822; baselines: league base rate 0.697457, naive 0.696123. Both
arms pass the dev gate. X7 sign check: 2/3 (ties in 2023/2024 and
2024/2025, where its fitted β_bt = 0 makes it identical to its
no-multiplier form; it differs only in 2022/2023, for the worse).

Virgin 2025/2026 (n=182; recomputed exactly through an independent
driver over the engine core):

| Arm | LL@10.5 | Mean P(over) | Actual | Breach | Leg (i) | Leg (ii) |
|---|---|---|---|---|---|---|
| Gate Zero | 0.662244 | 0.3255 | 0.3352 | −0.97pp | **FAIL** | PASS (clean) |
| X7 | 0.659400 | 0.3241 | 0.3352 | −1.10pp | **FAIL** | PASS (provisional band) |
| League base rate | **0.637856** | — | — | — | — | — |
| Naive trailing-10 | 0.643760 | — | — | — | — | — |

Calibration was fine; the models simply carried no virgin-window skill
beyond the base rate (virgin corners fell to 9.15/match, and the
near-constant base-rate probability scored best). X7's virgin fit also
chose β_bt = 0 — the box-touch trait (r=0.951 in EDA) is again worth
zero inside this multiplier structure, as in J1/DK/SA.
