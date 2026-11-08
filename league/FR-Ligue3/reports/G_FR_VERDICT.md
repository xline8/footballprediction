# Verdict — G-FR (FR-Ligue3 goals): **FAIL (dev gate, all three legs vs climatology)**

Frozen decision: PREREG_G_FR.md (prereg commit ef482d7, branch
wip-fr-ligue3, before any fitting). Virgin 2025/2026 was NOT read for
goals: Gate Zero failed the dev gate, so under the frozen mechanical
reading the variant is moot and the verdict is FAIL.

Dev (pooled 2022/2023–2024/2025, n=884, season-blocked expanding fit):

| Arm | 1X2 LL | RPS | OU2.5 LL | Dev gate |
|---|---|---|---|---|
| Gate Zero | 1.0923 | 0.2266 | 0.6994 | FAIL (all three legs vs climatology) |
| SHRINK | 1.0923 | 0.2266 | 0.6994 | moot |
| Climatology | **1.0869** | **0.2243** | **0.6864** | — |
| Naive trailing-10 | 1.2729 | 0.2390 | 0.7308 | — |

Per season (model vs climatology): 2022/2023: 1X2 1.1041 vs 1.1010,
RPS 0.2268 vs 0.2251, OU 0.7073 vs 0.6884; 2023/2024: 1X2 1.0600 vs
1.0715, RPS 0.2227 vs 0.2264, OU 0.7016 vs 0.6901; 2024/2025: 1X2
1.1153 vs 1.0883, RPS 0.2308 vs 0.2210, OU 0.6881 vs 0.6801. The
model beats climatology only in 2023/2024 and only on 1X2 LL and
RPS; it loses the OU leg in every dev season and loses the pooled
1X2 LL and RPS legs as well. It does beat the naive trailing-10 on
all three pooled legs — the gate requires beating BOTH baselines,
so the arm is dead.

Diagnosis (recorded, not acted on): in a low-scoring league
(2.48 goals/match dev scored, OU2.5 over-rate 0.4355) with weak
team-trait reliability (split-half r 0.323 / 0.309, EDA F2), the
fitted Dixon-Coles ratings add no out-of-sample signal over the
pooled outcome rates — the constant climatology beats the model on
every pooled leg. No post-hoc repair was attempted inside this
prereg.

SHRINK is numerically identical to Gate Zero in every season. Under
season-blocked prediction this is mechanical: at each season's fit
every team has either 0 prior in-league matches (entrant; its DC
ratings are the unseen defaults, and multiplying a rating by n/6
changes nothing Gate Zero does not already do) or ≥32 (a full prior
season). No team ever sits in the 1–5 match band the arm targets —
same observation as CH, FI, and NO.

Nothing ships for G-FR. No predictions directory is shipped.
