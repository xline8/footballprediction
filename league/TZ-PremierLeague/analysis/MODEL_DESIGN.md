# Step 6 — Model design: Tanzania Premier League

No fitting, preregistration, engine, predictions or virgin read is performed in this brief.

## 1 Feasibility matrix

| Candidate | target exists | virgin target | status |
|---|---|---|---|
| G-TZ goals | yes, 1,282 eligible scores | yes, 239 eligible 2025/2026 rows | BUILD |
| S-TZ SOT | no, 0/1,284 | no | NOT BUILDABLE |
| C-TZ corners | no, 0/1,284 | no | NOT BUILDABLE |
| K-TZ cards | no yellow target; 114 dismissals only | no | NOT BUILDABLE |
| T-TZ total shots | no, shotmap shots 0/1,284 | no | NOT BUILDABLE |

## 2 G-TZ goals design

Gate Zero is the production Dixon–Coles `model_v2.py` class `DC`: 14 sweeps, damping 0.7, +0.25 smoothing, fitted home-advantage initial value 0.28, attack/defence initial values 0, MAXG 10, production tau, and rho grid (0.0, −0.05, −0.10, −0.15) selected by weighted goals-only LL. Time decay is frozen at half-life 270 days. Fits use all eligible matches dated strictly before the target season's first match date; unseen teams start at league mean; names are the team key; parentLeagueId 9066 is one pooled table; both AW rows are excluded.

The only variant is **SHRINK**: for a team with n<6 prior in-league matches, set a*=a·n/6 and d*=d·n/6; n=0 is the unseen-team rule. Unlike the Ghana case, the arm is a real test here: Fountain Gate FC enters 2023/2024 with n=1 under its own name and Singida Black Stars enters 2024/2025 with n=2 under its own name.

### Dev protocol

Seed 2021/2022; evaluate 2022/2023, 2023/2024 and 2024/2025. Pooled scored n=720 (240 each). The harness reads no 2025/2026 or 2026/2027 rows. Report per-season and pooled 1X2 LL, RPS, and OU2.5 LL for each arm, against climatology and naive trailing-10. Primary line is OU2.5, with 1.5/2.5/3.5 ladder reporting.

### Virgin protocol

The primary virgin window is complete 2025/2026 with eligible n=239; fit on all eligible matches before its first match. Report calibration as actual minus predicted for home-win rate and OU2.5 over-rate, with SE=sd(pred−y)/sqrt(n). 2026/2027 is confirmatory and reserved: 84 matches are in progress.

### Gates

Dev gate: pooled 1X2 LL and RPS must beat climatology and OU2.5 LL must beat its base-rate baseline; otherwise the arm is dead. Virgin leg (i): LL ≤ Gate Zero and ≤ climatology. Virgin leg (ii): absolute calibration error ≤1.0 percentage point for both rates; a breach within 1 SE is PROVISIONAL PASS, otherwise FAIL. Virgin leg (iii): per-season sign check for the both-pass rule. Ties go to the simpler arm. If Gate Zero fails dev, variants are moot and virgin is not read. A failed candidate ships nothing.

Outputs for the next brief are the goals engine, dev results, virgin results/params, predictions on PASS, and verdict report. Halves are presentation-only using 0.4867818118.
