# Step 5 — Features: TH-ThaiLeague

Consumption rule: model design may use only adopted features below.
Causality contract as in the J1 template: features for a target match use
only matches strictly before its kickoff; ratios are ratios of sums;
missing data makes the dependent arm inactive for that match, never filled.

| # | Feature | Verdict and evidence |
|---|---|---|
| X1 | xG blend observation pair | **DROPPED.** `expected_goals` exists only in 2025/2026 (virgin), 2026/2027 and 1 match in 2024/2025 — the xG era begins inside the virgin. Goals DC is goals-only. |
| X2 | Mover tier offset | **MEASURED, conditional.** Thai League 2 (id 9498) observed movers n=6: first-season GF gap −0.262, GA gap +0.503 vs T1 mean. Supports the sanctioned SHRINK arm for goals only; no hard-coded offset. |
| X3 | Set-play xG share/rate | **DROPPED.** `expected_goals_set_play` exists only in the xG era (virgin onward). |
| X4 | xG per shot | **DROPPED.** Shotmap exists only from the virgin season. |
| X5 | Trailing target-rate means | **ADOPTED.** Reliabilities (for/against): SOT 0.694/0.594, corners 0.690/0.506, total shots 0.687/0.771, stats yellows 0.522/0.380, goals 0.734/0.374. Base feature of every count candidate. |
| X6 | Attacking xGOT per shot | **DROPPED.** Shotmap/xGOT absent before the virgin. |
| X7 | Opp-box touches | **ADOPTED (corners variant).** Reliability 0.819/0.751 — the strongest territorial trait here. Coverage: 174/240 in the 2022/2023 seed, 203/240 in 2023/2024, full from 2024/2025; the arm is inactive where a team's trailing touches are missing. |
| X8 | Referee yellow rate | **DROPPED.** Split-half referee strictness r = 0.199 (weak), and referee text coverage collapses to 9/240 in the virgin season — the feature could not even be evaluated where it must predict. |
| X9 | Possession + big-chance territorial covariates | **ADOPTED (corners Gate Zero, J1 pattern).** Possession reliability 0.849/0.849, big chance 0.564/0.493; both keys present on every stats match. |

## Halves constants (frozen, presentation only)

From pre-virgin split-era matches (Step 3): goals 0.4402 (HT goal events),
SOT 0.4447, corners 0.4622, total shots 0.4522, yellow cards 0.3076
(period splits). Per-match share variance ≈ noise for the first four;
cards carry a small true variance (0.008) but remain constant-presented
per programme rule. All five markets have a legitimate halves source —
no FT-only market in this league.
