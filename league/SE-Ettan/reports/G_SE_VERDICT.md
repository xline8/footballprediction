# Verdict — G-SE (SE-Ettan goals): **FAIL (dev gate)**

Frozen decision: PREREG_G_SE.md (prereg commit
2fc8d51c13736643f6156b1c71abb11e21b7de08, before any fitting).
Virgin 2025 was NOT read for goals: Gate Zero failed the dev gate,
so under the frozen mechanical reading the variant is moot and the
verdict is FAIL. No virgin numbers exist anywhere in this league
folder (no `results_virgin.json`, no `fitted_params_virgin.json`, no
virgin predictions), and 2026 was not touched.

Dev (pooled 2022–2024, n = 1,440, season-blocked expanding fit,
warm-up 2021 partial, 262 played matches):

| Arm | 1X2 LL | RPS | OU2.5 LL | Dev gate |
|---|---|---|---|---|
| Gate Zero | 1.0625 | 0.2354 | 0.7126 | FAIL |
| SHRINK | 1.0625 | 0.2354 | 0.7126 | FAIL (moot) |
| Climatology | 1.0596 | 0.2380 | 0.6834 | — |
| Naive trailing-10 | 1.1268 | 0.2333 | 0.7426 | — |

Per season, Gate Zero 1X2 LL / RPS / OU2.5 LL: 2022 1.1002 / 0.2447 /
0.7219; 2023 1.0233 / 0.2316 / 0.7160; 2024 1.0640 / 0.2300 / 0.6998.
Climatology per season: 2022 1.0643 / 0.2377 / 0.6882; 2023 1.0397 /
0.2416 / 0.6889; 2024 1.0747 / 0.2346 / 0.6732. Naive trailing-10 per
season: 2022 1.0267 / 0.2204 / 0.7387; 2023 1.1550 / 0.2378 / 0.7136;
2024 1.1988 / 0.2417 / 0.7756. SHRINK is identical to Gate Zero in
every season (see below).

Dev gate, leg by leg (pooled; an arm must beat BOTH baselines on all
three metrics — 6 legs):

- 1X2 LL vs climatology: LOSE — 1.0625 vs 1.0596 (+0.0029).
- 1X2 LL vs naive trailing-10: WIN — 1.0625 vs 1.1268.
- RPS vs climatology: WIN — 0.2354 vs 0.2380.
- RPS vs naive trailing-10: LOSE — 0.2354 vs 0.2333 (+0.0021).
- OU2.5 LL vs climatology: LOSE — 0.7126 vs 0.6834 (+0.0291).
- OU2.5 LL vs naive trailing-10: WIN — 0.7126 vs 0.7426.

Gate Zero passes 3 of 6 legs, so the dev gate fails. Per-season the
pattern is uneven: 2022 passes 1/6 legs (only OU2.5 vs naive), 2023
passes 4/6 (1X2 and RPS vs both baselines; OU2.5 loses to both), 2024
passes 5/6 (1X2 and RPS vs both, OU2.5 vs naive; OU2.5 loses to
climatology). The OU2.5 leg is the persistent failure: Gate Zero loses
OU2.5 LL to climatology in all three dev seasons (2022 0.7219 vs
0.6882; 2023 0.7160 vs 0.6889; 2024 0.6998 vs 0.6732).

SHRINK is numerically identical to Gate Zero pooled and per season
(1.0625 / 0.2354 / 0.7126 in every window). Verified cause: no team
had 1–5 prior in-league matches in any scored season's training data
— every team entering a scored season either had n = 0 prior matches
(pure entrant, already at the league-mean fallback in both arms) or
n ≥ 9 (2022) / ≥ 14 (2023, 2024), so the n/6 scaling never bit on a
fitted rating; a synthetic test proved the SHRINK scaling itself is
active. SHRINK's leg (iii) sign check (SHRINK 1X2 LL ≤ Gate Zero in
3 of 3 dev seasons, by equality) is recorded but moot: Gate Zero
failed its dev gate, so under the frozen mechanical reading the
variant is moot and nothing proceeds to virgin.

Virgin legs (i)–(iii): NOT APPLICABLE / NOT READ. No arm passed the
dev gate, so virgin 2025 was never read, no virgin LL or calibration
numbers exist, and leg (iii) for SHRINK is moot as above. 2026 was
not touched (confirmatory reserve).

Diagnosis (measured facts, recorded not acted on): the DC score
matrix systematically under-predicts total goals in this league —
mean predicted OU2.5 over-rate 0.5065 vs actual 0.5833 pooled (per
season 0.5013 vs 0.5854 in 2022, 0.5043 vs 0.5646 in 2023, 0.5138 vs
0.6000 in 2024), computed from `engine/goals/results_dev.csv`. That
shortfall is the OU2.5 LL gap: a constant 0.5833 over-rate
(climatology) beats the model's per-match total-goals distribution
on log-likelihood. The model also over-predicts home wins — mean
predicted home-win probability 0.4906 vs actual home-win rate 0.4313
pooled — while the fitted home intercept falls season by season
(0.4822 in the 2022 fit, 0.3506 in 2023, 0.3321 in 2024; rho 0.0 in
all three fits). Hypothesis (marked as hypothesis, not established):
with a single home intercept and no group term, the fitted lambdas
compress the total-goals level toward the league mean while
over-weighting the home side, so the score matrix is simultaneously
too home-heavy and too low-scoring; the naive trailing-10 baseline,
which uses each team's actual trailing scoring means as its lambdas,
wins RPS outright and loses only on 1X2 LL to the model. No post-hoc
repair was attempted inside this prereg. Nothing ships for G-SE.
