# Verdict — G-UYSEG (UY-SegundaDivision goals, Dixon–Coles goals-only)

**FAIL — dev gate (all three legs). Virgin NOT read. Nothing ships.**

Dev (season-blocked walk-forward; train seed 2021, 85 finished matches;
pooled n = 863):

| Arm | 1X2 LL | RPS | OU2.5 LL |
|---|---|---|---|
| Gate Zero | 1.1352 | 0.2432 | 0.6767 |
| SHRINK | 1.1352 | 0.2432 | 0.6767 |
| X2 | 1.1327 | 0.2427 | 0.6779 |
| Climatology | **1.0927** | **0.2318** | **0.6616** |
| Naive trailing-10 | 1.1697 | 0.2519 | — |

Per-season Gate Zero vs climatology (1X2 LL / RPS / OU2.5 LL):

| Season | n | Gate Zero | Climatology |
|---|---|---|---|
| 2022 | 169 | 1.1884 / 0.2551 / 0.6848 | 1.1080 / 0.2350 / 0.6604 |
| 2023 | 231 | 1.1263 / 0.2419 / 0.7093 | 1.0860 / 0.2340 / 0.6825 |
| 2024 | 233 | 1.1013 / 0.2353 / 0.6527 | 1.0868 / 0.2308 / 0.6468 |
| 2025 | 230 | 1.1394 / 0.2437 / 0.6623 | 1.0944 / 0.2284 / 0.6566 |

Gate Zero loses to climatology in **every season on every metric** — this is
not a hairline miss (contrast G-SK2's 0.000099 OU2.5 miss). The fitted
ratings carry real spread (attack SD 0.21–0.29, defence SD 0.28–0.41 across
fits) but the spread does not predict: the naive trailing-10 baseline is
even worse than the DC (pooled LL 1.1697), and the EDA already warned that
the attack trait is barely reliable (split-half r = 0.187, n = 30 teams;
season-to-season goals-for correlations −0.637 / +0.258 / +0.577 / −0.063).
Two aggravating details: the thin 2021 seed has an anomalously low home-win
rate (0.318 vs 0.379–0.416 in 2022–2025), so the 2022/2023 fits under-predict
home wins (predicted 0.335 / 0.342 vs actual 0.379 / 0.398); and the OU2.5
level is off in opposite directions by season (2023: predicted over-rate
0.340 vs actual 0.416; 2024: 0.398 vs 0.339). The league's outcomes are, on
this corpus, weakly predictable from team ratings at all.

Gate arithmetic (PREREG_G_UYSEG): pooled dev 1X2 LL must beat
climatology ✗ (1.1352 > 1.0927, worse by 0.0425); pooled RPS must beat
climatology ✗ (0.2432 > 0.2318, worse by 0.0114); pooled OU2.5 LL must beat
the base-rate baseline ✗ (0.6767 > 0.6616, worse by 0.0151). SHRINK is
byte-identical to Gate Zero in every season (0 changed rows, 0 teams with
1–5 prior matches — verified independently from the CSV: every
target-season team has either 0 prior matches, where both arms agree, or
≥10; this is the SHRINK ≡ Gate Zero structural pattern). X2 beats Gate Zero
on pooled 1X2 LL (1.1327 vs 1.1352) and RPS (0.2427 vs 0.2432) and in 2 of
4 dev seasons on 1X2 LL, but its OU2.5 LL (0.6779) is worse than
climatology too, so it fails the same leg — and per the prereg, Gate Zero
failing its own dev gate makes the variants moot regardless.

Virgin: **NOT read.** `results_virgin.json` records
`{"virgin_read": false, "reason": "gate zero failed dev gate; virgin not read
(variants moot)"}`. No virgin metrics, no fitted params, no predictions
file. The 2026 season (n = 218, transitional) is reserved as the
confirmatory window for any future re-registered attempt.

Ships: nothing. No predictions file was written.
(`engine/goals/results_dev.json` + `results_dev.csv` are the dev run
artefacts. The independent replay in the build notes — the production
`model_v2.py` DC refit on the same splits — reproduces every Gate Zero dev
number exactly, including the per-season LL/RPS/OU values to 4 decimals, so
this is a property of the league, not an implementation error.)

## Independent-verification notes (build log)

- Production-DC replay (`/tmp/replay_g_uyseg.py`, `model_v2.DC`, hl = 270,
  same season-blocked cutoffs): per-season Gate Zero LL/RPS/OU match the
  harness to 4 decimals; worst per-match probability difference vs
  `results_dev.csv` is 0.00005 (CSV rounding). Rho matches per season
  (−0.05 / −0.05 / −0.05 / 0.00). The harness `dc.py` is byte-identical to
  the SK-2Liga copy except its docstring; `arms.py` differs only in the
  frozen mover ids/offsets, which match the prereg exactly.
- Pooled numbers recomputed from `results_dev.csv` (863 rows, seasons
  2022–2025 only, no 2026 string anywhere): identical to `results_dev.json`.
  X2 differs from Gate Zero on 0/91/92/90 rows (2022–2025); SHRINK on 0.
  Climatology spot-check: the 2022 baseline is exactly the 2021 rates
  (H 0.3176 / D 0.2588 / A 0.4235, OU2.5 over 0.3765).
- Harness re-run by the operator is byte-identical (JSON + CSV).
- Defects found and fixed during the build (all before the prereg/dev):
  1. EDA `F1` pooled H/D/A (0.393/0.277/0.330) matched neither the
     match-weighted pooled rates nor the mean of per-season rates —
     corrected to the pooled values 0.394/0.275/0.331 (`pooled_eval` added
     to `eda.py`/`eda_summary.json`).
  2. EDA `F3` team 1H-share split-half (r = 0.367) counted matches with
     missing half data in the odd/even parity, inflating the correlation;
     the clean value is r = 0.330, and the de-confounded checks are
     r = 0.146 within team-season (n = 54) and r = 0.265 season-demeaned
     (n = 26) — all consistent with noise. Conclusion unchanged (frozen
     constant only), method fixed in `eda.py`, numbers recorded in
     `eda_summary.json`, `FEATURES.md` R1 reworded to cite the
     de-confounded check.
  3. The operator's brief asserted referee names exist in the payloads
     (key present); Codex recomputed correctly that the `Referee.text`
     field is empty in all 1,219 payloads (0/1,219 named) — X8 stays
     dropped, now on the verified number.
- No Codex defects found in the engine/dev run itself.

## What this means for the league

G-UYSEG is a complete FAIL: 0 of 1 candidates pass, 4 of 5 markets were
not buildable from the start (no SOT/corners/total-shots/yellows target in
any season). The league is scores-only with a weak attack signal; a future
re-registered attempt would need a genuinely different signal (none is
visible in this corpus — no xG, no stats, no lineups, no referees) or a
much longer seed before the ratings can be trusted. Do not ship any
UY-SegundaDivision predictions from this build.
