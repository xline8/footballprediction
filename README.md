# Football prediction pipeline

Predicts match outcomes for the top five European leagues (EPL, La Liga, Bundesliga, Serie A, Ligue 1) and turns the probabilities into betting picks when the market price disagrees with the model.

The engine is a **Dixon-Coles** model: a bivariate Poisson for home and away goals, with a `tau` correction for the low-score corners (0-0, 1-0, …) where the two scores stop being independent, plus a home-advantage term. Ratings decay with a half-life (default 270 days) over a rolling window of up to 4000 matches per division. A second model predicts corner markets from rolling shot statistics.

The models are validated the way they are used: **walk-forward**. Training always stops before the match being predicted, so no result from the future leaks into a rating or feature. Scoring uses proper rules: Brier, overall and per-class log loss, and a calibration table. On the last full run the DC model scored a Brier of 0.592 and a log loss of 0.993 across 8,908 predictions; draws are the weakest class, as they usually are (per-class log loss about 1.38).

Picks come from blending model probabilities against market odds and taking bets where the edge is positive. A backtest cuts the strategy by market and odds bucket, and the ledger (`ledger/picks.jsonl`) records every pick with the odds that were actually available when it was made. `grade_picks.py` settles them against real results.

## What it does

| Stage | Result | Code |
|---|---|---|
| Fetch and clean data | `all_matches_clean.csv` plus caches | `prepare.py`, `clean.py`, `download.py` |
| Fit/update Dixon-Coles per division | persisted model states in `.cache/models/` | `model_v2.py`, `model_state.py` |
| Predict corner markets | `predictions_corners_upcoming.csv` | `model_corners_v3.py` |
| Blend with market odds | `predictions_upcoming.csv` | `predict_upcoming_refactored.py` |
| Value-bet filter | `best_picks.csv`; picks appended to `ledger/picks.jsonl` | `make_picks.py`, `best_picks.py` |
| Grade settled picks | `ledger/graded.csv` | `grade_picks.py` |

Run everything with:

```
python setup_cache.py
python pipeline_orchestrator.py --run-all
```

Individual pieces also run standalone: `python model_v2.py final` fits and prints the scoring report, `python backtest_value.py` reruns the value-bet backtest, and `python refresh_fixtures.py` pulls fresh fixtures.

## Where the data comes from

The project downloads or scrapes four sources; none is bundled or cached permanently beyond `raw/`, `xg_raw/`, and `ta/`.

- **football-data.co.uk** — historical results and closing odds for all five leagues (`raw/{div}_2627.csv`, `all_matches.csv`). Downloaded by `download.py`.
- **Understat** — seasonal fixtures and expected-goals (xG) data (`xg_raw/*.json`), pulled through Understat's `getLeagueData` endpoint by `refresh_fixtures.py`.
- **TipsterArea** — live pre-match odds from several bookmakers, scraped by `ta_scrape.py` and turned into TA-model markets by `ta_model.py`.
- **NowGoal** — odds snapshots captured by `nowgoal_extract.js` and ingested by `snapshot_to_db.py` into `raw/odds_timeseries.csv`.

Scraping respects each source's structure; a failed fetch falls back to the last known snapshot instead of failing the whole pipeline.

## Repo layout

```
pipeline_orchestrator.py   end-to-end runner
football_etl.py            shared ETL and math primitives (pois, tau, norm, blend)
model_v2.py                Dixon-Coles
model_corners_v3.py        corner model
model_state.py             per-division model persistence
features.py                leak-free feature builder (Elo, rolling xG, rest days, H2H)
validation.py              proper-scoring metrics
paths.py                   central path constants
raw/                       football-data downloads
xg_raw/                    Understat fixtures / xG
ta/                        TipsterArea aggregated data
ledger/                    picks (picks.jsonl) and grading (graded.csv)
test_core.py               smoke tests
```

## Tests

```
python test_core.py
```
