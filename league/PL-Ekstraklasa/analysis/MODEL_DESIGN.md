# Phase 4 — Model Design: PL-Ekstraklasa Candidates

This is a candidate design only. Stage 1 performs no fitting and no dev or virgin evaluation. The dev window is a season-blocked walk-forward over the dev period 2021/2022–2024/2025 (1,224 matches including the 2021/2022 training seed; scored seasons 2022/2023–2024/2025, 918 matches). Primary-line over-rates below are computed over the full dev period (the BE convention). The primary virgin is 2025/2026 (306 matches), read once only after dev gates. 2026/2027 (124 matches) is confirmatory and must not be read here.

The phase rule is frozen: every row is `regular`; there is no split/play-off phase and no phase feature. Calibration is defined as **actual minus predicted** everywhere. Candidate arms are compared only after Gate Zero; no preregistration or result files are created in this stage.

| Candidate | Reference / Gate Zero | Primary .5 line (dev over-rate) | Candidate arms |
|---|---|---|---|
| G-PL goals | Dixon–Coles goals pattern with the X1 blend | OU 2.5 (0.482) | Gate Zero; SHRINK for thin-data team priors. X3 is NOT run: set-play xG is full only from 2025/2026 — an era starting inside the virgin kills the arm (ES lesson) |
| S-PL SOT | `model_sot.py` reference | 8.5 (0.492) | Gate Zero; RS ratio-shrink; X4 only if xG/shot reliability reaches ~0.35 on a usable era; X6 is dropped |
| C-PL corners | `model_corners_v3` reference with X9 | 9.5 (0.551) | Gate Zero; X7 box-touch multiplier only if the trailing availability gate passes |
| K-PL cards | `model_cards.py` reference | 3.5 (0.567) | Gate Zero; X8 referee arm only when referee coverage and reliability gates pass |
| T-PL total shots | A/B/C shots-family reference | 25.5 (0.526) | Arms A, B, and C are candidates; no extra PL feature is added |

X1 honesty note: stats-feed xG exists in only 10 of the 1,224 dev-period matches (4 in 2023/2024, 6 in 2024/2025 — exactly the stray shotmap matches) and becomes full only in 2025/2026. Gate Zero's blend therefore runs effectively goals-only through dev and through the virgin fit (whose training window ends 2024/2025); the blend weight is the production pattern with its documented goals-only fallback, not a fitted xG effect. xG observations enter training windows only for fits made after 2025/2026 data exists. This is also why X3 and X4 are dead: their eras start inside the virgin season.

Line selection is mechanical: among candidate .5 lines, choose the development over-rate closest to 0.5. For context, the adjacent development rates are SOT 9.5 = 0.364 and 10.5 = 0.260; corners 10.5 = 0.441 and 11.5 = 0.329; cards 4.5 = 0.392 and 5.5 = 0.241; shots 26.5 = 0.448 and 27.5 = 0.379. Goals uses the only requested 2.5 line.

No model-fitting result, virgin result, odds result, or calibration verdict belongs in this Stage 1 directory. The later evaluation must report calibration as actual minus predicted and preserve the season-blocked signed-age rule.
