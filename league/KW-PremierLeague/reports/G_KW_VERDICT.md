# Verdict — G-KW (KW-PremierLeague goals): **FAIL (dev gate, OU leg vs climatology)**

Frozen decision: PREREG_G_KW.md (prereg commit c8988cf, branch
wip-kw-premierleague, before any fitting). Virgin 2025/2026 was NOT
read for goals: Gate Zero failed the dev gate, so under the frozen
mechanical reading the variants are moot and the verdict is FAIL.

Dev (pooled 2021/2022–2024/2025, n=422, season-blocked expanding fit):

| Arm | 1X2 LL | RPS | OU2.5 LL | Dev gate |
|---|---|---|---|---|
| Gate Zero | 0.9436 | 0.1882 | 0.7293 | FAIL (OU leg vs climatology only) |
| SHRINK | 0.9436 | 0.1882 | 0.7293 | moot |
| X2 | 0.9496 | 0.1899 | 0.7371 | moot |
| Climatology | 1.0767 | 0.2357 | **0.6806** | — |
| Naive trailing-10 | 1.0108 | 0.2086 | 0.7405 | — |

Gate Zero beats BOTH baselines on pooled 1X2 LL (0.9436 vs 1.0767 /
1.0108) and RPS (0.1882 vs 0.2357 / 0.2086), and beats naive on OU —
but the gate requires beating both baselines on all three legs, and
it loses the OU2.5 leg to climatology pooled (0.7293 vs 0.6806).

Per season (model Gate Zero vs climatology vs naive, 1X2 LL / RPS /
OU2.5 LL): 2021/2022: model 1.0354 / 0.2195 / 0.7942, climatology
1.0737 / 0.2408 / 0.6863, naive 1.0237 / 0.2213 / 0.7667. 2022/2023:
model 1.0303 / 0.2088 / 0.7586, climatology 1.0936 / 0.2302 / 0.6633,
naive 1.1025 / 0.2310 / 0.7086. 2023/2024: model 0.9250 / 0.1805 /
0.7283, climatology 1.0763 / 0.2378 / 0.7086, naive 0.9628 / 0.1883 /
0.8044. 2024/2025: model 0.8133 / 0.1551 / 0.6585, climatology
1.0606 / 0.2359 / 0.6648, naive 0.9565 / 0.1989 / 0.6884.

Diagnosis (recorded, not acted on): the fitted Dixon-Coles ratings
carry strong 1X2/RPS signal — they beat both baselines on both legs
pooled and in nearly every season — but the fitted goal totals are
worse-calibrated than the league base rate in the first three dev
seasons (OU LL 0.7942 / 0.7586 / 0.7283 vs climatology 0.6863 /
0.6633 / 0.7086). Only in 2024/2025, the first season with a full
played fixture list (111/111) and the deepest training window, does
the model beat climatology on all three metrics. The early scored
seasons are exactly the ones thinned by unplayed fixtures (69 and
120 of 90/132 played), so the expanding fit prices totals off a
partial record while climatology pools the same record's over-rate
directly. No post-hoc repair was attempted inside this prereg.

X2 (entrant offset, the FI-pattern variant): numerically identical
to Gate Zero in 2021/2022 and 2022/2023 (fewer than 3 completed
entrant transitions before those seasons, so the offset is 0 by the
frozen rule), worse in 2023/2024 (1X2 LL 0.9464 vs 0.9250) and mixed
in 2024/2025 (1X2 LL 0.8126 vs 0.8133 marginally better; RPS and OU
marginally worse). Pooled it is worse than Gate Zero on all three
metrics. Its dev sign check would have passed leg (iii) (X2 ≤ Gate
Zero on 1X2 LL in 3 of 4 dev seasons, two by equality), but the
variant is moot under the frozen mechanical reading.

SHRINK is numerically identical to Gate Zero in every season. Under
season-blocked prediction this is mechanical: every team has either
0 prior in-league matches (entrant; exponents are the unseen
defaults 0.0, and scaling 0.0 by n/6 changes nothing) or ≥14 (a
prior season in this split-phase format) — no team sits in the 1–5
band the arm targets. Same observation as BY.

Nothing ships for G-KW. No predictions directory is shipped.
Re-run reproduces results_dev.json exactly (md5
67e9e6f0ea63509fb13b64cb0f0a8d2e).
