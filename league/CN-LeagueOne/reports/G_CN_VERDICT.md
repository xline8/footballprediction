# Verdict — G-CN (CN-LeagueOne goals): **FAIL (dev gate, OU leg)**

Frozen decision: PREREG_G_CN.md (prereg commit 05c5870, branch
wip-cn-leagueone, before any fitting). Virgin 2025 was NOT read for
goals: Gate Zero failed the dev gate, so under the frozen mechanical
reading the variant is moot and the verdict is FAIL.

Dev (pooled 2022–2024, n=786, season-blocked expanding fit):

| Arm | 1X2 LL | RPS | OU2.5 LL | Dev gate |
|---|---|---|---|---|
| Gate Zero | 1.0286 | 0.2096 | 0.6927 | FAIL (OU leg) |
| SHRINK | 1.0286 | 0.2096 | 0.6927 | moot |
| Climatology | 1.0886 | 0.2293 | **0.6919** | — |
| Naive trailing-10 | 1.1995 | 0.2128 | 0.7680 | — |

Per season (model OU2.5 LL vs climatology): 2022: 0.6880 vs 0.6931
(model wins); 2023: 0.6946 vs 0.6956 (model wins, by 0.0010);
2024: 0.6968 vs 0.6869 (model loses) — the pooled OU leg fails by
0.0007 (0.6927 vs 0.6919), carried by the single 2024 season. Gate
Zero passes the 1X2 LL leg (1.0286 < 1.0886 and < 1.1995) and the
RPS leg (0.2096 < 0.2293 and < 0.2128) but fails the OU2.5 leg
against climatology (0.6927 > 0.6919). It does beat the naive
trailing-10 on OU (0.6927 < 0.7680) — the gate requires beating
BOTH baselines, so the arm is dead. This is the same failure mode
as the FI reference itself (G-FI: Gate Zero OU 0.7231 vs
climatology 0.6921, FAIL dev gate OU leg) and as NO (0.6835 vs
0.6501) — the verbatim reference engine behaves here as it did
there, only closer: the narrowest dev-gate OU miss in the program
so far.

Diagnosis (recorded, not acted on): the fitted mean team goals mu
falls as the training window expands (1.362 / 1.328 / 1.219 for the
2022 / 2023 / 2024 fits) and the model's implied totals run low in
two of three dev seasons: predicted mean total goals 2.35 / 2.25 /
2.32 vs actual 2.61 / 2.26 / 2.48 per season; predicted OU2.5
over-rate 0.415 / 0.390 / 0.407 vs actual 0.507 / 0.379 / 0.433.
2023 is fitted almost exactly (2.25 vs 2.26) and the model wins
its OU leg there; 2022 and 2024 are under-predicted, and 2024's
miss is what sinks the pooled leg. A constant over-rate beats the
model's totals in the pooled window by the thinnest margin the
program has seen. No post-hoc repair was attempted inside this
prereg — the gate is frozen, and a 0.0007 miss is still a miss.

SHRINK is numerically identical to Gate Zero in every season. Under
season-blocked prediction this is mechanical: at each season's fit
every team has either 0 prior in-league matches (entrant; its DC
ratings are the unseen defaults, and multiplying a rating by n/6
changes nothing Gate Zero does not already do) or ≥30 (a full prior
season). No team ever sits in the 1–5 match band the arm targets —
same observation as CH, FI and NO.

Nothing ships for G-CN. No predictions directory is shipped.
