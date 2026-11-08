# Verdict — G-FI (FI-Ykkonen goals): **FAIL (dev gate)**

Frozen decision: PREREG_G_FI.md (prereg commit
e5874b8d62f005abf9a79e8ee2b5641069cf1f2a, branch wip-fi-ykkonen,
before any fitting). Split: Jarvis OPSI A (board comment
6761468990) — dev ≤ 2024 as-is. Virgin 2025 was NOT read for goals:
Gate Zero failed the dev gate, so under the frozen mechanical
reading the variants are moot and the verdict is FAIL.

Dev (pooled 2022–2024, n=1,010, season-blocked expanding fit):

| Arm | 1X2 LL | RPS | OU2.5 LL | Dev gate |
|---|---|---|---|---|
| Gate Zero | 1.0747 | 0.2437 | 0.7026 | FAIL (all three legs vs climatology) |
| SHRINK | 1.0747 | 0.2437 | 0.7026 | moot |
| X2 | 1.0660 | 0.2404 | 0.6940 | moot (fails dev gate too) |
| Climatology | 1.0420 | 0.2355 | **0.6485** | — |
| Naive trailing-10 | 1.1023 | 0.2288 | 0.7208 | — |

Per season (model OU2.5 LL vs climatology): 2022: 0.7359 vs 0.6493;
2023: 0.6784 vs 0.6609; 2024: 0.6739 vs 0.6148 — the OU leg fails in
every dev season, it is not one bad season. Gate Zero fails the 1X2
LL leg against climatology (1.0747 > 1.0420, though it beats naive
1.1023), fails the RPS leg against BOTH baselines (0.2437 > 0.2355
and > 0.2288), and fails the OU2.5 leg against climatology (0.7026
> 0.6485, though it beats naive 0.7208). The gate requires beating
BOTH baselines on all three metrics, so the arm is dead. This is
the same failure mode as the FI-Veikkausliiga reference league
itself (its goals candidate, also labelled G-FI there: Gate Zero OU
0.7231 vs climatology 0.6921, FAIL dev gate OU leg) — the verbatim
reference engine behaves here as it did there.

Diagnosis (recorded, not acted on): the DC fit's implied totals run
far too low out-of-sample: predicted mean total goals 2.68 / 2.99 /
2.85 vs actual 3.43 / 3.33 / 3.51 per dev season, predicted OU2.5
over-rate 0.491 / 0.558 / 0.532 vs actual 0.648 / 0.627 / 0.710.
The lambdas are too tightly clustered and too low for a league
averaging ~3.4 goals/match with a 0.65 over-rate; a constant
over-rate beats the model's totals in all three dev seasons. The
fitted rho is 0.0 in all three seasons and the home exponent
0.19–0.24. No post-hoc repair was attempted inside this prereg.

SHRINK is numerically identical to Gate Zero in every season. Under
season-blocked prediction this is mechanical: at each season's fit
every team has either 0 prior in-league matches (entrant; its DC
ratings are the unseen defaults, and multiplying a rating by n/6
changes nothing Gate Zero does not already do) or ≥22 (a full prior
season). No team ever sits in the 1–5 match band the arm targets —
same observation as CH/NO.

X2 improves on Gate Zero pooled on all three metrics (1.0660 /
0.2404 / 0.6940 vs 1.0747 / 0.2437 / 0.7026) and beats Gate Zero's
1X2 LL in 2 of 3 dev seasons (2022: 1.0674 vs 1.0785; 2023: 1.0458
vs 1.0693; 2024: 1.1132 vs 1.0781 — the sign check would have been
2/3), but it still fails the dev gate itself: it loses to
climatology on all three metrics and to naive trailing-10 on RPS
(0.2404 > 0.2288). The entrant offset helps where Kakkonen churn is
heavy (11 entrants in 2022, 9 in 2023) and hurts in 2024, where only
2 entrants (JJK, KPV) carry a Kakkonen-measured offset into the
single-table Ykkönen season. Since Gate Zero failed dev, X2 is moot
under the frozen mechanical reading regardless.

Nothing ships for G-FI. No predictions directory is shipped. The
virgin (2025) was never read; 2026 untouched.
