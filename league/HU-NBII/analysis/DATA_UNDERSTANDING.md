# Data understanding — HU-NBII (FotMob 9117)

## Inventory

The index has 344 rows: 240 in 2025/2026 and 104 in 2026/2027. The builder
reads the warehouse payloads, not the index flags, and writes the 200 rows that
meet the finished-score rule.

| class | 2025/26 | 2026/27 | total | treatment |
|---|---:|---:|---:|---|
| genuine (`finished=true`, scoreStr) | 96 | 104 | 200 | included |
| partial (`finished=false`, scoreStr) | 41 | 0 | 41 | excluded |
| missing scoreStr | 103 | 0 | 103 | excluded |

The 103 missing-score rows are pre-match fetches recorded as index 0-0, mostly
rounds 4–23 (2025-08-17 through 2026-03-22). The 41 scored-but-unfinished rows
are mid-match captures: no completed-game marker is reliable, their last event
minute has median 45 and maximum 70 among the 22 partial payloads with a timed
event. None of the 41 has `gameEnded` or `secondHalfEnded`; their mean recorded
score is 0.805 goals/match. They are not final results. The inclusion rule is
mechanical and does not infer a result from either class. Partial per-round
recorded-goal means are: R1 1.000 (n=3), R2 1.500 (n=2), R4 1.250 (n=4), R5
0.167 (n=6), R6 0.200 (n=5), R7 1.200 (n=5), R8 0.250 (n=8), R9 0.800 (n=5),
R10 0.667 (n=6), R11 0.800 (n=5), R12 0.000 (n=8), R13 0.000 (n=8), R14
0.000 (n=8), R15 0.000 (n=7), R16 0.000 (n=8), R17 0.000 (n=8), R18 0.000
(n=8), R19 0.000 (n=8), R20 0.000 (n=8), R21 0.000 (n=8), R22 0.000 (n=8),
R23 0.000 (n=8). These are diagnostic means, never league levels.

Goal events total 562 across the payloads. Event goals match the score in
237/241 payloads with a scoreStr. The four mismatches are 4842123 (2025/26,
score 0-2 vs events 0-1), 4842138 (1-1 vs 1-0), 4842140 (1-0 vs 0-0), and
4842146 (1-0 vs 0-0). Final score remains authoritative for the CSV.
Among finished scored payloads, nine have an empty `gameEnded` but a populated
`secondHalfEnded`; their goal events corroborate their scores and they remain
included. One additional finished 0-0 has neither marker and no goal event;
its score is retained by the registered finished-plus-scoreStr rule.

## Field coverage

| field | 2025/26 (240) | 2026/27 (104) | interpretation |
|---|---:|---:|---|
| scoreStr | 137 | 104 | 2025/26 has 103 missing |
| finished | 96 | 104 | partial captures explain the gap |
| genuine score | 96 | 104 | CSV inclusion |
| non-empty events | 110 | 101 | goal/card event feed is incomplete |
| non-empty stats | 0 | 0 | no SOT/corners/cards/shots stats |
| non-empty shotmap shots | 0 | 0 | empty skeleton in 344/344 |
| non-empty referee text | 0 | 0 | absent in 344/344 |
| non-empty lineup | 0 | 0 | no usable lineup stats |
| non-empty period splits | 0 | 0 | no market split source |

There are 47 card events in all 344 payloads, about 0.14 per match versus a
normal cards feed. This is an absent/unusable cards target, not a low league
level. The 2025/26 scoreStr set has 202 half markers; the finished-only CSV
has 189 half-marker matches. On those finished matches, event-derived first-half
goals are 234 and final-score goals are 533, a descriptive share of 0.439.

## Calendar and format

2025/26 has 16 teams, rounds 1–30, and 8 matches per round in the index; only
96 of 240 are genuine. 2026/27 has 16 teams after accent normalization and
currently covers rounds 1–13 plus rounds 17 and 24, dated 2026-07-25 through
2026-11-08. The frozen scope is a single 16-team double round-robin of 30
rounds: no split group, playoff, or championship round.

The 2025/26 fetch-wave defect is the central data-quality finding. 2026/27 is
inventory-only under this preregistration and is not read as a virgin
evaluation window.

## Sibling and mover check

HU-NBI (FotMob 212) is completed; G-HU-NBI failed its development gate. The
identifiable transitions are Diósgyőri VTK and Kazincbarcikai BSC relegated
from NB I to NB II, Vasas Budapest promoted from NB II to NB I, and Gyirmót plus
Nagykanizsa entering from NB III. The cross-tier offset is dropped: the useful
mover set is only three relevant NB-II mover teams for this question and there
is no gateable HU-NBII window.
