# Step 6 — Model Design: CH-ChallengeLeague

Feasibility matrix: goals — target exists all seasons; SOT / corners /
total shots / yellows — targets exist in the stats era (2023/2024+) and
in the virgin (181/181). **All five candidates are buildable.** Total
shots is NOT FI's case: within CH's single rich stats era its level is
consistent (25.61 / 25.30 per match in the two dev stats seasons), so
T-CH is built with stats-era windows. Cards runs on stats yellows
because the event feed carries almost no cards in this league
(Step 1 / EDA F5) — a feed-forced divergence from FI, recorded here
and in PREREG_K_CH before any fitting.

Windows frozen for every built candidate: virgin = **2025/2026**
(complete, 181 matches — read ONCE per candidate, only for dev-passing
arms). 2026/2027 (in progress, 65) is untouched. Implementation
divergence from the FI production references, recorded pre-fitting:
the production engines are not runnable in this bundle, so each CH
engine is a minimal, documented port of the reference *pattern*
(Dixon-Coles for goals; trait-rate + Negative Binomial for counts),
written in numpy/scipy (no sklearn exists in this environment).
Constants not carried over are listed in each prereg.

| Candidate | Gate Zero pattern | Variant arms | Warm-up | Dev scored | Primary line |
|---|---|---|---|---|---|
| G-CH goals | Dixon-Coles Poisson (goals-only, X1 fallback): attack/defence ratings + home advantage fitted by Poisson likelihood (L-BFGS, sum-to-zero), rho from grid (0, −0.05, −0.10, −0.15) by fit log-likelihood, score matrix to 10 goals | SHRINK (n<6 prior in-league matches ⇒ attack/defence exponents scaled by n/6 at prediction) | 2021/2022 | 2022/2023–2024/2025 (n=540), season-blocked expanding fit | 1X2 LL/RPS + OU 2.5 |
| S-CH SOT | Trait-rate NB: decay-weighted (HL 365d) team SOT for/against rates, prior K=8 shrinkage to league mean; μ = λ_home + λ_away with λ_team = for-rate × opp-against-rate / league-side-mean; NB size r fitted on dev scored rows (grid, max NB loglik) | — none | 2023/2024 | 2024/2025 (n=180), per-match WF | 8.5 |
| C-CH corners | Same trait-rate NB pattern on corners | — none | 2023/2024 | 2024/2025 (n=180), per-match WF | 8.5 |
| K-CH cards | Same trait-rate NB pattern on stats yellows | — none (X8 data absent) | 2023/2024 | 2024/2025 (n=180), per-match WF | 4.5 |
| T-CH total shots | Same trait-rate NB pattern on total shots | — none | 2023/2024 | 2024/2025 (n=180), per-match WF | 26.5 |

Gate legs (identical program-wide, frozen verbatim in each prereg):
dev gate — pooled dev LL at the primary line (goals: 1X2 LL, RPS and
OU LL legs) beats BOTH baselines (league base rate / climatology;
naive trailing-10), else the arm is dead and the virgin is NOT read
for it; if Gate Zero fails dev, variants are moot, verdict FAIL.
Virgin legs — (i) LL ≤ Gate Zero's and ≤ best baseline's; (ii)
calibration |mean predicted − actual| ≤ 1.0pp clean PASS, breach
within 1 SE of the boundary = PROVISIONAL PASS, beyond = FAIL;
(iii) variant sign check: variant dev LL ≤ Gate Zero's in at least
half the dev seasons (goals only; count candidates are single-arm so
(iii) is vacuous). Both-pass: lower pooled virgin LL ships; ties →
simpler arm. Gates never move after a result is seen; FAIL is a
valid outcome.

Halves presentation via the frozen constants in FEATURES.md.
Predictions-only: no CH odds/settlement source in-system.
