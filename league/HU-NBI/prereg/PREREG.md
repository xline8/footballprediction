# HU-NBI preregistration — Phase A

Frozen before fitting. There are no LL numbers, fitted parameters, walk-forward results, or virgin reads in this phase.

## Windows and targets

Development is an expanding, season-blocked walk-forward over 2022/2023, 2023/2024, and 2024/2025. Virgin is 2025/2026, the last complete 198-match season, read once and only for arms that pass development. 2026/2027 is in progress and remains reserved; it is not used for any design statistic. The target fields exist in the dev and virgin windows: goals and event cards on all rows; SOT, corners, and total shots on 193/198, 197/198, 198/198 in dev seasons and 198/198 in virgin. Missing stat rows are omitted only from that target's fit/evaluation, never imputed.

Cards are event-unified `Yellow + YellowRed`; the feed has zero `yellow_cards`/`red_cards` stat-key rows, so no stats-vs-events agreement comparison exists and events are the target by construction. `Red` and `YellowRed` are not a red-card market target; red is descriptive only. Plain `Yellow` events occur in all seasons.

## Coordinator correction (pre-fitting, before this commit)

The Phase A draft carried dev means and half constants computed from a superseded builder intermediate. Recomputed from the committed hu_nbi.csv: dev means goals 2.8384 / SOT 8.5646 / corners 10.0136 / cards 4.5825 / total shots 19.0425; by the stated nearest-.5 rule the total-shots primary line is 19.5 (not 18.5); all other lines unchanged (2.5 / 8.5 / 9.5 / 4.5). Half constants re-frozen on the fit window only (virgin excluded): goals 0.4471, cards 0.3644. No fitting had taken place; the freeze below is the corrected one.

## Arms and gates

For each candidate, Gate Zero is the unmodified production analogue: goals-only DC for goals, v5 `model_sot.py` for SOT, `model_corners_v3.py` for corners with the available possession covariate, `model_cards.py` for cards, and J1 total-shots arm A v1 for total shots. Registered variants are only the arms listed in `MODEL_DESIGN.md` and `FEATURES.md`; there are no rescue arms.

The development gate is: the arm's log likelihood at the primary line must beat both the league base rate and naive trailing-10 baseline, plus the per-season sign check used by the program (LL improvement over each baseline must be positive in every scored development season). An arm failing development does not read virgin.

Virgin legs, for every arm passing development, are (i) LL beats the best baseline and (ii) calibration: absolute breach ≤1 percentage point is clean PASS; ≤1 standard error is PROVISIONAL PASS; otherwise FAIL. Calibration is actual minus predicted. Tie rule: the simpler arm wins, and Gate Zero ships. Gates never move after results are seen. If no arm passes development, the candidate's virgin is deliberately unread and nothing ships.

The only halves mechanism is the frozen goals share 0.4471 and cards share 0.3644 (pooled 2021/22–2024/25 fit window, virgin excluded), presentation only. SOT, corners, and total shots have null half shares.
