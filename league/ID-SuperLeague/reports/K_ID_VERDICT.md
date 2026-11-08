# Verdict — K-ID (cards): **FAIL** (dev gate; virgin deliberately unread)

Prereg: `prereg/PREREG_K_ID.md` (frozen before fitting). Target:
event-unified yellows (direct Yellow + YellowRed events), scored only
on events_complete matches, because the stats feed has no cards key
at all in this league. Primary line 4.5. Nothing ships.

## Dev results (seed 2021/2022; scored seasons on complete-feed rows)

| season | n | gate_zero LL | x5 LL | base LL | naive LL | actual over-4.5 |
|---|---|---|---|---|---|---|
| 2022/2023 | 306 | 0.6899 | 0.6846 | 0.6961 | 0.6887 | 0.4575 |
| 2023/2024 | 144 | 0.7217 | 0.7164 | 0.7112 | 0.7250 | 0.6181 |
| 2024/2025 | 281 | 0.7006 | 0.6928 | 0.6879 | 0.6937 | 0.4235 |
| **pooled** | **731** | **0.7003** | **0.6940** | **0.6959** | **0.6978** | **0.4761** |

(Actual over-rates and n per season recomputed independently from
the league CSV; they match the runner output exactly.)

## Gate arithmetic (frozen legs)

Dev gate requires pooled dev LL to beat **both** the base-rate
baseline and naive trailing-10. Gate Zero: 0.7003 vs base 0.6959 and
naive 0.6978 — it beats neither. **Gate Zero fails dev ⇒ K-ID FAILS,
the variant is moot, and the virgin season (2025/2026, whose event
feed is complete for all 306 matches) was NOT read**
(`engine/cards/results_virgin.json` records `virgin_read: false`).

The x5 blend (0.6940) does beat both baselines on dev, but the frozen
rule is explicit: a Gate Zero dev failure kills the candidate and
variants are moot. No post-hoc promotion of x5 was made.

Contributing facts, plainly: team yellow traits in this league are
only modestly reliable (split-half r = 0.402 for / 0.338 against,
vs 0.66/0.51 in J1), and the 2023/2024 scored block is the Jul–Oct
2023 complete-feed slice whose actual over-rate is 0.6181 — an
early-season, high-card slice that no trailing state predicts
(Gate Zero calibration that season: −13.46pp, SE 4.14). Pooled dev
calibration for the record: gate_zero −1.93pp (SE 1.86).

Note on the NB size: the harness estimated r = 500 (the cap) for all
three methods on the seed season. This was verified by hand: seed
yellows are *underdispersed* (mean 4.09, variance 3.63), so the
moment denominator is negative (−199.7 for the model method) and the
frozen rule caps r at 500, i.e. the Poisson limit. Not a bug.

**K-ID: FAIL. Virgin unread. Nothing ships.**
