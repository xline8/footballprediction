# Verdict — G-SG (SG-PremierLeague goals): **FAIL (dev gate, OU leg vs climatology)**

Frozen decision: PREREG_G_SG.md (prereg commit 9b5d46b, branch
wip-sg-premierleague, before any fitting). Virgin 2025/2026 was
NOT read for goals: Gate Zero failed the dev gate, so under the
frozen mechanical reading the variants are moot and the verdict
is FAIL.

Dev (pooled 2022 + 2023 + 2024/2025, n=364, season-blocked
expanding fit):

| Arm | 1X2 LL | RPS | OU2.5 LL | Dev gate |
|---|---|---|---|---|
| Gate Zero | 0.9607 | 0.2056 | 0.5507 | FAIL (OU leg vs climatology) |
| SHRINK | 0.9607 | 0.2056 | 0.5507 | moot |
| Climatology | 1.0521 | 0.2421 | **0.5338** | — |
| Naive trailing-10 | 0.9633 | 0.2080 | 0.5783 | — |

Per season (model vs climatology vs naive, 1X2 LL / RPS /
OU2.5 LL):
2022: model 0.9450 / 0.1954 / 0.5546, climatology 1.0589 /
0.2387 / 0.5428, naive 0.9773 / 0.2046 / 0.5636.
2023: model 0.7972 / 0.1726 / 0.5548, climatology 1.0157 /
0.2509 / 0.5412, naive 0.8513 / 0.1915 / 0.6086.
2024/2025: model 1.0954 / 0.2383 / 0.5446, climatology 1.0740 /
0.2383 / 0.5213, naive 1.0365 / 0.2231 / 0.5671.
The model beats BOTH baselines on pooled 1X2 LL and RPS — the
fitted ratings carry real outcome signal in this league — but
the gate requires beating BOTH baselines on ALL THREE legs,
and the model loses the OU2.5 leg to climatology pooled
(0.5507 vs 0.5338) and in every dev season (0.5546 vs 0.5428;
0.5548 vs 0.5412; 0.5446 vs 0.5213). It also has a weak third
season: in 2024/2025 it loses 1X2 LL to both baselines. The
arm is dead.

Diagnosis (recorded, not acted on): in the highest-scoring
league in the program (dev scored OU2.5 over-rate 0.7747), the
climatology baseline's constant over-probability — the pooled
training over-rate — is an unusually strong OU benchmark, and
the Dixon-Coles fitted totals price the over worse than that
constant in all three dev seasons: the model's match-level
total-goals dispersion loses more log-loss than its level
tracking gains. The 1X2/RPS legs show the ratings themselves
are informative (pooled wins over both baselines, and large
wins in 2022–2023); the failure is specific to totals pricing,
the same leg that killed G-BY, G-NO, G-UY and G-CN. No post-hoc
repair was attempted inside this prereg.

SHRINK is numerically identical to Gate Zero in every season.
Under season-blocked prediction this is mechanical: at each
season's fit every team has either 0 prior in-league matches
(entrant; its DC ratings are the unseen defaults, and
multiplying a rating by n/6 changes nothing Gate Zero does not
already do) or ≥21 (a full prior season). No team ever sits in
the 1–5 match band the arm targets — same observation as CH,
FI, NO, FR and BY.

Nothing ships for G-SG. No predictions directory is shipped.
