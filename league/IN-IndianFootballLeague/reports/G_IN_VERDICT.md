# Verdict — G-IN (IN-IndianFootballLeague goals): **FAIL (dev gate)**

Frozen decision: PREREG_G_IN.md (prereg commit 83d1b1f, branch
wip-in-indianfootballleague, before any fitting). Virgin 2025/2026
was NOT read for goals: Gate Zero failed the dev gate, so under the
frozen mechanical reading the variant is moot and the verdict is
FAIL.

Dev (pooled 2022/2023–2024/2025, n=418, season-blocked expanding fit):

| Arm | 1X2 LL | RPS | OU2.5 LL | Dev gate |
|---|---|---|---|---|
| Gate Zero | 1.0861 | 0.2337 | 0.7568 | FAIL (1X2 vs climatology; RPS vs naive; OU vs both) |
| SHRINK | 1.0861 | 0.2337 | 0.7568 | moot |
| Climatology | **1.0813** | 0.2365 | **0.6903** | — |
| Naive trailing-10 | 1.1344 | **0.2320** | 0.7399 | — |

Per season (model vs climatology vs naive, 1X2 LL / RPS / OU2.5 LL):
2022/2023: model 1.1263 / 0.2451 / 0.8303, climatology 1.0841 /
0.2421 / 0.6948, naive 1.0383 / 0.2255 / 0.7558 — the model is worst
on all three legs against both baselines. 2023/2024: model 1.0400 /
0.2224 / 0.7638, climatology 1.0789 / 0.2377 / 0.6931, naive 1.0610 /
0.2284 / 0.7726 — the model wins 1X2 and RPS against both, but loses
OU to climatology. 2024/2025: model 1.0996 / 0.2355 / 0.6752,
climatology 1.0811 / 0.2295 / 0.6826, naive 1.3162 / 0.2428 / 0.6859
— the model wins OU against both but loses 1X2 and RPS to
climatology. Pooled, the model passes only 2 of the 6 gate legs
(RPS vs climatology; 1X2 LL vs naive). The gate requires beating
BOTH baselines on ALL THREE legs. The arm is dead.

Diagnosis (recorded, not acted on): the pre-registered calibration
risk materialised. The goals level ROSE across the dev era (2.579
warm-up → 2.727 → 3.331 → 3.182), and the expanding fit, trained
first on the low-scoring warm-up, badly mispriced totals in the
first scored season (OU2.5 LL 0.8303 vs climatology 0.6948 in
2022/2023) and never recovered the pooled OU leg; by the final dev
season the fit had caught up (OU won outright in 2024/2025), but
the gate is pooled and frozen. Team-trait signal is only moderate
in this league (split-half r 0.608 / 0.462, weak-to-moderate
season-to-season correlations, heavy promotion/relegation churn),
and the naive trailing-10 beat the fitted model outright in
2022/2023 on all three legs. No post-hoc repair was attempted
inside this prereg.

SHRINK is numerically identical to Gate Zero in every season. Under
season-blocked prediction this is mechanical: at each season's fit
every team has either 0 prior in-league matches (entrant; its DC
ratings are the unseen defaults, and multiplying a rating by n/6
changes nothing Gate Zero does not already do) or ≥22 (a full prior
season). No team ever sits in the 1–5 match band the arm targets —
same observation as CH, FI, NO, FR and BY.

X2 was not run: the entrant offset was dropped pre-fitting on the
frozen EDA F4 evidence (6 dev transitions, mean GF −0.110 / GA
+0.025, signs mixed) — see PREREG_G_IN.md.

Nothing ships for G-IN. No predictions directory is shipped.
Virgin 2025/2026 NOT read; 2026/2027 untouched.
