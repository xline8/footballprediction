# G-TR1 verdict — FAIL (nothing ships, virgin NOT read)

Prereg: `prereg/PREREG_G_TR1.md` (frozen 7953936, before fitting).
Source: `engine/goals/results_dev.json` + `predictions_dev.csv`
(headline numbers independently recomputed from the per-match
predictions by the coordinator — exact match). Dev scored
2022/2023–2024/2025 (n = 998 regular, non-awarded; seed 2021/2022).
No 2025/2026 or 2026/2027 rows were read by the harness (the loader
whitelists dev seasons only).

## Dev results — pooled (n = 998)

| arm | 1X2 LL | RPS | OU2.5 LL | dev gate |
|---|---:|---:|---:|---|
| Gate Zero | 1.065849 | 0.227498 | 0.707038 | **FAIL** (OU leg) |
| SHRINK | 1.065849 | 0.227498 | 0.707038 | FAIL (identical) |
| X2 (mover) | 1.109489 | 0.239835 | 0.713493 | FAIL (all legs) |
| climatology | 1.074184 | 0.231945 | 0.692858 | baseline |

Per season (1X2 LL): Gate Zero 1.063770 / 1.077960 / 1.057788;
X2 1.063770 (≡ GZ — no completed prior transition, offsets 0) /
1.173477 / 1.095582.

## Gate arithmetic

The frozen dev gate requires pooled 1X2 LL and RPS to beat
climatology AND OU2.5 LL to beat the base-rate baseline. Gate Zero
passes the 1X2 leg (1.065849 < 1.074184) and the RPS leg
(0.227498 < 0.231945) but fails the OU2.5 leg: 0.707038 >
0.692858 (+0.014180). Gate Zero therefore fails its dev gate.

Under the prereg's frozen mechanical reading — Gate Zero dev
failure ⇒ candidate FAILS, variants moot, virgin NOT read — the
2025/2026 virgin was **deliberately NOT read** and nothing ships.
(This is the rule the parent TR-SuperLig K-TR build breached with
its X8 variant; it is applied correctly here.)

Notes: SHRINK is numerically identical to Gate Zero by construction
in this season-blocked harness (unseen teams already sit at the
league mean; every returning team has ≥6 prior matches), as in the
parent league. X2's mover offsets were real and correctly scoped
(applied movers: 4 in 2022/2023 with zero offsets, 2 in 2023/2024
with dGF +0.303 / dGA −0.580, 4 in 2024/2025 with dGF +0.099 /
dGA −0.416) and made dev strictly worse — the relegated-team prior
does not transfer at this tier. The 1H presentation constant
(goals 0.4482) ships nowhere, since no arm passed.
