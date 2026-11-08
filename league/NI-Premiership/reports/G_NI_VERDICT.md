# Verdict — G-NI (NI-Premiership goals): **FAIL (dev gate)**

Frozen decision: PREREG_G_NI.md (prereg commit 0fb5a643, before any
fitting). Virgin 2025/26 was NOT read for goals: Gate Zero failed
the dev gate, so under the frozen mechanical reading the variant is
moot and the verdict is FAIL. No virgin numbers exist anywhere in
this league folder (no `results_virgin.json`, no
`fitted_params_virgin.json`, no virgin predictions), and 2026/27 was
not touched.

Dev (pooled 2022/23–2024/25, n = 684 regular matches, season-blocked
expanding fit, warm-up 2021/22 complete, 228 played regular
matches):

| Arm | 1X2 LL | RPS | OU2.5 LL | Dev gate |
|---|---|---|---|---|
| Gate Zero | 0.9830 | 0.2102 | 0.7047 | FAIL |
| SHRINK | 0.9830 | 0.2102 | 0.7047 | FAIL (moot) |
| Climatology | 1.0431 | 0.2406 | 0.6915 | — |
| Naive trailing-10 | 1.0164 | 0.2248 | 0.7447 | — |

Per season, Gate Zero 1X2 LL / RPS / OU2.5 LL: 2022/23 0.8758 /
0.1838 / 0.7120; 2023/24 0.9475 / 0.2013 / 0.6834; 2024/25 1.1257 /
0.2455 / 0.7186. Climatology per season: 2022/23 1.0256 / 0.2393 /
0.6886; 2023/24 1.0437 / 0.2453 / 0.6798; 2024/25 1.0600 / 0.2373 /
0.7062. Naive trailing-10 per season: 2022/23 1.0015 / 0.2205 /
0.7541; 2023/24 0.9649 / 0.2103 / 0.7200; 2024/25 1.0828 / 0.2437 /
0.7600. SHRINK is identical to Gate Zero in every season (see
below). Fitted home intercept / rho per season: 2022/23 0.2375 /
0.00; 2023/24 0.3125 / 0.00; 2024/25 0.3279 / 0.00.

Dev gate, leg by leg (pooled; an arm must beat BOTH baselines on all
three metrics — 6 legs):

- 1X2 LL vs climatology: WIN — 0.9830 vs 1.0431.
- 1X2 LL vs naive trailing-10: WIN — 0.9830 vs 1.0164.
- RPS vs climatology: WIN — 0.2102 vs 0.2406.
- RPS vs naive trailing-10: WIN — 0.2102 vs 0.2248.
- OU2.5 LL vs climatology: LOSE — 0.7047 vs 0.6915 (+0.0132).
- OU2.5 LL vs naive trailing-10: WIN — 0.7047 vs 0.7447.

Gate Zero passes 5 of 6 legs, so the dev gate fails. Per-season the
pattern is uneven: 2022/23 passes 5/6 legs (everything except OU2.5
vs climatology, 0.7120 vs 0.6886); 2023/24 passes 5/6 (everything
except OU2.5 vs climatology, 0.6834 vs 0.6798); 2024/25 passes only
1/6 (OU2.5 vs naive only, 0.7186 vs 0.7600 — it loses 1X2 LL and RPS
to BOTH baselines that season, 1.1257 vs 1.0600/1.0828 and 0.2455 vs
0.2373/0.2437). The OU2.5 leg is the
persistent failure: Gate Zero loses OU2.5 LL to climatology in all
three dev seasons (2022/23 0.7120 vs 0.6886; 2023/24 0.6834 vs
0.6798; 2024/25 0.7186 vs 0.7062). The 2024/25 season is the worst
dev season on every metric (1X2 LL 1.1257 — worse than climatology
1.0600 that season).

