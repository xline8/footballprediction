# Verdict — G-LU (LU-NationalDivision goals): **FAIL (dev gate)**

Frozen decision: PREREG_G_LU.md (prereg commit
ef84db14, before any fitting). Virgin 2025/26 was NOT read for goals:
Gate Zero failed the dev gate, so under the frozen mechanical reading
the variant is moot and the verdict is FAIL. No virgin numbers exist
anywhere in this league folder (no `results_virgin.json`, no
`fitted_params_virgin.json`, no virgin predictions), and 2026/27 was
not touched.

Dev (pooled 2022/23–2024/25, n = 720, season-blocked expanding fit,
warm-up 2021/22 complete, 240 played matches):

| Arm | 1X2 LL | RPS | OU2.5 LL | Dev gate |
|---|---|---|---|---|
| Gate Zero | 0.9922 | 0.2120 | 0.7063 | FAIL |
| SHRINK | 0.9922 | 0.2120 | 0.7063 | FAIL (moot) |
| Climatology | 1.0547 | 0.2386 | 0.6729 | — |
| Naive trailing-10 | 0.9756 | 0.2073 | 0.7399 | — |

Per season, Gate Zero 1X2 LL / RPS / OU2.5 LL: 2022/23 1.0113 /
0.2229 / 0.7180; 2023/24 0.9982 / 0.2061 / 0.6912; 2024/25 0.9671 /
0.2070 / 0.7096. Climatology per season: 2022/23 1.0397 / 0.2422 /
0.6534; 2023/24 1.0829 / 0.2343 / 0.6773; 2024/25 1.0413 / 0.2393 /
0.6880. Naive trailing-10 per season: 2022/23 0.9108 / 0.1929 /
0.6798; 2023/24 1.0483 / 0.2237 / 0.7668; 2024/25 0.9676 / 0.2052 /
0.7730. SHRINK is identical to Gate Zero in every season (see below).
Fitted home intercept / rho per season: 2022/23 0.3189 / −0.05;
2023/24 0.2457 / 0.00; 2024/25 0.2008 / 0.00.

Dev gate, leg by leg (pooled; an arm must beat BOTH baselines on all
three metrics — 6 legs):

- 1X2 LL vs climatology: WIN — 0.9922 vs 1.0547.
- 1X2 LL vs naive trailing-10: LOSE — 0.9922 vs 0.9756 (+0.0166).
- RPS vs climatology: WIN — 0.2120 vs 0.2386.
- RPS vs naive trailing-10: LOSE — 0.2120 vs 0.2073 (+0.0047).
- OU2.5 LL vs climatology: LOSE — 0.7063 vs 0.6729 (+0.0334).
- OU2.5 LL vs naive trailing-10: WIN — 0.7063 vs 0.7399.

Gate Zero passes 3 of 6 legs, so the dev gate fails. Per-season the
pattern is uneven: 2022/23 passes 2/6 legs (1X2 and RPS vs
climatology only — naive wins all three metrics that season, 0.9108
vs 1.0113 on 1X2 LL); 2023/24 passes 5/6 (everything except OU2.5 vs
climatology, 0.6912 vs 0.6773); 2024/25 passes 4/6 (1X2 and RPS vs
climatology, 1X2 and OU2.5 vs naive — 1X2 vs naive by 0.0005,
0.9671 vs 0.9676; RPS loses to naive, OU2.5 loses to climatology).
The OU2.5 leg is the persistent failure: Gate Zero loses OU2.5 LL
to climatology in all three dev seasons (2022/23 0.7180 vs 0.6534;
2023/24 0.6912 vs 0.6773; 2024/25 0.7096 vs 0.6880).

SHRINK is numerically identical to Gate Zero pooled and per season
(0.9922 / 0.2120 / 0.7063 in every window). Verified cause: no team
had 1–5 prior in-league matches in any scored season's training
data — every team entering a scored season either had n = 0 prior
matches (pure entrant, already at the league-mean fallback in both
arms) or n ≥ 30, so the n/6 scaling never bit on a fitted rating;
a synthetic test proved the SHRINK scaling itself is active (n=3
gives factor 0.5; 0.8 → 0.4, −0.6 → −0.3). SHRINK's leg (iii) sign
check (SHRINK 1X2 LL ≤ Gate Zero in 3 of 3 dev seasons, by equality)
is recorded but moot: Gate Zero failed its dev gate, so under the
frozen mechanical reading the variant is moot and nothing proceeds
to virgin.

Virgin legs (i)–(iii): NOT APPLICABLE / NOT READ. No arm passed the
dev gate, so virgin 2025/26 was never read, no virgin LL or
calibration numbers exist, and leg (iii) for SHRINK is moot as above.
2026/27 was not touched (confirmatory reserve).

Diagnosis (measured facts, recorded not acted on): the DC score
matrix systematically under-predicts total goals in this league —
mean predicted OU2.5 over-rate 0.5373 vs actual 0.6028 pooled (per
season 0.5022 vs 0.6417 in 2022/23, 0.5585 vs 0.5958 in 2023/24,
0.5512 vs 0.5708 in 2024/25), computed from
`engine/goals/results_dev.csv`. That shortfall is the OU2.5 LL gap:
a constant 0.6238 over-rate (climatology, pooled) beats the model's
per-match total-goals distribution on log-likelihood. The model also
over-predicts home wins slightly — mean predicted home-win
probability 0.4561 vs actual home-win rate 0.4431 pooled (worst in
2022/23: 0.4629 vs 0.4208) — while the fitted home intercept falls
season by season (0.3189 in the 2022/23 fit, 0.2457 in 2023/24,
0.2008 in 2024/25; rho −0.05, 0.0, 0.0). The same failure mode
killed G-SE (OU2.5 shortfall 0.5065 vs 0.5833 there). Hypothesis
(marked as hypothesis, not established): with the goals level
drifting down across seasons (3.21 → 3.34 → 3.13 → 2.99 in the
training windows) the 270-day decay still leaves the fitted
lambdas compressed toward the training mean while the actual
over-rate stays high, so the score matrix is simultaneously too
low-scoring in total and too home-heavy; the naive trailing-10
baseline, which uses each team's actual trailing scoring means as
its lambdas, wins 1X2 LL and RPS outright. No post-hoc repair was
attempted inside this prereg. Nothing ships for G-LU.

Independent verification (by the coordinator, not Codex):
- All headline metrics recomputed from `results_dev.csv` with an
  independent script — exact match to 4 decimals, pooled and
  per-season, all four methods.
- Second-path fit with production `model_v2.py` DC (iterative
  updates, same windows): pooled 0.9889 / 0.2127 / 0.6947 — same
  3/6 legs (loses 1X2 LL and RPS to naive, OU2.5 LL to
  climatology), same FAIL. The verdict does not depend on the
  optimizer.
- Naive baseline recomputed with same-day matches strictly excluded
  (date-grouped prediction): pooled 0.9755 / 0.2073 / 0.7400 vs
  the engine's 0.9756 / 0.2073 / 0.7399 — the same-day ordering
  choice moves no leg by more than 0.0002.
- Code review of the engine: bounded trailing-10 deque
  (maxlen=10), dev loader hard-guards (virgin/reserve rows rejected,
  frozen counts enforced), standard DC tau on all four low-score
  cells, RPS over the first two cumulative terms, SHRINK scaling
  applied to both exponents. One post-Codex cleanup: the
  per-match predictions were removed from `results_dev.json`
  (summary-only, SE precedent); the CSV is the per-match record.
  Re-running the harness after the cleanup reproduces the metrics
  to full precision.
