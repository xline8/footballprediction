# Verdict — G-NO (NO-2Divisjon goals): **FAIL (dev gate, OU leg)**

Frozen decision: PREREG_G_NO.md (prereg commit 2901fa0, branch
wip-no-2divisjon, before any fitting). Virgin 2025 was NOT read for
goals: Gate Zero failed the dev gate, so under the frozen mechanical
reading the variant is moot and the verdict is FAIL.

Dev (pooled 2022–2024, n=1,066, season-blocked expanding fit):

| Arm | 1X2 LL | RPS | OU2.5 LL | Dev gate |
|---|---|---|---|---|
| Gate Zero | 1.0046 | 0.2188 | 0.6835 | FAIL (OU leg) |
| SHRINK | 1.0046 | 0.2188 | 0.6835 | moot |
| Climatology | 1.0392 | 0.2332 | **0.6501** | — |
| Naive trailing-10 | 1.1274 | 0.2368 | 0.7052 | — |

Per season (model OU2.5 LL vs climatology): 2022: 0.6775 vs 0.6729;
2023: 0.6842 vs 0.6485; 2024: 0.6882 vs 0.6304 — the OU leg fails in
every dev season, it is not one bad season. Gate Zero passes the 1X2
LL leg (1.0046 < 1.0392 and < 1.1274) and the RPS leg (0.2188 <
0.2332 and < 0.2368) but fails the OU2.5 leg against climatology
(0.6835 > 0.6501). It does beat the naive trailing-10 on OU (0.6835
< 0.7052) — the gate requires beating BOTH baselines, so the arm is
dead. This is the same failure mode as the FI reference itself
(G-FI: Gate Zero OU 0.7231 vs climatology 0.6921, FAIL dev gate OU
leg) — the verbatim reference engine behaves here as it did there.

Diagnosis (recorded, not acted on): the DC fit is strong in-sample
(2021 fit scores 1X2 LL 0.8528 on its own training rows vs
climatology 1.0323) but out-of-sample its implied totals run low:
predicted mean total goals 3.00 / 2.99 / 2.86 vs actual 3.39 / 3.33 /
3.45 per season, predicted OU2.5 over-rate 0.57 / 0.56 / 0.53 vs
actual 0.62 / 0.65 / 0.68. The lambdas are too tightly clustered
and too low for a league averaging ~3.4 goals/match with a 0.65
over-rate; a constant over-rate beats the model's totals in all
three dev seasons. No post-hoc repair was attempted inside this
prereg.

SHRINK is numerically identical to Gate Zero in every season. Under
season-blocked prediction this is mechanical: at each season's fit
every team has either 0 prior in-league matches (entrant; its DC
ratings are the unseen defaults, and multiplying a rating by n/6
changes nothing Gate Zero does not already do) or ≥24 (a full prior
season). No team ever sits in the 1–5 match band the arm targets —
same observation as CH and FI.

Nothing ships for G-NO. No predictions directory is shipped.
