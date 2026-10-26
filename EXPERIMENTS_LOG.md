# EXPERIMENTS_LOG

Single source of truth for the keep-or-revert loop.
Each experiment: hypothesize → implement → backtest → keep (commit) or revert (log failure).

## Current best baseline (RESET 2026-10-26)

Engine: `backtest_picks.py` (walk-forward, 68,763 test matches, historical B365 opening odds).
Rule: signal = pure model prob, edge = `p − 1/odds` > 0.02, flat 1u stake, 1X2.

| model | yield | log loss | brier | macro-F1 | hit rate | n bets |
|---|---|---|---|---|---|---|
| **DC (baseline)** | **−8.85%** | 1.0311 | 0.6161 | 0.3703 | 0.308 | 46,092 |
| T3 feature | −10.40% | 1.0287 | 0.6171 | 0.3542 | 0.274 | 50,339 |

Goal: yield > 0 while not ruining log loss / Brier. Secondary: lower log loss.

## Progress

| # | hypothesis | config | yield | log loss | brier | verdict |
|---|---|---|---|---|---|---|
| E1 | De-vigging (Shin) | dc/shin/thr .02 | **−7.11%** | 1.0311 | 0.6161 | ✅ KEEP (vs −8.85) |
| E1b | De-vigging (mult) | dc/mult | −8.50…−9.07% | 1.0311 | 0.6161 | ❌ worse than shin |
| E2 | Ensemble blend DC+T3 | blend w .1/.2/.3/.5 + shin | −7.10…−7.17% | 1.020–1.025 | 0.611–0.614 | ❌ no yield gain |
| E3 | Platt recalibration | platt + shin thr .05 | −6.82% | 1.0407 ↑ | 0.6221 ↑ | ❌ ruins logloss/brier |
| E4 | Threshold sweep | shin thr .03/.05/.08/.10/.15/.20 | −6.93…−6.67% | 1.0311 | 0.6161 | ✅ KEEP thr .15 (−6.67%) |
| E4b | Kelly staking | kelly .25 + shin | −8.39% | 1.0311 | 0.6161 | ❌ worse than flat |
| E5 | Draw-specific / T3-at-high-thr | t3 + shin thr .05 | −7.09% | 1.0287 | 0.6171 | ❌ worse than dc |

### Conclusion (after pool exhausted, 7 experiments)

- Best achieved: **DC + Shin de-vigging + edge thr 0.15, flat 1u → yield −6.67%**, log loss 1.0311, Brier 0.6161, hit rate 0.338, 156,871 bets.
- **No configuration reached positive ROI.** The B365 opening odds are efficient; after removing the overround the residual edge is negative. Calibration improves hit-rate but worsens log loss/Brier.
- Recommendation: do **not** switch live bets to any of these. If pursued further, the lever is a genuinely sharper model (more informative features / better calibration *before* edge extraction), not threshold/staking/de-vigging tuning, which are exhausted here.

### Kept (committed)
- `backtest_picks.py` refactor into a configurable engine with `records_cache.jsonl`; default promoted to best config (thin, thr 0.15).

---

## Phase 4 — Core model R&D (target: log loss < 1.020, Brier < 0.600)

Starting baseline (68,763-match walk-forward): DC log loss 1.0311 / Brier 0.6161; T3 feature log loss 1.0287 / Brier 0.6171.

| # | hypothesis | log loss | brier | verdict |
|---|---|---|---|---|
| E1 | Meta-logistic: DC+X3 + market-implied probs | **1.0019** | **0.5989** | ✅ KEEP (both targets hit) |
| E2 | MLP 2-lapis (numpy, 20 fitur) | 1.0126 | 0.6050 | ❌ worse than meta (ll/brier) |
| E3 | Meta + close odds (CLV) | 1.0063 | 0.6001 | ❌ worse than meta (ll/brier) |
| E4 | Per-league (div) meta | 1.0070 | 0.6021 | ❌ worse than meta (ll/brier) |
| E5 | Meta dgn input logit | **1.0017** | **0.5988** | ✅ KEEP (both improve) |

E1 detail: features = p(ph,pd,pa) + p_t3 + (1/o_h,1/o_d,1/o_a) opening odds; multinomial logistic, walk-forward. macro-F1 0.3798, accuracy 0.5031.
E1 ROI (backtest, shin thr 0.15): **yield −5.77%** (vs DC −6.67%), hit rate 36.1%, log loss 1.0045, Brier 0.6004 → also improves the betting leg. Meta promoted to default model.
E5 ROI (logit meta, shin thr 0.15): **yield −5.80%**, hit rate 36.0%, log loss 1.0043, Brier 0.6003 → LL/Brier slightly better, yield flat. Meta (logit) promoted to default.
