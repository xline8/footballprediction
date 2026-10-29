# Experiment Register

Record of the keep-or-revert experiment loop. Each experiment states a
hypothesis, is implemented and backtested under leak-free walk-forward
validation, and is then kept (committed) or reverted with the reason
recorded here. Failed experiments stay in the register; they are the
evidence behind what the production system does not do.

## Baseline at register reset (2026-10-26)

Engine: `backtest_picks.py`, walk-forward over 68,763 test matches, at
historical B365 opening odds. Rule: signal = model probability, edge =
`p − 1/odds` > 0.02, flat 1u stake, 1X2.

| Model | Yield | Log loss | Brier | Macro-F1 | Hit rate | Bets |
|---|---|---|---|---|---|---|
| **Dixon-Coles (baseline)** | **−8.85%** | 1.0311 | 0.6161 | 0.3703 | 0.308 | 46,092 |
| T3 feature model | −10.40% | 1.0287 | 0.6171 | 0.3542 | 0.274 | 50,339 |

Objective: positive yield without degrading log loss or Brier. Secondary
objective: lower log loss.

## Correction (2026-10-26): the Shin de-vigging bug

A bug was found in the Shin branch of `_fair_probs`: the bisection ran in
the wrong direction, driving z to about 0.999. Fair probabilities summed
to roughly 0.52 instead of 1.0, implied probabilities were understated,
and computed edges were inflated. The fix reversed the bisection
direction; the corrected probabilities sum to 1.0, validated on 2,000
random odds triples and against the multiplicative method.

Consequences for every Shin-based result up to that point (Phases 3–5):

- The Phase 5 S1 pocket (+3.23% flat, 1,340 bets) **did not survive**.
  With correct Shin de-vigging, the top-5 favourites filter (odds 1.2–1.5,
  edge in [0.20, 0.22)) produces n = 0: edges that large almost never occur
  on heavy favourites. The earlier result was an artefact of the bug.
- The best remaining positive segment, top-5 at odds 2.6–3.5, returned
  +1.88% (n = 512) but was temporally unstable: profit concentrated in
  small samples from 2017, 2020, 2021, and 2025, with 2023–2026 negative.
  Noise, not edge.
- Global meta-model yield after the fix: −3.77% (n = 17,093), against
  Dixon-Coles at −9.01% (n = 71,015). The meta model is clearly the better
  probability model; global yield is still negative, which is what B365
  market efficiency predicts.
- Conclusion: no validated positive-ROI pocket remained after the
  correction. The live filter in `make_picks_live.py` was deliberately
  left producing 0 picks rather than send money after a phantom edge,
  pending a strategy with a genuinely re-validated edge.

## First pool: de-vigging and policy tuning (E1–E5)

| # | Hypothesis | Config | Yield | Log loss | Brier | Verdict |
|---|---|---|---|---|---|---|
| E1 | Shin de-vigging | dc/shin/thr .02 | **−7.11%** | 1.0311 | 0.6161 | Keep (vs −8.85%) |
| E1b | Multiplicative de-vigging | dc/mult | −8.50…−9.07% | 1.0311 | 0.6161 | Revert: worse than Shin |
| E2 | Ensemble blend DC + T3 | blend w .1/.2/.3/.5 + shin | −7.10…−7.17% | 1.020–1.025 | 0.611–0.614 | Revert: no yield gain |
| E3 | Platt recalibration | platt + shin thr .05 | −6.82% | 1.0407 | 0.6221 | Revert: degrades log loss and Brier |
| E4 | Threshold sweep | shin thr .03/.05/.08/.10/.15/.20 | −6.93…−6.67% | 1.0311 | 0.6161 | Keep thr .15 (−6.67%) |
| E4b | Kelly staking | kelly .25 + shin | −8.39% | 1.0311 | 0.6161 | Revert: worse than flat |
| E5 | Draw-specific / T3 at high threshold | t3 + shin thr .05 | −7.09% | 1.0287 | 0.6171 | Revert: worse than DC |

Conclusion, after the pool was exhausted (7 experiments):

