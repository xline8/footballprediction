# Pre-registration — K-KR2 (K League 2 cards)

Frozen 2026-11-10 before any fitting. Reference pattern: production
cards family (Poisson team attack/defence ratings + Negative
Binomial totals).

TARGET FREEZE (with reason): the target is STATS-feed yellows
(`yellow_cards_home + yellow_cards_away`). An event-unified target
is impossible in this league: the FotMob event feed contains ZERO
plain Yellow card events in 2022, 2023, 2024 and 2025 (only Red /
YellowRed events are carried; corpus totals of event-feed plain
yellows: 2021: 650, 2022–2025: 0 each, 2026: 964). The population is
2023–2025 only: 2021 has no stats block at all, and the 2022 stats
yellows are an artefact era (69.4% of matches record zero yellows;
monthly means 0.6–1.4 until Oct 2022 vs 2.93 in 2023).

Population: regular season only; matches with the target present.
Dev: seed 2023 (232 with target), scored 2024 (229). Virgin:
complete 2025 (273, target-complete), read ONCE and only if Gate
Zero passes dev. 2026 reserved, unread. Primary line OU 2.5
(scored-dev over-rate 0.620 — the mechanical closest-to-0.50 pick:
OU 3.5 is 0.371, distance 0.129 > 0.120). Secondary lines 3.5 / 4.5
reported.

Arms:
- Gate Zero (the only arm): season-blocked Poisson ratings on stats
  yellows (IPF, half-life 270 days at the season-start cutoff, prior
  0.25), expected total λh + λa, NB over-probabilities with r = the
  frozen moment estimate on the training window (r = Σμ² /
  Σ((y−μ)²−μ), capped [2, 500]).
- No X8 referee arm: referee identity covers only 400 of 1,397
  regular matches and just 3 referees reach ≥20 matches corpus-wide
  (2 in the stats era); strictness reliability is inestimable
  (FEATURES.md). No variant arm is registered for this candidate.

Baselines: league base rate (prior-seasons over-rate at the line)
and naive trailing-10 (team last-10 for/against means before the
season, combined (own_for + opp_against)/2 per side).

Dev gate: Gate Zero passes dev iff its pooled LL at 2.5 beats BOTH
baselines' pooled LL at 2.5 (the scored window is the single season
2024, so no per-season sign check applies). If Gate Zero fails dev,
the candidate FAILS and the virgin is NOT read.

Virgin gate: LL at 2.5 ≤ the better virgin baseline LL (Gate Zero
is the only arm, so the Gate-Zero-comparison leg is vacuous);
calibration |mean predicted over-rate − actual over-rate| ≤ 1 pp
clean PASS, ≤ 1 pp + 1 SE PROVISIONAL PASS, else FAIL. On PASS the
fitted params and virgin per-match predictions ship, with halves
presentation via this league's frozen cards 1H share 0.330.
