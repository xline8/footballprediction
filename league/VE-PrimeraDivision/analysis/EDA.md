# Step 3 — EDA: VE-PrimeraDivision

All calculations are in `eda_compute.py`; the complete numeric output is `eda_numbers.json` and the committed chart set is under `charts/`.

## Levels and windows

Regular goals/match are 2.6905, 2.4333, 2.4857, 2.3077, 2.3352, and 2.6099 for 2021–2026. Regular home/away goal means are respectively 1.4563/1.2341, 1.3875/1.0458, 1.4238/1.0619, 1.2857/1.0220, 1.3571/0.9780, and 1.4560/1.1538. Stats-era regular levels are: 2025 SOT 8.2857, corners 8.8022, stats yellows 5.9677, total shots 23.7143; 2026 SOT 8.7403, corners 9.0497, stats yellows 5.5912, total shots 26.5083.

The goals dev window (regular 2023+2024, n=392) has mean 2.4031, OU2.5 over-rate 0.4388, and home-win rate 0.4286. Counts are frozen descriptively in `eda_numbers.json`: 2026 Apertura is the dev window, 2025 Clausura the seed, and 2026 Clausura the transitional virgin window.

## Split-half reliability

The alternating chronological split requires at least six matches per team. Full values for goals, SOT, corners, stats yellows, total shots, possession, big chances, and on-target rate are in the JSON for 2025 Clausura, 2026 regular, and pooled stats-era samples. Headline pooled correlations are goals for/against .461/.336, SOT for/against .274/.359, corners for/against .615/.264, yellow for/against .156/.587, total shots for/against .558/.395, possession .655, and on-target rate −.300. The 2025 sample has only 13 rounds per team and should be treated as thin-sample evidence.

## Halves and artifacts

Ratio-of-sums first-half shares are goals .4478 (n=947), SOT .4651 (n=243), corners .4669 (n=242), total shots .4662 (n=243), and stats yellows .3900 (n=241). The variance decomposition (observed variance of per-match shares minus the binomial floor `mean(p(1-p)/n_i)` at the pooled share `p`) gives true variance ≈ 0 for goals (−0.0004), SOT (−0.0002) and total shots (+0.0003), and a small positive residual for corners (+0.0042, SD ≈ 0.065) and stats yellows (+0.0056, SD ≈ 0.075). Per-match 1H share is therefore noise around a frozen constant for every market; the constants are presentation-only, never fitted per team. (An earlier draft of this EDA computed the noise floor from each match's own share, which collapses the floor toward 0 and fabricates positive true variance; the formula was corrected to the pooled share and the numbers above are the corrected ones.) The 2026 event-card audit share is .3783 versus .3900 from stats-period cards; event cards are overcounted and are not the K source.

Two tiers of stats feed in 2025 Clausura: of the 117 stats matches, 62 carry the full feed (all groups + period splits) while 55 carry a reduced feed — `Periods.All` only, 'Top stats' group only (possession, total shots, SOT, corners). Yellows, fouls, reds, passes, keeper saves, shots off target and blocked shots therefore exist in only 288 stats-era matches (62 in 2025 + 226 in 2026); SOT, corners, total shots and possession exist in all 343. The K seed (2025 Clausura regular) has yellows in 62 of its 91 matches.

`big_chance` is 0 in all 288 full-feed matches (nonzero in 0/288) — the key exists but the feed never populates it, so the big-chance covariate of X9 is dead in this league (possession is the only live X9 input). `shots_inside_box` / `shots_outside_box` are likewise 0 in all 288. Referees are named in 87/233 matches in 2025 and 145/227 in 2026 (the `Referee` key is present but empty-text in the other 2025 matches).

2026 drift (regular, Apertura → Clausura): total shots 24.64 → 28.40, SOT 8.25 → 9.23, corners 8.74 → 9.37, stats yellows 6.16 → 5.01, goals 2.56 → 2.66. The rise in shots/SOT/corners builds month by month through 2026 (shots: Feb–Apr ≈ 24–25, Aug 27.1, Sep 29.2, Oct 30.0) while yellows fall — a genuine regime drift, not a single feed step. The virgin window (2026 Clausura) therefore sits at materially higher count levels than the dev window (2026 Apertura); the calibration legs will be hard and the gate decides. 2025 levels are Clausura-only (n=91 regular with stats).

The stats-vs-events agreement table, event-card coverage, referee counts, and per-key nonzero counts are in `eda_numbers.json`. Event cards are ~absent before 2026: in 2025 Clausura, event-unified yellows total 3 versus 370 stats yellows, exact agreement 0/62; in 2026 they total 1,388 versus 1,276 stats yellows, exact in 155/226. Shotmap/xG absence is asserted: 0 non-empty shotmaps and 0 expected-goals keys. Several keys are absent or zero-filled, including inside/outside-box shots, accurate crosses/long balls, interceptions, clearances, duels, successful dribbles, and touches in the opposition box.

## J1 checklist status

SIGNAL: goals, corners, total shots, possession, and some SOT traits have usable descriptive reliability. NOISE / weak: cards as a team-trait signal and the 2025 on-target-rate result. NOT RUNNABLE: X2 second-tier prior, X8 referee reliability, and any xG/shotmap-based X1 refinement; X3, X4, X6 are impossible without shotmaps/xG; X7 is dropped because `touches_opp_box` is absent. K uses stats yellows, not event-unified cards.