- Best achieved: DC + Shin de-vigging + edge threshold 0.15, flat 1u,
  yield −6.67%, log loss 1.0311, Brier 0.6161, hit rate 0.338, 156,871
  bets.
- No configuration reached positive ROI. B365 opening odds are efficient:
  after the overround is removed, the residual edge is negative.
  Recalibration improves hit rate and worsens log loss and Brier.
- Recommendation recorded at the time: do not move any of these to live
  betting. Further progress requires a sharper model (more informative
  features, better calibration before edge extraction), not more
  threshold, staking, or de-vigging tuning, which are exhausted here.

Kept: `backtest_picks.py` refactored into a configurable engine with
`records_cache.jsonl`; the default promoted to the best configuration
(Shin, threshold 0.15).

## Phase 4 — Core model R&D

Target: log loss below 1.020 and Brier below 0.600. Starting baseline on
the 68,763-match walk-forward: DC log loss 1.0311 / Brier 0.6161; T3
feature model 1.0287 / 0.6171.

| # | Hypothesis | Log loss | Brier | Verdict |
|---|---|---|---|---|
| E1 | Meta-logistic on DC + T3 + market-implied probabilities | **1.0019** | **0.5989** | Keep: both targets hit |
| E2 | Two-layer MLP (numpy, 20 features) | 1.0126 | 0.6050 | Revert: worse than meta |
| E3 | Meta + closing odds (CLV features) | 1.0063 | 0.6001 | Revert: worse than meta |
| E4 | Per-league meta models | 1.0070 | 0.6021 | Revert: worse than meta |
| E5 | Meta on logit inputs | **1.0017** | **0.5988** | Keep: both improve |
| E6 | Elo decay (K proportional to 1/√play) | 1.0016 | 0.5988 | Revert: noise (about E5), T3 worsened |

E1 detail: features = DC probabilities (ph, pd, pa) + T3 probabilities +
inverse opening odds; multinomial logistic regression, walk-forward.
Macro-F1 0.3798, accuracy 0.5031. Betting leg at Shin threshold 0.15:
yield −5.77% (vs DC −6.67%), hit rate 36.1%, log loss 1.0045, Brier
0.6004. The meta model also improved the betting leg and was promoted to
the default model.

E5 detail: yield −5.80%, hit rate 36.0%, log loss 1.0043, Brier 0.6003.
Log loss and Brier slightly better than E1, yield flat. The logit-input
meta model was promoted to default.

## Phase 5 — GBDT engine and segmented ROI mining

| # | Hypothesis | Log loss | Brier | Verdict |
|---|---|---|---|---|
| E1 | LightGBM multiclass (20 features, raw + meta) | 1.0032 | 0.5998 | Revert: worse than meta (1.0017 / 0.5988) |
| E1b | LightGBM (meta signals only) | 1.0025 | 0.5993 | Revert: worse than meta |
| S1 | Segment sweep: top-5 heavy favourites (odds 1.2–1.5), edge in [0.20, 0.22) | — | — | Positive ROI found, later invalidated |

S1 detail, as recorded at the time: top-5 leagues (E0/D1/I1/SP1/F1), odds
1.2–1.5, model edge in [0.20, 0.22). Flat 1u returned +3.23% on 1,340 bets
at a 74.8% hit rate; fractional Kelly (0.25) returned +4.75% on 145 bets
at 76.6%. It was positive in every calendar year 2021–2025 and was
implemented in `backtest_picks.py --filter [--kelly]`.

Invalidation (2026-10-26): under the corrected Shin de-vigging described
above, this filter selects n = 0. The +3.23% was an artefact of the bug
and must not be used.

## Phase 7 — Feature science and market dynamics

Baseline: 9-logit meta model, log loss 1.0017, Brier 0.5988; backtest
yield at threshold 0.02 with corrected Shin: −3.77% (n = 17,093). Keep
rule: log loss below 1.0017 **and** yield above −3.77%.

