# Verdict — G-CZ-FNL (CZ-FNL goals, Dixon–Coles goals-only)

**FAIL — dev gate (all three legs). Virgin NOT read. Nothing ships.**

Dev (pooled, n = 720; walk-forward season-blocked, evaluation
2022/2023–2024/2025):

| Arm | 1X2 LL | RPS | OU2.5 LL | vs climatology (1.073111 / 0.223606 / 0.693599) |
|---|---|---|---|---|
| Gate Zero | 1.098532 | 0.231372 | 0.706552 | LL ✗, RPS ✗, OU ✗ |
| SHRINK | 1.098532 | 0.231372 | 0.706552 | identical to Gate Zero (see note) |
| X2 | 1.105400 | 0.232192 | 0.711411 | LL ✗, RPS ✗, OU ✗ |

Per-season Gate Zero vs climatology (1X2 LL / RPS / OU2.5 LL):

| Season | Model | Climatology |
|---|---|---|
| 2022/2023 | 1.086316 / 0.230740 / 0.709422 | 1.058827 / 0.220443 / 0.691897 |
| 2023/2024 | 1.089272 / 0.232678 / 0.727397 | 1.063212 / 0.226120 / 0.693148 |
| 2024/2025 | 1.120007 / 0.230697 / 0.682835 | 1.097295 / 0.224254 / 0.695753 |

The model loses the 1X2 LL and RPS legs in **every** dev season, not
just pooled. The only leg the model wins anywhere is OU2.5 in
2024/2025 (0.682835 vs 0.695753); the pooled OU leg still fails by
0.0130.

Gate arithmetic (PREREG_G_CZ_FNL): the dev gate requires pooled 1X2 LL
and RPS to beat climatology AND OU2.5 LL to beat the base-rate
baseline. Gate Zero fails all three — LL 1.098532 > 1.073111,
RPS 0.231372 > 0.223606, OU 0.706552 > 0.693599 — so **Gate Zero
fails the dev gate**; per the frozen mechanical reading the variants
are moot and the virgin window was NOT read
(`engine/goals/results_virgin.json`: `virgin_read: false`).

Notes:
- SHRINK ≡ Gate Zero to all printed digits, by construction: under
  season-blocked fitting a team's prior in-league match count at
  prediction time is only ever 0 (new/promoted — where SHRINK's
  factor is 0, the same as Gate Zero's unseen rule) or ≥ 30
  (verified: prior-count values present are 30 and 60 only). The arm
  had no match on which it could differ.
- X2 behaved as designed (≡ Gate Zero in 2022/2023 — no completed
  transition) but pooled it is worse than Gate Zero on all three
  metrics. Its only improvements are LL/RPS in 2024/2025 (1.106012 /
  0.225723 vs 1.120007 / 0.230697), outweighed by 2023/2024, where X2
  hurts most (LL 1.123874 vs 1.089272): the cumulative offset that
  season (+0.545833, −0.154167) rests on a single completed
  transition (Karvina), and Brno's actual first season ran the other
  way on attack (ΔGF −0.065). Moot under the gate rule either way.
- Context, not excuse: this league's goals traits are the weakest
  measured in the programme so far (EDA: goals-for r = 0.327,
  goals-against r = 0.295, vs CZ-Liga 0.648 / 0.366), with 3–5 team
  changes per season including reserve sides. A Dixon–Coles that
  cannot beat expanding base rates here is a property of the league,
  not of the fit: fitted params are sane (mu 1.35–1.42, h 0.30–0.35,
  rho 0 / −0.05).
- Verification: the climatology baselines were recomputed
  independently from `data/fnl_matches.csv` — per-season and pooled
  1X2 LL 1.073111, RPS 0.223606, OU LL 0.693599, exact match with the
  harness. Gate Zero's per-season metrics were recomputed with an
  independent driver through the same `dc.py` — exact match to all
  six decimals in all three seasons. X2 2023/2024 was likewise
  re-driven independently — exact match. `dc.py` is byte-identical
  to the audited CZ-Liga engine except its docstring. The
  `virgin-metrics` runner was exercised after the fix to its
  `virgin-predict` branch (it referenced an undefined `dev`): it
  re-ran dev deterministically and wrote the `virgin_read: false`
  marker without creating any predictions.
