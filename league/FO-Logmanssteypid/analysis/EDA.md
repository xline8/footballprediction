# Step 3 — EDA: FO-Logmanssteypid (n=6; read as description, not estimation)

All numbers below are computed from the 6 payloads (see
`eda_summary.json`). With n=6 they describe the final series; they
cannot support any fitted parameter, and no reliability statistic is
computed — split-half reliability needs repeated team-seasons, which
do not exist here (each team plays at most one match per year, and
the two finalists meet only in that year's final).

## Levels

| Market | Matches with target | Mean / match | Notes |
|--------|--------------------|--------------|-------|
| Goals (total) | 6/6 | 1.83 | Home 7, away 4; totals 2, 1, 0, 4, 2, 2 |
| Over 2.5 rate | 6/6 | 1/6 = 16.7% | Only 2024 (2–2) went over |
| BTTS rate | 6/6 | 2/6 = 33.3% | 2021 (1–1) and 2024 (2–2) |
| Total shots | 0/6 | — | No stats, no shotmap |
| Corners | 0/6 | — | No stats |
| Shots on target | 0/6 | — | No stats, no shotmap |
| Cards | 0/6 | — | No events, no stats, no referee |
| xG | 0/6 | — | No shotmap |

Reference points: goals 1.83/match sits below the J1/top-5 norm
(~2.6–2.8), but at n=6 the SE on the mean is ±0.5 goals — the
difference is noise, and three of the six finals were 0–0/1–1 draws
decided on penalties. It is description, not a level estimate.

## Home advantage (n=6)

Home wins 2, draws 3, away wins 1; home goals 7 vs away 4 (1.17 vs
0.67 per match). A home edge of that size on 6 matches has a binomial
SE of ~19pp on the home-win rate — consistent with anything from no
advantage to a strong one. No home-advantage parameter is estimated.
(Note also that "home" in a cup final is a nominal designation — the
final is a one-off neutral-venue occasion in practice, which is one
more reason a league home-advantage parameter would not transfer.)

## Halves (no data — NO constants frozen)

No 1H share can be computed for any market: there are no stats
period splits and no goal-minute events in any payload. Nothing is
reported and nothing is frozen (`config.yaml`:
`halves_constants: {}`). No market gets 1H/2H presentation.

## Team traits

Not computable. Split-half reliability by season requires teams with
repeated matches inside a season; the maximum is 1 match per team
per season (the final itself). There is no within-season trait signal
to split, and across seasons a team's Løgmanssteypið history is at
most 2 stale finals. All J1 trait checks (F1–F13 analogues) are
therefore **not run** — the precondition (repeated team-seasons)
fails before the statistic does.

## Referee

No referee field in any payload (0/6). Referee strictness cannot be
measured, and the cards target has no referee arm available. (Cards
are in any case not buildable at n=6 with no card data of any kind.)

## Data-quality findings (payload-level)

1. The events feed is empty in all 6 payloads — not merely missing
   stats, but zero recorded events of any type. The competition's
   FotMob coverage is score-only at the lowest level
   (`coverageLevel: "lower"` in every payload).
2. The index flags agree with the payloads here (`has_stats: False`,
   `has_shotmap: False` on 6/6) — the flag class that lied for
   CO-Superliga does not lie for this competition. `content.shotmap`
   is a present-but-empty key in all 6.
3. Team-name spelling is accent-inconsistent across years ("B36
   Torshavn" vs "B36 Tórshavn"; "Vikingur" vs "Víkingur"). Distinct
   clubs are 6 after normalisation, 8 raw.