| # | Hypothesis | Features | Log loss | Brier | Yield (best thr) | n | Verdict |
|---|---|---|---|---|---|---|---|
| E1 | Fatigue: rest differential and schedule density over 14/30 days | rest_diff, dens14_diff, dens30_diff | 1.0018 | 0.5989 | −3.57% (thr .02) | 19,110 | Revert: log loss did not fall |
| E2 | xG overperformance (rolling 5: goals for/against vs xG) | opp_h/a, opc_h/a | 1.0018 | 0.5989 | −3.36% (thr .02) | 20,968 | Revert: log loss did not fall |
| E3 | Motivation: points per match and late-season flags | ppm_h/a, ppm_diff, late | 1.0017 (1.001656 → 1.001704) | 0.5988 | −3.12% (thr .02); best −1.45% (thr .05) | 2,875 | Revert: log loss did not fall |
| E4 | CLV proxy from odds movement | — | — | — | — | — | Not testable: the dataset holds a single odds snapshot per match |

Findings:

- All three testable hypotheses failed the log-loss gate. The meta model
  already sits near the market's information ceiling (log loss about
  1.0017); context features did not improve calibration.
- Yield nevertheless improved in all three: −3.57%, −3.36%, −3.12% at
  threshold 0.02, each better than the −3.77% baseline, and E3 reached
  −1.45% at threshold 0.05 (n = 2,875), the most promising direction.
  None was kept: the log-loss gate is strict, and E3's best threshold was
  selected post hoc, which risks fitting noise.
- E4 could not be executed. With no second odds snapshot, odds movement
  (CLV) cannot be computed. The data gap had to be closed first.
- Conclusion: no feature passed the keep protocol. Yield stayed negative
  and no live strategy was activated.

## Phase 8 — Dual-gate evaluation and motivation features

Baseline at pre-fixed threshold 0.05 (Shin, flat): yield −5.65%
(n = 2,158). Gate: log loss at most 1.00170 **and** yield above −3.77%
with n at least 2,000. No threshold sweep.

| # | Hypothesis | Features | Log loss | Brier | Yield (thr .05) | n | Verdict |
|---|---|---|---|---|---|---|---|
| 8.1 | Desperation index and desperation × nothing-to-play-for interaction | despo_h/a, nothing_h/a, inter_h/a, rel, eur | 1.0021 | 0.5991 | −3.27% | 3,834 | Revert: log loss degraded |
| 8.2 | Goal-difference tie-break urgency | u_h/a, gd_h/a, rel | 1.0020 | 0.5990 | −5.23% | 3,127 | Revert: log loss degraded, yield below bar |
| 8.3 | Dixon-Coles × motivation | dmot_main/h/a, mot_diff | 1.0018 | 0.5989 | −4.74% | 2,588 | Revert: log loss degraded, yield below bar |
| 8.4 | Rest disadvantage × motivation | rest_diff, despo, stack_h/a, mot_diff | 1.0021 | 0.5990 | −3.52% | 3,067 | Revert: log loss degraded |

Findings and the recommendation recorded at the time:

- All four failed the log-loss gate (1.0018–1.0021 against a 1.00170 cap).
  Motivation and context features add variance to the average probability
  estimate, which worsens log loss, while improving bet selection: yield
  at threshold 0.05 rose from −5.65% to between −3.27% and −3.52% in 8.1
  and 8.4.
- The pattern is consistent with Phase 7. The meta model sits at the
  market's information ceiling; context features cannot lower global log
  loss but do move betting decisions toward more profitable subsets. A
  strict log-loss gate makes model features almost impossible to admit.
- Recommended next path: apply motivation as a post-model overlay on the
  betting decision and stake, leaving model probabilities (and therefore
  log loss) unchanged, so the gate passes trivially while the yield gain
  is harvested. That is a policy change rather than a feature change, and
  it was taken up in Phase 9.
- No live strategy was activated. `run_daily_shadow.py` was not run,
  because nothing was kept.

## Phase 9 — Decoupled betting policy and contextual overlay

