# Pre-registration — G-KR2 (K League 2 goals)

Frozen 2026-11-10 before any fitting. Reference: production
Dixon-Coles pattern (the production xG blend has no xG in this
league — `expected_goals` appears in 0 of 1,407 matches — so Gate
Zero is goals-only by construction, not by choice).

Population: regular season only; the 2 intra-K2 play-off rows per
season are excluded (frozen phase rule; cross-tier ties are not in
this feed). Dev: seed 2021 (180), scored 2022–2024 (688). Virgin:
complete 2025 (273), read ONCE and only for dev-passing arms.
Confirmatory 2026 is in progress and reserved, unread. Primary line
OU 2.5; scored-dev over-rate 0.494.

Arms:
- Gate Zero: unmodified DC (rho grid {0, −0.05, −0.10, −0.15},
  half-life 270 days, 14 IPF iterations, prior 0.25), fit per target
  season on all earlier regular matches.
- SHRINK: Gate Zero, then attack/defence log-ratings of teams with
  <6 prior K2 matches scaled by count/6.
- X2 mover offset: teams whose immediately preceding season was in
  K League 1 (team-ID match against the KR-KLeague1 corpus
  `league/KR-KLeague1/data/kr_matches.csv`) AND with no K2 matches
  before the target season get log-rating offsets
  log(att_rel) / log(def_rel), where att_rel = (GF + 10·μ_K1) /
  ((n + 10)·μ_K1) from that team's prior K1 season (GF = goals for,
  n = its K1 matches, μ_K1 = K1 league goals per team-match that
  season), def_rel likewise with goals against. Movers in scope:
  2022 Gwangju FC; 2023 Gimcheon Sangmu, Seongnam FC; 2024 Suwon
  Samsung Bluewings; 2025 (virgin) Incheon United. K3 entrants get
  no offset (no corpus).

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
ties prefer Gate Zero, then SHRINK, then X2. On PASS the winning
arm's fitted params and its virgin per-match predictions ship.
