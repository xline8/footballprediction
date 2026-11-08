# Phase 3.5 — Features: RU-1Division

The consumption rule is strict: model design may use only adopted features in
this table and the architectural components named there. Any rejected item
stays out unless this document is amended with new evidence.

| # | Feature | Verdict and evidence |
|---|---|---|
| X1 | xG blend observation pair | **DROPPED.** No xG, set-play xG, or shotmap exists in any row. Goals-only DC is the only eligible goals observation. |
| X2 | Mover tier offset | **MEASURED, conditional.** The parent corpus contains 1,312 RU-Premier rows. Relegated movers n=9 have prior RU-Premier GF/GA 0.941/1.707 and first-season RU-1Division GF/GA gap +0.233/-0.126. Promoted/other n=11 has gap -0.136/+0.059; returning n=3 has -0.139/+0.087. Use only as a shrinkage/offset arm; no hard-coded offset. |
| X3 | Set-play xG share/rate | **DROPPED.** Set-play xG is absent. |
| X4 | xG per shot | **DROPPED.** Shotmap is empty in all 1,756 rows. |
| X5 | Trailing target-rate means | **ADOPTED.** SOT, corners, and total shots use stats rows; cards use event-unified yellows. Reliabilities are SOT 0.673/0.633, corners 0.612/0.661, total shots 0.751/0.714, event yellows 0.722/0.724 for/against. |
| X6 | Attacking xGOT per shot | **DROPPED.** Shotmap and xGOT are absent. |
| X7 | Opp-box touches | **DROPPED.** `touches_opp_box` is absent. |
| X8 | Referee yellow rate | **DROPPED.** Referee text coverage is 0.0% in every season. |
| X9 | Possession + big-chance territorial covariates | **POSSESSION-ONLY ADOPTED AS A CORNERS COVARIATE.** Big chance is absent, while possession for/against reliability is 0.844/0.839. The corners design carries possession only; the full RU-Premier pair is impossible. |

All target features obey the causal contract: trailing windows use only
matches strictly before kickoff, ratios are ratios of sums, and missing stats
remain missing. First-half shares are not features. SOT, corners, cards, and
total shots have FT presentation only.