Architecture: the probability engine is locked (meta model, log loss
1.0017 unchanged); Shin edge is computed on its output; a policy overlay
then filters or stakes bets. Evaluation: yield above −1.50%, n at least
1,000, and positive yield in at least 3 of 2021–2025. Reference point:
threshold 0.05 flat baseline of −5.65% (n = 2,158).

Framework: `policy_overlay.py` (candidates, desperation index, composite
= 0.6·desperation + 0.4·fatigue_norm).

| Policy | Rule | Best setting | N | Yield | Stable (≥ 3/5 years) | Verdict |
|---|---|---|---|---|---|---|
| 9.1 | Filter desperation > θ | θ = 0.3 | 169 | +12.7% | 1/5 | Revert: N and stability |
| 9.2 | Filter rest gap ≥ 3 | gap = 3 | 44 | +1.8% | 0/5 | Revert: N and stability |
| 9.3 | Filter composite ≥ θ | θ = 0.3 | 176 | +11.8% | 1/5 | Revert: N and stability |
| 9.4 | Stake = 0.25 · composite | θ = 0 | **553** | **+6.7%** | **3/5** | Revert: N < 1,000 |
| 9.4 floor | Stake = 0.25 · (f + (1−f)·c) | f = 0.3 | 2,158 | −4.4% | 2/5 | Revert: yield and stability |

Findings:

- Policy 9.4 in its pure form (dynamic contextual Kelly staking, no floor)
  was the only configuration with both positive yield (+6.7%) and 3/5
  temporal stability. It failed on sample size: N = 553 against a 1,000
  minimum.
- Adding a stake floor to restore N = 2,158 removed the effect entirely
  (yield back to −4.4%, against a −5.65% baseline at best). The gain in
  9.4 comes from zero-staking low-context bets, not from staking
  everything more cleverly.
- Context overlays concentrate betting into small subsets (roughly
  200–600 bets) with positive but noisy ROI. Nothing passed the combined
  size and stability gates.
- Recommendation recorded at the time: 9.4 is the strongest lead in the
  register. Passing the size gate needs either more data (a live ledger),
  a looser edge threshold, or a broader desperation definition, with the
  dilution risk that carries.
- No policy was kept. `make_picks_live.py` was unchanged and the shadow
  flow stayed at 0 picks.

## Phase 10 — Significance testing and high-context expansion

Step 1, bootstrap significance of Policy 9.4 (`verify_significance.py`,
10,000 resamples): n = 553 bets; weighted ROI +6.72%; bootstrap mean
+6.76%; 95% CI [−9.48%, +23.44%]; **p = 0.2164** against H0 of ROI ≤ 0.
Not significant. The size gate could not be relaxed on statistical
grounds: the interval is wide and covers zero comfortably, so the result
is sensitive to a few large bets.

Step 2, expanding the high-context pool (`policy_expand.py`):

- **Continental proximity was not available.** The `EC` division in the
  dataset is the English National League (fifth tier), not the Champions
  League, Europa League, or Conference League. No European club fixtures
  exist in the data, so the continental feature is identically zero.
- **Rivalry (head-to-head proxy):** adding weight w4 raised N to 747 and
  destroyed the yield (+2.8% → +0.3%). The head-to-head proxy is not
  predictive; it only dilutes.
- **Desperation expansion (title and European places):** N rose to about
  562 (from 553) with yield +5.18% and 3/5 stability, similar to the
  original 9.4.
- No configuration reached N ≥ 800 with yield above +4.5% and stability
  of at least 3/5. The best compromises were the base weighting (0.6, 0.4)
  at N = 562 and +5.18% (too small), and the w4 variant at N = 747 with
  yield near zero (failed).

Step 3, shadow tracking: blocked by both steps above. Nothing was kept,
`make_picks_live.py` was unchanged, and live shadow stayed at 0 picks.
Conclusion recorded at the time: 9.4 remains the best lead, but N = 553
is too small and the effect is not significant. Proving an edge here
needs more data (live ledger accumulation) or a context definition that
is predictive rather than a frequency proxy.

## Phase 11 — Exogenous data enrichment pipeline

