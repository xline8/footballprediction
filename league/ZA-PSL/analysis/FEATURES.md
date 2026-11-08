# Step 5 — Features: ZA-PSL

Consumption rule: model design may use only adopted features below.
Causality contract as in the J1 template: features for a target match use
only matches strictly before its kickoff; ratios are ratios of sums;
missing data makes the dependent arm inactive for that match, never filled.
All team logic keys on FotMob team id (names are unstable for 3 ids —
Step 1).

| # | Feature | Verdict and evidence |
|---|---|---|
| X1 | xG blend observation pair | **DROPPED.** `expected_goals` exists only in 2025/2026 (virgin) and 2026/2027 — the xG era begins inside the virgin. Goals DC is goals-only. |
| X2 | Mover tier offset | **DROPPED as an offset; SHRINK retained.** No South African second tier exists in the warehouse, so no tier-step offset can be estimated. Entrant descriptives measured within this league (n = 5 pre-virgin entrants): GF gap −0.271, GA gap +0.147 vs league mean — direction supports the programme-sanctioned SHRINK arm for goals only; no hard-coded offset. |
| X3 | Set-play xG share/rate | **DROPPED.** `expected_goals_set_play` exists only in the xG era (virgin onward). |
| X4 | xG per shot | **DROPPED.** Shotmap exists only from the virgin season. |
| X5 | Trailing target-rate means | **ADOPTED.** Reliabilities (for/against): SOT 0.607/0.340, corners 0.249/0.567, total shots 0.751/0.630, stats yellows 0.578/0.608, goals 0.480/0.217. Base feature of every count candidate. (Corners-for and goals-against are weak; that is recorded, and the dev gate is the judge.) |
| X6 | Attacking xGOT per shot | **DROPPED.** Shotmap/xGOT absent before the virgin. |
| X7 | Opp-box touches | **ADOPTED (corners variant).** Reliability 0.651/0.725. Coverage: 145/240 in the 2022/2023 seed, 190/240 in 2023/2024, full from 2024/2025; the arm is inactive where a team's trailing touches are missing. |
| X8 | Referee yellow rate | **DROPPED.** Split-half referee strictness r = 0.080 (noise) over 10 referees / 213 matches, AND referee text coverage is sparse in dev (62–82 per season) and collapses to 13/240 in the virgin — the feature could not even be evaluated where it must predict. Fails both legs. |
| X9 | Possession + big-chance territorial covariates | **ADOPTED (corners Gate Zero, J1 pattern).** Possession reliability 0.847/0.847, big chance 0.552/0.442; both keys present on every stats match. |

## Halves constants (frozen, presentation only)

From pre-virgin split-era matches (Step 3): goals 0.4724 (HT goal
events), SOT 0.4736, corners 0.4679, total shots 0.4584, yellow cards
0.3253 (period splits). Per-match share variance ≈ noise for the first
four; cards carry a small true variance (0.0051) but remain
constant-presented per programme rule. All five markets have a
legitimate halves source — no FT-only market in this league.
