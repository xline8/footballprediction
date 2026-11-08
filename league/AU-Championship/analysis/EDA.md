# Step 3 — EDA: AU-Championship

Levels are computed from `data/au_championship_matches.csv` (87
rows). 2025 is the only complete season; 2026 is TRANSITIONAL
(rounds 1–4 of 6, final stage unplayed) and its levels are inventory
only — no arm is fitted or scored against 2026 anywhere in this
build. Reference points: J1 goals 2.68/match, AU-ALeague ~2.9/match;
top-5 Europe ~2.6–2.9/match.

## F1 — Goals levels (the only target that exists)

| Season | n | Mean goals | Home goals/m | Away goals/m | Home win | Draw | Away win | Over 2.5 |
|---|---|---|---|---|---|---|---|---|
| 2025 (complete) | 55 | 3.218 | 1.909 | 1.309 | 47.3% (26) | 23.6% (13) | 29.1% (16) | 56.4% (31) |
| 2026 (transitional) | 32 | 2.906 | 1.344 | 1.562 | 31.2% (10) | 25.0% (8) | 43.8% (14) | 62.5% (20) |
| Pooled | 87 | 3.103 | 1.701 | 1.402 | 41.4% (36) | 24.1% (21) | 34.5% (30) | 58.6% (51) |

- The Championship is a high-scoring competition: 3.10 goals/match
  pooled, above J1 (2.68) and above its A-League sibling. The 2025
  home/away split (1.91 vs 1.31) is a normal home advantage; the
  2026 reversal (1.34 home vs 1.56 away) is noise at n=32 — the
  home-win rate swings 16pp between the two seasons, which is what
  n=32–55 does to a rate (SE ≈ 8–9pp).
- Total-goals distribution (pooled): 0 goals 7, 1: 10, 2: 19, 3: 17,
  4: 12, 5: 12, 6: 7, 7: 3. Seven 0-0s (8.0%) — all finished
  matches, genuine scoreless draws (Poisson expectation at
  λ=3.10 is ~4.5%; 8.0% is ~1.2 SE above it at n=87).
- Final stage 2025 (n=7): 19 goals, mean 2.71/match — below the
  group stage (3.29/match, 158 goals in 48). Knockout caution is
  visible even at n=7, but n=7 cannot support a phase split in any
  future design; it is recorded here as context only.

## F2 — Home advantage

2025: home win 47.3% vs away win 29.1% (18.2pp gap). 2026:
home win 31.2% vs away win 43.8% (−12.6pp). Pooled: 41.4% vs 34.5%
(+6.9pp). The sign flip between seasons is a small-sample artefact,
not a finding: with 16 teams playing 6 group matches each, a
season's home-win rate is dominated by which clubs host the strong
sides. No home-advantage parameter is estimable to gate standard
from one complete season.

## F3 — Half shares (frozen-constant question)

**Not testable.** No period splits exist in any of the 87 payloads
(`content.stats` null; `header.status.halfs` holds timestamps only).
No halves constant is frozen for any market; there is no 1H/2H
presentation. (For scale: the J1 goals constant 0.412 was measured
on thousands of matches; this league has zero split observations.)

## F4 — Team traits (split-half reliability)

**Not computable.** The J1 checklist (split-half by season) needs
repeated team-seasons with enough matches per team to split. Here
each club plays 6–9 matches in a season and 12 of 16 clubs appear
in both seasons — a split-half correlation over ~6 matches per half
would be pure noise, and with a single complete season there is no
second season to validate against. No team trait (attack, defence,
set-play, or any other) is claimed reliable in this league. This is
a structural fact about the sample, not a gap that more collection
within 2025 could fix.

## F5 — SOT / corners / cards / total shots levels

**No data.** The targets do not exist in any payload (stats null
87/87, shotmap empty 87/87, events empty 87/87). No levels can be
reported, not even descriptively. The only card-adjacent signal,
red-card counts in `header.status`, is near-zero-filled (≥1 red in
12/1,333 parent matches) and is not a yellow/total-cards target.

## F6 — Referee

No referee field in any payload (blank in 1,333/1,333). Referee
strictness cannot be measured; X8 is unavailable in principle.

## F7 — Cross-tier (X2) evidence

- A-League overlap: 0 clubs (13 A-League senior clubs vs 20
  Championship clubs, disjoint). No mover prior from the sibling.
- State-league overlap: all 20 Championship clubs play in state
  leagues, but that is same-season concurrent form (state Feb–Sep,
  Championship Oct–Dec), not a prior-season mover offset, and 48%
  of state scores are unrecorded. Rejected as a feature
  (MODEL_DESIGN.md §4).

## F8 — Format change (2026 shootouts)

Drawn group matches went to a shootout in 2026 (8/8 draws, no ET)
and did not in 2025 (0/12 group draws; the only 2025 shootout was
the QF after ET). Any future goals design must decide the
points/1X2 treatment of shootout-decided draws before fitting —
the stored score is the drawn score in both seasons, so 1X2
markets are unaffected, but a points-based table (if one were ever
modelled) would need the bonus-point rule, which is not in the
payloads and was not verified against an external source.

## Summary

One complete season of a high-scoring (3.22 goals/match), 16-team
competition, scores-only, no stats, no splits, no referee, no
reliable team trait, and a format change in the transitional
season. That is the whole dataset. Nothing in it supports a gate.
