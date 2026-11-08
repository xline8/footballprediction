# Phase 4 — Model Design: GR-SuperLeague Candidates

This is a candidate design only. No fitting or dev/virgin evaluation
has been performed. The dev window is a season-blocked walk-forward
over the dev period 2021/2022–2024/2025 (956 matches including the
2021/2022 training seed; scored seasons 2022/2023–2024/2025, 716
matches). The primary virgin is 2025/2026 (236 matches, last complete
season), read once only after dev gates. 2026/2027 (69 matches) is
confirmatory and must not be read in this build.

**Phase rule (frozen):** phase is flagged from `general.leagueName`
(`regular`, `playoff_championship`, `playoff_conference`,
`playoff_relegation`); all phases are ordinary rows in every fit and
every window; no phase feature anywhere (BE precedent; measured
phase goal levels 2.465–2.958 vs regular 2.524 — see EDA).
Calibration is defined as **actual minus predicted** everywhere.

| Candidate | Reference / Gate Zero | Primary .5 line (dev over-rate) | Candidate arms |
|---|---|---|---|
| G-GR goals | Dixon–Coles goals pattern with the X1 blend | OU 2.5 (0.482) | Gate Zero; SHRINK for thin-data team priors. X3 NOT run: set-play reliability fails (0.193) and its era starts inside the virgin |
| S-GR SOT | `model_sot.py` v5 reference | 8.5 (0.447; 7.5 is 0.562) | Gate Zero; RS ratio-shrink. X4 NOT run (era inside virgin); X6 dropped (0.264) |
| C-GR corners | `model_corners_v3` reference with X9 | 8.5 (0.517; 9.5 is 0.386) | Gate Zero; X7 box-touch multiplier (reliability 0.953/0.855, min-8 trailing rule) |
| K-GR cards | `model_cards.py` reference | 4.5 (0.520; 3.5 is 0.699) | Gate Zero ONLY. X8 dropped at design: referee reliability 0.262 fails (EDA F7) |
| T-GR total shots | A/B/C shots-family reference | 22.5 (scored-dev 0.534; 23.5 is 0.447) | Arms A, B, C; no extra GR feature |

Line selection is mechanical (over-rate closest to 0.5), with one
documented exception: the shots line is selected on the scored dev
seasons (2022/2023–2024/2025) because the 2021/2022 seed season's
total_shots feed is a different measurement (mean 16.89 and on-target
rate 0.510 against 21.96–24.16 and 0.315–0.362 in every later season;
DATA_UNDERSTANDING §2). All other markets' seed-season measurements
are coherent, so their lines use the full dev period (BE convention).

X1 honesty note: stats-feed xG is full only from 2025/2026 (18 stray
matches before). Gate Zero's blend therefore runs effectively
goals-only through dev and through the virgin fit (whose training
window ends 2024/2025); the blend weight is the production pattern
with its documented goals-only fallback, not a fitted xG effect.

Frozen halves constants (complete-splits era 2023/2024–2025/2026,
presentation only): goals 0.4528, SOT 0.4530, corners 0.4862, total
shots 0.4611, yellow cards 0.3522.

Gates (frozen programme standard, repeated verbatim in every
prereg): dev — goals beats climatology on 1X2 LL AND RPS AND base
rate on OU2.5 LL, else FAIL and variants are moot; counts beat base
rate AND naive trailing-10 on the primary-line LL, else FAIL.
Virgin, read ONCE and only for dev-passers: PASS if LL ≤ best
baseline AND |calibration| ≤ 1pp; PROVISIONAL if a calibration
breach is within 1 SE of the boundary; else FAIL. No dev pass ⇒
virgin NOT read. Gates never move.
