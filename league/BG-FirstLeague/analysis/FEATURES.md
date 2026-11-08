# Step 5 — Features: BG-FirstLeague

Consumption rule: model design may use only adopted features below.
Causality contract as in the J1 template: features for a target match
use only matches strictly before its kickoff; ratios are ratios of
sums; missing data makes the dependent arm inactive for that match,
never filled. All team logic keys on FotMob team id (names unstable
for 2 ids — Step 1). Evidence: Step 3 (`eda_numbers.json`).

| # | Feature | Verdict and evidence |
|---|---|---|
| X1 | xG blend observation pair | **DROPPED.** No `expected_goals` key and no shotmap anywhere in this league (0/1,471). Goals DC is goals-only. |
| X2 | Mover tier offset | **DROPPED as a hard offset; SHRINK retained.** The tier-2 corpus (id 9096) exists and movers were measured against it: 7 pre-virgin entrants, pooled GF gap −0.205, GA gap +0.399 vs league mean. Direction supports the programme-sanctioned SHRINK arm for goals only; no hard-coded offset is estimated. |
| X3 | Set-play xG share/rate | **DROPPED.** No set-play xG key exists. |
| X4 | xG per shot | **DROPPED.** No shotmap. |
| X5 | Trailing target-rate means | **ADOPTED.** Reliabilities (for/against): SOT 0.746/0.645, corners 0.659/0.583, total shots 0.700/0.737, goals 0.535/0.532, event yellows 0.229/0.334. Base feature of every count candidate. Yellows are weak — recorded; the dev gate judges. |
| X6 | Attacking xGOT per shot | **DROPPED.** No shotmap/xGOT. |
| X7 | Opp-box touches | **DROPPED.** `touches_opp_box` key absent from the stats feed in every season. The corners X7 arm therefore cannot exist here. |
| X8 | Referee yellow rate | **ADOPTED as a cards variant arm.** Referee strictness split-half r = 0.379 (20 referees ≥20 matches, 921 matches), referee text coverage ~100% including the virgin (293/293). Moderate signal: arm status, not base design. |
| X9 | Possession + big-chance territorial covariates (corners Gate Zero) | **PARTIALLY ADOPTED.** Possession exists on every stats row and is highly reliable (0.822/0.822). `big_chance` is absent, so the unmodified Gate Zero multiplier (which requires both covariates) is inactive on every row of this league — that is recorded, not patched. A pre-registered **POSS** variant arm uses the identical engine with a possession-only multiplier (beta grid = the J1 possession grid) to test the covariate that actually exists. |

## Halves constants (frozen, presentation only)

From pre-virgin event data (Step 3): goals **0.4542**, yellow cards
**0.3183**. SOT, corners, total shots: **null — FT-only** (no period
splits and no event source exist in this league; RU-1Division
precedent). Per-match share variance ≈ noise for goals; cards carry
a small true variance (+0.0075) but remain constant-presented per
programme rule.
