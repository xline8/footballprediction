# Step 5 — Features: TH-ThaiLeague2

Consumption rule: model design may use only adopted features below.
Causality contract as in the J1 template: features for a target match use
only matches strictly before its kickoff; ratios are ratios of sums;
missing data makes the dependent arm inactive for that match, never filled.

| # | Feature | Verdict and evidence |
|---|---|---|
| X1 | xG blend observation pair | **DROPPED.** No xG exists in any payload (stats feed null in 681/681; shotmap empty in 681/681). Goals DC is goals-only. |
| X2 | Mover tier offset | **MEASURED, conditional.** Parent T1 corpus (id 8984) exists under `league/TH-ThaiLeague/data/`. Relegated movers into the dev season n=3 with mixed gaps (Chonburi +0.397/−0.416; Police Tero −0.135/+0.147; Trat −0.172/+0.131). Supports the sanctioned SHRINK arm for goals only; no hard-coded offset. |
| X3 | Set-play xG share/rate | **DROPPED.** `expected_goals_set_play` absent (stats feed null). |
| X4 | xG per shot | **DROPPED.** Shotmap absent in every match. |
| X5 | Trailing target-rate means | **ADOPTED for goals and cards only.** Reliabilities (dev-season split-half, for/against): goals 0.353/0.522, event yellows 0.287/0.099 (against near noise — recorded). For SOT/corners/total shots there is no target to trail: not applicable, those candidates are not buildable. |
| X6 | Attacking xGOT per shot | **DROPPED.** Shotmap/xGOT absent in every match. |
| X7 | Opp-box touches | **DROPPED.** `touches_opp_box` absent (stats feed null). |
| X8 | Referee yellow rate | **DROPPED, not measurable.** Referee text coverage is 0/273 in the dev season and 0/306 in the virgin (72/90 only in the confirmatory season). No reliability check can be run and the feature could not predict where it must. |
| X9 | Possession + big-chance territorial covariates | **DROPPED.** Both keys absent (stats feed null). There is no corners candidate for them to serve in any case. |

## Halves constants (frozen, presentation only)

From dev-season regular matches, event-derived (Step 3): goals **0.4249**
(HT goal events), yellow cards **0.3322** (card event times <= 45).
Per-match share variance ≈ noise for both. SOT, corners and total shots
have no legitimate halves source in this league's data (no period splits;
no events for those markets) and are frozen **FT-only** — in practice the
point is moot, as those candidates are not buildable at all.