SHRINK is numerically identical to Gate Zero pooled and per season
(0.9830 / 0.2102 / 0.7047 in every window). Verified cause: no team
had 1–5 prior in-league matches in any scored season's training
data — every team entering a scored season either had n = 0 prior
matches (pure entrant, already at the league-mean fallback in both
arms) or n ≥ 76, so the n/6 scaling never bit on a fitted rating;
a synthetic test proved the SHRINK scaling itself is active (n=3
gives factor 0.5). SHRINK's leg (iii) sign check (SHRINK 1X2 LL ≤
Gate Zero in 3 of 3 dev seasons, by equality) is recorded but moot:
Gate Zero failed its dev gate, so under the frozen mechanical
reading the variant is moot and nothing proceeds to virgin.

Virgin legs (i)–(iii): NOT APPLICABLE / NOT READ. No arm passed the
dev gate, so virgin 2025/26 was never read, no virgin LL or
calibration numbers exist, and leg (iii) for SHRINK is moot as above.
2026/27 was not touched (confirmatory reserve).

Diagnosis (measured facts, recorded not acted on): the DC score
matrix systematically under-predicts total goals in this league —
mean predicted OU2.5 over-rate 0.4952 vs actual 0.5439 pooled (per
season 0.4485 vs 0.5526 in 2022/23, 0.4902 vs 0.6009 in 2023/24,
0.5470 vs 0.4781 in 2024/25 — the shortfall is concentrated in the
first two dev seasons and REVERSES in 2024/25), computed from
`engine/goals/results_dev.csv`. That shortfall is the OU2.5 LL gap:
the constant-rate climatology beats the model's per-match
total-goals distribution on log-likelihood in all three dev
seasons. The model also over-predicts home wins slightly —
mean predicted home-win probability 0.4590 vs actual home-win rate
0.4503 pooled — while the fitted home intercept RISES season by
season (0.2375 in the 2022/23 fit, 0.3125 in 2023/24, 0.3279 in
2024/25; rho 0.0 throughout). The same failure mode killed G-LU and
G-SE (OU2.5 shortfall 0.5373 vs 0.6028 in LU, 0.5065 vs 0.5833 in
SE). Hypothesis (marked as hypothesis, not established): with the
goals level swinging season to season with no trend (2.73 → 2.84 →
3.10 → 2.54) the 270-day decay still leaves the fitted lambdas
compressed toward the training mean while the actual over-rate stays
high in the first two dev seasons, so the score matrix is too
low-scoring in total; the naive trailing-10 baseline, which uses
each team's actual trailing scoring means as its lambdas, beats the
model on OU2.5 LL in no season but loses on 1X2 LL/RPS pooled —
the model's 1X2/RPS edge is real, its totals edge is not. No
post-hoc repair was attempted inside this prereg. Nothing ships for
G-NI.

Independent verification (by the coordinator, not Codex):
- All headline metrics recomputed from `results_dev.csv` with an
  independent script — exact match to 4 decimals, pooled and
  per-season, all four methods.
- Second-path fit with production `model_v2.py` DC (iterative
  updates, same windows): pooled 0.9773 / 0.2096 / 0.6997 — same
  5/6 legs (loses OU2.5 LL to climatology, 0.6997 vs 0.6915; wins
  the other five), same FAIL. The verdict does not depend on the
  optimizer. (Production DC's fitted home intercepts differ —
  0.0899 / 0.2428 / 0.2324 vs the L-BFGS 0.2375 / 0.3125 / 0.3279 —
  the iterative fit under-converges on the first window; the gate
  outcome is identical either way.)
- Naive baseline recomputed independently with date-grouped
  prediction (same-day matches strictly excluded): pooled 1.0164 /
  0.2248 / 0.7447 — identical to the engine's to 4 decimals.
- Code review of the engine: bounded trailing-10 deque
  (maxlen=10), dev loader hard-guards (virgin/reserve rows rejected,
  frozen counts 228/684 enforced, playoffs excluded), standard DC
  tau on all four low-score cells, RPS over the first two cumulative
  terms, SHRINK scaling applied to both exponents, renormalised
  score matrix. One cosmetic note (not a defect): the naive arm's
  11×11 matrix is not renormalised after truncation at MAXG = 10,
  so its probabilities sum to 0.9997–1.0000 (mean 0.99999) — the
  largest possible LL effect is ~0.0003 per match, far below every
  leg margin. Clean rerun of `run_g_ni.py` reproduces all three
  output files byte-for-byte (identical SHA-256).
