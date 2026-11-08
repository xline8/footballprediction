# Step 3 — EDA: CO-Superliga (n=12; read as description, not estimation)

All numbers below are computed from the 12 payloads (see
`eda_summary.json`). With n=12 they describe the tie series; they cannot
support any fitted parameter, and no reliability statistic is computed —
split-half reliability needs repeated team-seasons, which do not exist
here (each team appears in at most one tie per year).

## Levels

| Market | Matches with target | Mean / match | Notes |
|--------|--------------------|--------------|-------|
| Goals (total) | 12/12 | 2.42 | Home 18, away 11 |
| Over 2.5 rate | 12/12 | 4/12 = 33.3% | Totals: 3,5,2,1,1,7,1,2,2,0,2,3 |
| BTTS rate | 12/12 | 6/12 = 50.0% | |
| Total shots | 7/12 | 24.43 | Stats era 2023+ only (171 shots) |
| Corners | 7/12 | 9.86 | Stats era only (69 corners) |
| Shots on target | 7/12 | 8.14 | Stats-block; shotmap SOT 68 in 4 matches (2025–26) |
| Cards (Card events) | 12/12 | 8.08 | Events feed; includes 2nd-yellow/red cards as Card events |
| xG (stats-block) | 4/12 | — | 2025–26 only; values 2.15/0.23, 0.11/0.97, 1.09/0.86, 1.05/0.76 |

Reference points: goals 2.42/match sits below the J1/top-5 norm (~2.6–2.8)
but at n=12 the SE on the mean is ±0.4 goals — the difference is noise.
Corners 9.86 and SOT 8.14 are in the normal range for the same reason:
they are description, not a level estimate.

## Home advantage (n=12)

Home wins 6, draws 4, away wins 2; home goals 18 vs away 11 (1.50 vs
0.92 per match). A home edge of that size on 12 matches has a binomial
SE of ~14pp on the home-win rate — consistent with anything from no
advantage to a strong one. No home-advantage parameter is estimated.

## Halves (descriptive only — NO constants frozen)

| Market | 1H share | Basis |
|--------|----------|-------|
| Goals | 0.345 (10/29) | Goal events by minute (≤45') |
| Total shots | 0.421 (72/171) | Stats 1H splits, 7 matches |
| Corners | 0.464 (32/69) | Stats 1H splits, 7 matches |
| SOT | 0.386 (22/57) | Stats 1H splits, 7 matches |

Every share is within noise of the frozen top-5 constants at these n
(SE ≈ 0.06–0.09), and the goals share (0.345) is computed over 29 goals.
Per the program's frozen-constant rule these would need a real sample to
freeze; at n=7–29 they are reported and **not frozen** (`config.yaml`:
`halves_constants: {}`). No market gets 1H/2H presentation.

## Team traits

Not computable. Split-half reliability by season requires teams with
repeated matches inside a season; the maximum is 2 matches per team per
season (the two legs of one tie), and the two legs are against the same
opponent a week apart. There is no within-season trait signal to split,
and across seasons a team's Superliga history is at most 2 stale matches.
All J1 trait checks (F1–F13 analogues) are therefore **not run** — the
precondition (repeated team-seasons) fails before the statistic does.

## Referee

No referee field in any payload (0/12). Referee strictness cannot be
measured, and the cards target has no referee arm available. (Cards are
in any case not buildable at n=12.)

## Data-quality findings (payload-level)

1. `yellow_cards` stats-block is zero-filled [0, 0] in all three
   2023/2024 stats matches while the same matches' event feeds contain
   9, 10 and 5 Card events — the field is unusable before 2025.
2. The index `has_shotmap=True` for 2025/2026 is key presence only;
   `shotmap.shots` is empty in 8/12 payloads. Real shotmap coverage is
   4 matches.
3. 2024 leg 2 has no stats block while its pair (leg 1) does — coverage
   is leg-asymmetric, not season-asymmetric.
