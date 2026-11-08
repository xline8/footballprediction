# Step 3 — Exploratory data analysis

All figures below are generated from eligible rows in `tz_matches.csv`; exact machine-readable values are in `eda_numbers.json`.

## 1 Levels

| Season | n | goals/match | H | D | A | O2.5 | BTTS | 0–0 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 2021/2022 | 239 | 1.958 | .423 | .339 | .238 | .301 | .418 | .146 |
| 2022/2023 | 240 | 2.338 | .492 | .225 | .283 | .417 | .458 | .063 |
| 2023/2024 | 240 | 2.154 | .433 | .317 | .250 | .388 | .429 | .154 |
| 2024/2025 | 240 | 2.383 | .479 | .246 | .275 | .446 | .383 | .104 |
| 2025/2026 | 239 | 2.172 | .452 | .285 | .264 | .393 | .360 | .134 |
| 2026/2027 | 84 | 2.405 | .548 | .202 | .250 | .417 | .476 | .048 |
| pooled | 1,282 | 2.215 | .462 | .277 | .261 | .391 | .414 | .115 |

The supplied coordinator levels (1.962, 2.337, 2.154, 2.383, 2.175, 2.405) use the full 240-row season denominators for the two seasons containing AW rows; the eligible-row recomputation above is the frozen preprocessing definition. Tanzania is below J1's 2.68 goals/match, above Ghana's 2.02 and close to the NG reference 2.11.

No SOT, corners, cards-as-yellow-target, or total-shot levels exist: stats are non-empty in 0/1,284 and shotmap shots in 0/1,284.

## 2 Team trait reliability

Within each season, matches are chronological; each team-season must have at least 10 matches and at least 5 in each half. The split-half Pearson r values are attack / defence: 2021/2022 .534/.701; 2022/2023 .769/.605; 2023/2024 .852/.571; 2024/2025 .658/.874; 2025/2026 .798/.710; 2026/2027 .202/.151. Each season contributes 16 team-seasons; pooled n=96 gives attack r=.575 and defence r=.490.

## 3 Home advantage

Pooled eligible mean home goals is 1.300 and away goals .914, a +.386 goal home difference. The pooled home-win rate is .462 versus away-win .261; the per-season rates are in the levels table and JSON.

## 4 Half shares

The trusted eligible HT sample is 1,146 matches and 1,381 first-half goals. First-half share is a ratio of sums. By season: 2021/2022 209 matches, .4979; 2022/2023 227, .4670; 2023/2024 202, .4660; 2024/2025 218, .5017; 2025/2026 209, .4913; 2026/2027 81, .5149. The frozen pooled goals constant is **0.4867818118**.

Per-match observed share variance is .131935; the binomial noise floor is .133540, giving excess variance −.001605. Team-season split-half share reliability is r=.168 over 93 eligible team-seasons. The constant is therefore presentation-only, not a team feature.

## 5 Turnover and movers

There are 26 distinct names. New/out sets by season are stored exactly in `inventory_summary.json`. The two rename footnotes are retained: Fountain Gate FC is a one-match name after Singida Big Stars' 29 matches in 2022/2023; Singida Black Stars is a two-match name after Ihefu FC's 28 matches in 2023/2024. Names are never merged.
