# Verdict — G-BY (BY-PremierLeague goals): **FAIL (dev gate, OU leg vs climatology + 1X2/RPS legs vs naive)**

Frozen decision: PREREG_G_BY.md (prereg commit 66cbfe4, branch
wip-by-premierleague, before any fitting). Virgin 2025 was NOT read
for goals: Gate Zero failed the dev gate, so under the frozen
mechanical reading the variants are moot and the verdict is FAIL.

Dev (pooled 2022–2024, n=690, season-blocked expanding fit):

| Arm | 1X2 LL | RPS | OU2.5 LL | Dev gate |
|---|---|---|---|---|
| Gate Zero | 1.0679 | 0.2223 | 0.7143 | FAIL (OU leg vs climatology; 1X2 + RPS legs vs naive) |
| SHRINK | 1.0679 | 0.2223 | 0.7143 | moot |
| X2 | 1.0867 | 0.2257 | 0.7200 | moot |
| Climatology | 1.0886 | 0.2327 | **0.6934** | — |
| Naive trailing-10 | **1.0534** | **0.2181** | 0.7455 | — |

Per season (model vs climatology vs naive, 1X2 LL / RPS / OU2.5 LL):
2022: model 1.0852 / 0.2235 / 0.6967, climatology 1.1073 / 0.2315 /
0.6959, naive 1.0586 / 0.2123 / 0.7530. 2023: model 1.0354 / 0.2220 /
0.7306, climatology 1.0682 / 0.2373 / 0.6933, naive 1.0101 / 0.2162 /
0.7323. 2024: model 1.0789 / 0.2212 / 0.7176, climatology 1.0877 /
0.2298 / 0.6910, naive 1.0861 / 0.2255 / 0.7495. The model beats
climatology on pooled 1X2 LL and RPS, and beats naive on pooled OU —
but the gate requires beating BOTH baselines on ALL THREE legs, and
the model loses the OU leg to climatology in every dev season
(0.6967 vs 0.6959 in 2022, 0.7306 vs 0.6933 in 2023, 0.7176 vs 0.6910
in 2024) and loses the pooled 1X2 LL and RPS legs to the naive
trailing-10 (1.0679 vs 1.0534; 0.2223 vs 0.2181). The arm is dead.

Diagnosis (recorded, not acted on): the fitted Dixon-Coles ratings
do carry 1X2/RPS signal over pooled outcome rates (they beat
climatology on both), but they systematically misprice totals — the
model's OU2.5 log-loss is worse than the constant base rate in all
three dev seasons, i.e. the fitted goal totals are worse-calibrated
than the league over-rate. Separately, the naive trailing-10 (no
ratings, no home advantage, just each team's last-10 goals-for mean)
beats the fitted model on 1X2 LL and RPS pooled, driven by 2022 and
2023 — recent-form goals means track this league's outcomes better
than the expanding-fit ratings. No post-hoc repair was attempted
inside this prereg.

X2 (entrant offset, the FI-pattern variant): numerically identical
to Gate Zero in 2022 (fewer than 3 completed entrant transitions
before that season, so the offset is 0 by the frozen rule), slightly
worse in 2023 (1.0366 vs 1.0354) and much worse in 2024 (1.1319 vs
1.0789 on 1X2 LL; OU 0.7360 vs 0.7176). The 2024 entrants
(Arsenal Dzerzhinsk, FK Vitebsk, Dnyapro Mogilev) performed better
than the frozen tilt (attack ×0.8, conceded ×1.25) assumes — the
largest entrant tilt in the programme, adopted on the strongest EDA
evidence, backfired in its first live season. The variant is moot
under the frozen mechanical reading (Gate Zero failed dev), and its
dev sign check would have failed leg (iii) anyway (X2 ≤ Gate Zero on
1X2 LL in only 1 of 3 dev seasons: 2022 by equality).

SHRINK is numerically identical to Gate Zero in every season. Under
season-blocked prediction this is mechanical: at each season's fit
every team has either 0 prior in-league matches (entrant; its DC
ratings are the unseen defaults, and multiplying a rating by n/6
changes nothing Gate Zero does not already do) or ≥28 (a full prior
season). No team ever sits in the 1–5 match band the arm targets —
same observation as CH, FI, NO and FR.

Nothing ships for G-BY. No predictions directory is shipped.