Decision: the historical dataset was saturated by the meta model (log
loss 1.0017), so the work pivoted to data engineering. The enrichment
layer was built without modifying `all_matches_clean.csv`.

Architecture (`data_enrichment/`):

- `utils.py` — team-name normalisation (top-team aliases), fuzzy matching
  (Levenshtein), safe float parsing, logging.
- `fetch_xg.py` — Understat fetcher (xG, xPTS) with timeouts and a
  fallback to the local `xg_matches.csv` cache.
- `fetch_closing_odds.py` — extraction of Pinnacle (PSH/PSD/PSA) and
  Max/Avg prices from the historical CSVs.
- `synthesize_european.py` — a congested-schedule heuristic:
  `midweek_cup_flag` when a team has another match within ±3 days.
- `enrich_pipeline.py` — left join into `all_matches_enriched.csv`
  (`--full`, or a dry-run subset).

Dry run (EPL 2023/24, 380 matches):

| Feature | Joined | Note |
|---|---|---|
| Pinnacle / Max / Avg | 380/380 (100%) | PS columns already present in the source |
| xG | 240/380 (63%) | from the local cache |
| Midweek flag | 120/380 (32%) | consistent with the window calibration |
| rolling_xg_diff | 380/380 (100%) | leak-free, chronological |

Full run (70,425 matches): Pinnacle/Max/Avg 70,425/70,425; xG 9,074
(12.9%); midweek flags 21,342 (30.3%); rolling_xg_diff 70,066 (99.5%).
The `all_matches_clean.csv` source was left untouched.

Blockers recorded:

1. Understat could not be pulled reliably (page and API structure changes,
   CAPTCHA risk), so the pipeline uses the local cache, with mock data
   only as a last-resort fallback.
2. Genuine European fixtures are unavailable: the `EC` division is the
   English National League, not the UCL, UEL, or UECL. The
   congested-schedule heuristic stands in as a proxy.
3. Pure odds movement is unavailable (one odds snapshot per match), so
   Pinnacle/Max/Avg prices were extracted as a cross-book CLV proxy.

## Phase 12 — Sharp book consensus and enriched alpha

The enriched data (`all_matches_enriched.csv`: Pinnacle prices, midweek
flags, rolling_xg_diff) was integrated into the prediction engine. Join
coverage: 51,420 of 68,763 records carry Pinnacle prices (83.1%); the rest
were imputed with a neutral B365 fallback (deviation 1.0).

### Pathway A — ML injection into the meta model (kept)

Meta features expanded from 9 to 17: deviation of B365 from Pinnacle for
home/draw/away, Pinnacle fair probabilities (Shin de-vigged), and midweek
flags for both teams. Monthly walk-forward, multinomial logistic.

| Metric | Meta baseline (9 features) | + sharp (17 features) |
|---|---|---|
| Log loss | 1.0017 | **1.0013** |
| Brier | 0.5988 | **0.5986** |
| Macro-F1 | 0.3743 | **0.3768** |
| Accuracy | 0.5028 | **0.5035** |

The log-loss gate (below 1.00170) passed at 1.001257. Sharp-book
information lowered log loss through the previous market ceiling, so the
17-feature model was promoted to the new meta baseline: `experiment_meta`
moved to 17 features, `records_cache.jsonl` was recomputed (66,379 of
68,763 records carry meta probabilities), and the `ps`, `mw_h`, and
`rollxg` columns were persisted. One bug was found and fixed on the way:
an early version of `augment_records` loaded records without the
enrichment join, which left the new columns all-NaN and silently trained
a 9-feature model.

### Pathway B — Sharp/soft policy overlay (reverted)

With the meta model locked, bets with a Shin edge were filtered on the
Pinnacle deviation of the bet side, with and without midweek flags. Gate:
N ≥ 800 and bootstrap p < 0.05 against H0 of ROI ≤ 0.

