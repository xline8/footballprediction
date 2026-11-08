# Pre-registration — G-KR3 (K League 3 goals)

Frozen 2026-11-10 before any fitting. Reference: production
Dixon-Coles pattern (the production xG blend has no xG in this
league — `expected_goals` appears in 0 of 1,296 payloads — so Gate
Zero is goals-only by construction, not by choice).

Population: regular season only; the 4 intra-K3 play-off rows of 2021
are excluded (frozen phase rule; cross-tier ties are not in this
feed). The 8 unplayed 2021 index fixtures (placeholder 0-0 scores,
started=False) are excluded before any population is formed. Dev:
seed 2021 (202), scored 2022–2024 (690). Virgin: complete 2025 (210),
read ONCE and only for dev-passing arms. Confirmatory 2026 is in
progress and reserved, unread. Primary line OU 2.5; scored-dev
over-rate 0.4536.

Arms:
- Gate Zero: unmodified DC (rho grid {0, −0.05, −0.10, −0.15},
  half-life 270 days, 14 IPF iterations, prior 0.25), fit per target
  season on all earlier regular matches.
- SHRINK: Gate Zero, then attack/defence log-ratings of teams with
  <6 prior K3 matches scaled by count/6.
- NO X2 arm: zero teams moved K League 2 -> K League 3 in any season
  2022–2026 (verified against the K2 index, league_id 9116), so no
  mover offset is estimable. K4 entrants have no corpus.

Baselines: expanding climatology (prior-seasons 1X2 rates and OU 2.5
over-rate).

Dev gate (all legs required): Gate Zero pooled 1X2 LL < climatology
pooled 1X2 LL AND Gate Zero pooled RPS < climatology RPS AND Gate
Zero pooled OU 2.5 LL < climatology OU LL. Variant arms must also
beat climatology on all three pooled legs AND pass the per-season
sign check (variant pooled-season 1X2 LL ≤ Gate Zero's in at least
2 of the 3 scored dev seasons). If Gate Zero fails dev, the
candidate FAILS and the virgin is NOT read for any arm.

Virgin gate (per arm): 1X2 LL ≤ Gate Zero virgin 1X2 LL AND ≤
climatology virgin 1X2 LL; calibration on home-win rate and on OU
2.5 over-rate: |mean predicted − actual| ≤ 1 pp clean PASS, ≤ 1 pp +
1 SE PROVISIONAL PASS, else FAIL (the worse of the two calibration
legs classifies the arm). Both-pass selection: lowest virgin 1X2 LL;
ties prefer Gate Zero, then SHRINK. On PASS the winning arm's fitted
params and its virgin per-match predictions ship. Halves presentation
uses this league's frozen goals 1H share 0.4273 (config.yaml).
