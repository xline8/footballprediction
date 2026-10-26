# Football 1X2 & Derivative Market Prediction

A quantitative research engine that predicts pre-match football outcomes for the
top five European leagues (EPL, La Liga, Bundesliga, Serie A, Ligue 1) and prices
derivative markets (Over/Under 2.5, BTTS) from a calibrated scoreline matrix.

The engine is built for research, not for chasing returns. It tests whether the
B365 and Pinnacle markets hide exploitable value; the answer so far is no, and
the code is structured to keep that conclusion honest.

## Key achievements

- **Elite calibration.** The meta model reaches a walk-forward log loss of
  **1.0013** and Brier 0.5986, near the information ceiling implied by the
  market. A Dixon-Coles bivariate Poisson model, a feature model, and market
  odds are stacked into a multinomial logistic meta-model.
- **Strict discipline.** Every experiment runs leak-free walk-forward validation,
  proper scoring metrics (log loss, Brier, per-class), and a dual gate: a log
  loss safety check plus a fixed-threshold yield check with a bootstrap
  significance test. A de-vigging bug that inflated a false +3.23% strategy was
  found and fixed; a small-sample +6.7% policy was kept out because its bootstrap
  p-value was 0.216. No live betting strategy is active without a significant,
  stable backtest.
- **Market efficiency finding.** The 1X2 and Over/Under 2.5 derivative markets
  look efficient: soft books copy sharp lines, and after removing the margin no
  tested rule produces a statistically significant positive ROI.

## Core architecture

- **Dixon-Coles engine** (`model_v2.py`): a bivariate Poisson model with a
  low-score dependency correction and decayed team ratings.
- **Meta model** (`experiment_meta.py`, `backtest_picks.py`): stacks logits of
  the DC model, the feature model, and market-implied probabilities with a
  walk-forward multinomial logistic regression. It also consumes enriched sharp
  signals (Pinnacle deviation, Pinnacle shin-fair probabilities, midweek flags).
- **Data enrichment pipeline** (`data_enrichment/`): joins Pinnacle odds,
  midweek/cup fatigue flags, and rolling xG differentials into
  `all_matches_enriched.csv`, without touching the clean source data.
- **Matrix pricing** (`matrix_pricer.py`): builds the bivariate Poisson
  scoreline matrix and meta-calibrates it so the summed 1X2 marginals match the
  meta model exactly. Over/Under and BTTS probabilities are derived from that
  calibrated matrix.
- **Decoupled policy engine**: betting decisions are filtered *after* the model
  (edge thresholds, overlays, staking) so calibration stays intact. Candidate
  policies must clear the dual gate before they can go live.

## Live shadow tracker

`run_daily_shadow.py` runs the production monitor as a daily cron-safe chain:
generate predictions → filter and record picks → resolve and grade. Each step is
isolated with try/except, so a failure in one stage never crashes the pipeline.
It is deliberately strict: with no validated edge, it emits **0 picks** and
records nothing to the ledger. When a strategy clears the gates, this is the
component that goes to a real ledger without risking live money.

## Reference

[QUANT_RESEARCH_REPORT.md](QUANT_RESEARCH_REPORT.md) contains the full scientific
summary: the modeling milestones, the de-vigging and small-sample lessons, and
the market-efficiency evidence.

## Getting started

Run the end-to-end pipeline:

```
python setup_cache.py
python pipeline_orchestrator.py --run-all
```

Individual pieces also run standalone: `python model_v2.py final` fits and prints
the scoring report, `python backtest_value.py` reruns the value-bet backtest, and
`python refresh_fixtures.py` pulls fresh fixtures.

Dependencies: `numpy` (see `requirements.txt`). The optional API server
(`api_server.py`) and scrapers use `fastapi`, `uvicorn`, `pydantic`, `requests`,
and `httpx`. `test_core.py` holds the smoke tests (`python test_core.py`).