| Deviation > | Midweek | N | Yield | Positive years (of 2021–2025) |
|---|---|---|---|---|
| 1.00 | no | 418 | −4.57% | 2/5 |
| 1.00 | yes | 89 | −22.47% | 0/5 |
| 1.02 | no | 201 | −10.97% | 2/5 |
| 1.02 | yes | 43 | −35.19% | 0/5 |
| 1.05 | no | 65 | −2.63% | 0/5 |
| 1.05 | yes | 15 | −25.67% | 0/5 |
| 1.08 | no | 18 | +32.94% | 0/5 |
| 1.08 | yes | 5 | −100% | 0/5 |

No configuration reached N ≥ 800; the best headline (+32.9% on n = 18) is
noise. Filtering on Pinnacle deviation without midweek selects small,
losing subsets, and adding midweek shrinks N drastically. The overlay was
reverted, no new overlay was adopted, and `make_picks_live.py` stayed at
0 picks.

Phase conclusion: the sharper meta baseline (log loss 1.0013, Brier
0.5986) gives a better foundation for future edge extraction, but no new
betting edge was validated. The new baseline's global yield awaited
confirmation from the default backtest.

## Phase 13 — Derivative markets and matrix pricing

Architecture: `matrix_pricer.py` builds the bivariate Poisson Dixon-Coles
scoreline matrix (λ_home, λ_away, ρ from `records_cache`), then
meta-calibrates it: the Home, Draw, and Away regions are scaled
proportionally so the summed 1X2 marginals match the meta model (log loss
1.0012) exactly. Over 2.5, Under, and BTTS probabilities are derived from
that matrix. Self-checks: 1X2 marginals equal the meta model, over + under
= 1, BTTS pair = 1.

Derivative odds availability:

- **Over/Under 2.5:** available (B365 on 54,766 matches, Pinnacle on
  48,309), so a backtest was possible.
- **BTTS:** no historical odds column exists. Recorded as a data blocker;
  the pricing logic remains in `matrix_pricer` for live shadow use.

Backtest, Over/Under 2.5 (B365, two-way Shin de-vig, flat 1u, both sides):

| Threshold | N | Yield | Hit rate | Bootstrap p |
|---|---|---|---|---|
| 0.02 | 35,412 | −5.66% | 50.2% | 1.0000 |
| 0.05 | 22,193 | −5.98% | 50.0% | 1.0000 |
| 0.08 | 12,479 | −6.19% | 49.8% | 1.0000 |

No edge: the hit rate sits at the Over/Under base rate (about 50%), so
the model adds no signal over the market, and the yield is approximately
the B365 margin (−6%). The betting rule was reverted. `matrix_pricer`
was kept as core infrastructure. Nothing was activated live; shadow
stayed at 0 picks.

## Phase 15 — Corner model integration and alpha validation

Evaluation of `model_corners_v3.py` (Poisson corner model, mean from
rolling shots, gamma and r fitted on the 2019/20–2020/21 validation
window). Walk-forward test 2021/22–2025/26, n = 8,906.

Step 1, predictive calibration (no odds involved):

| Metric | League base rate | Shot-based model |
|---|---|---|
| Log loss (total corners NLL) | 2.6169 | **2.6087** |
| Brier, Over 9.5 | 0.2483 | **0.2474** |
| MAE, total corners | 2.669 | **2.656** |
| RMSE by league (E0/D1/I1/SP1/F1) | 3.39/3.33/3.38/3.30/3.32 | **3.38/3.32/3.38/3.28/3.32** |

The shot-based model beat the league base rate on every metric and in
every league, consistently but by small margins. Calibration buckets for
P(total > 9.5): actual/predicted 0.46/0.46, 0.55/0.54, 0.60/0.62, which is
adequately calibrated. The model carries real but small signal (log loss
2.61 is far from ideal); its probabilities remain useful for ranking and
risk purposes.

Step 2, ROI backtest: **not executable**. Historical corner odds exist in
neither `all_matches_enriched.csv` nor the clean dataset (blocker T10).
Wiring into `backtest_picks.py`, de-vigging, and a threshold sweep were
deferred until an odds source exists. Shadow activation steps were
therefore not applicable.

Status: `model_corners_v3.py` kept as infrastructure. Blocker T10
recorded. No validated corner alpha.
